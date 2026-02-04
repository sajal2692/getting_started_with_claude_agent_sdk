#!/usr/bin/env python3
"""
Risk Analysis Helper Script

Performs comprehensive risk analysis on a stock including volatility, beta, VaR, and risk-adjusted metrics.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
    from scipy import stats
except ImportError:
    print("ERROR: Required packages not found. Install yfinance, pandas, numpy, and scipy.", file=sys.stderr)
    sys.exit(1)


def fetch_data(ticker: str, benchmark: str, period: str) -> tuple:
    """Fetch stock and benchmark data"""
    try:
        print(f"Fetching {ticker} and {benchmark} data...", file=sys.stderr)

        stock = yf.Ticker(ticker)
        stock_hist = stock.history(period=period)

        bench = yf.Ticker(benchmark)
        bench_hist = bench.history(period=period)

        if stock_hist.empty:
            raise ValueError(f"No data found for {ticker}")
        if bench_hist.empty:
            raise ValueError(f"No data found for benchmark {benchmark}")

        return stock_hist['Close'], bench_hist['Close']

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def calculate_volatility_metrics(returns: pd.Series) -> dict:
    """Calculate various volatility measures"""
    # Annualized volatility
    annualized_vol = float(returns.std() * np.sqrt(252) * 100)

    # Downside deviation (only negative returns)
    downside_returns = returns[returns < 0]
    downside_dev = float(downside_returns.std() * np.sqrt(252) * 100) if len(downside_returns) > 0 else 0.0

    # Categorize volatility
    if annualized_vol < 15:
        category = "Low"
    elif annualized_vol < 30:
        category = "Moderate"
    else:
        category = "High"

    return {
        "annualized_volatility_pct": round(annualized_vol, 2),
        "downside_deviation_pct": round(downside_dev, 2),
        "volatility_category": category
    }


def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> dict:
    """Calculate beta and correlation with market"""
    # Align the data
    df = pd.DataFrame({'stock': stock_returns, 'market': market_returns}).dropna()

    if len(df) < 2:
        return {
            "beta": 0.0,
            "correlation_with_market": 0.0,
            "beta_interpretation": "Insufficient data"
        }

    # Calculate beta using covariance
    covariance = df['stock'].cov(df['market'])
    market_variance = df['market'].var()
    beta = float(covariance / market_variance) if market_variance > 0 else 0.0

    # Correlation
    correlation = float(df['stock'].corr(df['market']))

    # Interpretation
    if beta < 0.8:
        interpretation = f"{abs(1 - beta) * 100:.0f}% less volatile than market (defensive)"
    elif beta <= 1.2:
        interpretation = "Similar volatility to market"
    else:
        interpretation = f"{(beta - 1) * 100:.0f}% more volatile than market (aggressive)"

    return {
        "beta": round(beta, 2),
        "correlation_with_market": round(correlation, 2),
        "beta_interpretation": interpretation
    }


def calculate_var(returns: pd.Series, confidence: float = 0.95) -> dict:
    """Calculate Value at Risk"""
    # Daily VaR
    daily_var = float(np.percentile(returns, (1 - confidence) * 100) * 100)

    # Monthly VaR (approximate)
    monthly_var = daily_var * np.sqrt(21)  # Approx 21 trading days per month

    interpretation = f"{confidence * 100:.0f}% confidence that daily loss won't exceed {abs(daily_var):.2f}%"

    return {
        "confidence_level": confidence,
        "daily_var_pct": round(daily_var, 2),
        "monthly_var_pct": round(monthly_var, 2),
        "interpretation": interpretation
    }


def calculate_risk_adjusted_metrics(returns: pd.Series, downside_returns: pd.Series) -> dict:
    """Calculate Sharpe ratio, Sortino ratio, and max drawdown"""
    # Sharpe ratio (simplified, assuming 0% risk-free rate)
    mean_return = returns.mean() * 252  # Annualized
    volatility = returns.std() * np.sqrt(252)
    sharpe = float(mean_return / volatility) if volatility > 0 else 0.0

    # Sortino ratio (uses downside deviation)
    downside_std = downside_returns.std() * np.sqrt(252)
    sortino = float(mean_return / downside_std) if downside_std > 0 else 0.0

    # Maximum drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_dd = float(drawdown.min() * 100)
    max_dd_date = drawdown.idxmin().strftime("%Y-%m-%d") if not drawdown.empty else None

    return {
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "max_drawdown_pct": round(max_dd, 2),
        "max_drawdown_date": max_dd_date
    }


def assess_overall_risk(metrics: dict) -> dict:
    """Provide overall risk assessment"""
    vol = metrics['volatility_metrics']['annualized_volatility_pct']
    beta = metrics['market_risk']['beta']
    max_dd = abs(metrics['risk_adjusted_metrics']['max_drawdown_pct'])

    # Determine overall risk level
    high_risk_factors = []

    if vol > 30:
        high_risk_factors.append(f"High volatility ({vol:.2f}%)")
    if beta > 1.2:
        high_risk_factors.append(f"Beta significantly above 1 ({beta:.2f})")
    if max_dd > 30:
        high_risk_factors.append(f"Large maximum drawdown ({max_dd:.2f}%)")

    if len(high_risk_factors) >= 2:
        overall_risk = "High"
        suitable_for = "Aggressive investors with high risk tolerance"
    elif vol > 30 or beta > 1.2 or max_dd > 30:
        overall_risk = "Moderate-High"
        suitable_for = "Growth-oriented investors comfortable with volatility"
    elif vol < 15 and beta < 0.8 and max_dd < 15:
        overall_risk = "Low"
        suitable_for = "Conservative investors seeking stability"
    else:
        overall_risk = "Moderate"
        suitable_for = "Balanced investors with moderate risk tolerance"

    if not high_risk_factors:
        if vol < 20:
            high_risk_factors.append(f"Moderate volatility ({vol:.2f}%)")
        if 0.8 <= beta <= 1.2:
            high_risk_factors.append(f"Market-like beta ({beta:.2f})")

    return {
        "overall_risk": overall_risk,
        "risk_factors": high_risk_factors,
        "suitable_for": suitable_for
    }


def analyze_risk(ticker: str, benchmark: str = "^GSPC", period: str = "1y", confidence: float = 0.95) -> dict:
    """Perform comprehensive risk analysis"""
    # Fetch data
    stock_prices, bench_prices = fetch_data(ticker, benchmark, period)

    # Align data
    df = pd.DataFrame({'stock': stock_prices, 'bench': bench_prices}).dropna()

    if df.empty:
        raise ValueError("No overlapping data found")

    print(f"Analyzing {len(df)} data points...", file=sys.stderr)

    # Calculate returns
    stock_returns = df['stock'].pct_change().dropna()
    market_returns = df['bench'].pct_change().dropna()

    # Price data
    current_price = float(df['stock'].iloc[-1])
    period_return = ((df['stock'].iloc[-1] - df['stock'].iloc[0]) / df['stock'].iloc[0]) * 100

    price_data = {
        "current_price": round(current_price, 2),
        "period_return_pct": round(period_return, 2),
        "price_range": {
            "min": round(float(df['stock'].min()), 2),
            "max": round(float(df['stock'].max()), 2)
        }
    }

    # Calculate all metrics
    volatility_metrics = calculate_volatility_metrics(stock_returns)
    market_risk = calculate_beta(stock_returns, market_returns)
    var_metrics = calculate_var(stock_returns, confidence)

    # Downside returns for Sortino
    downside_returns = stock_returns[stock_returns < 0]
    risk_adjusted = calculate_risk_adjusted_metrics(stock_returns, downside_returns)

    # Compile results
    result = {
        "ticker": ticker.upper(),
        "benchmark": benchmark,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "period": period,
        "price_data": price_data,
        "volatility_metrics": volatility_metrics,
        "market_risk": market_risk,
        "value_at_risk": var_metrics,
        "risk_adjusted_metrics": risk_adjusted
    }

    # Overall assessment
    result["risk_assessment"] = assess_overall_risk(result)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Perform comprehensive risk analysis on a stock"
    )
    parser.add_argument(
        "--ticker",
        required=True,
        help="Stock ticker symbol (e.g., TSLA, AAPL)"
    )
    parser.add_argument(
        "--benchmark",
        default="^GSPC",
        help="Benchmark ticker for beta calculation (default: ^GSPC)"
    )
    parser.add_argument(
        "--period",
        default="1y",
        choices=["3mo", "6mo", "1y", "2y", "5y"],
        help="Time period for analysis (default: 1y)"
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.95,
        choices=[0.90, 0.95, 0.99],
        help="Confidence level for VaR (default: 0.95)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (e.g., tmp/risk_analysis.json)"
    )

    args = parser.parse_args()

    # Perform analysis
    try:
        results = analyze_risk(args.ticker, args.benchmark, args.period, args.confidence)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Risk analysis complete!", file=sys.stderr)
    print(f"Results saved to {output_path}", file=sys.stderr)

    # Print summary
    print(f"\n{'='*60}")
    print(f"RISK ANALYSIS: {results['ticker']}")
    print(f"{'='*60}")
    print(f"\nOverall Risk: {results['risk_assessment']['overall_risk']}")
    print(f"Volatility: {results['volatility_metrics']['annualized_volatility_pct']:.2f}%")
    print(f"Beta: {results['market_risk']['beta']:.2f}")
    print(f"Max Drawdown: {results['risk_adjusted_metrics']['max_drawdown_pct']:.2f}%")
    print(f"Sharpe Ratio: {results['risk_adjusted_metrics']['sharpe_ratio']:.2f}")
    print(f"\nSuitable for: {results['risk_assessment']['suitable_for']}")


if __name__ == "__main__":
    main()
