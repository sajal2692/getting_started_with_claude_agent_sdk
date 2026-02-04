#!/usr/bin/env python3
"""
Comparative Stock Analysis Helper Script

Compares performance of multiple stocks over the same time period.
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
except ImportError:
    print("ERROR: Required packages not found. Make sure yfinance, pandas, and numpy are installed.", file=sys.stderr)
    sys.exit(1)


def fetch_stock_data(ticker: str, period: str) -> pd.DataFrame:
    """Fetch historical data for a single stock"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            raise ValueError(f"No data found for {ticker}")

        return hist['Close']
    except Exception as e:
        print(f"ERROR fetching {ticker}: {e}", file=sys.stderr)
        raise


def calculate_metrics(prices: pd.Series) -> dict:
    """Calculate performance metrics for a stock"""
    # Basic price metrics
    start_price = float(prices.iloc[0])
    end_price = float(prices.iloc[-1])
    total_return = ((end_price - start_price) / start_price) * 100

    # Annualized return (approximate based on period length)
    days = len(prices)
    years = days / 252  # Trading days per year
    annualized_return = ((1 + total_return / 100) ** (1 / years) - 1) * 100 if years > 0 else total_return

    # Daily returns for volatility calculation
    daily_returns = prices.pct_change().dropna()

    # Volatility (annualized)
    volatility = float(daily_returns.std() * np.sqrt(252) * 100)

    # Sharpe ratio (simplified, assuming 0% risk-free rate)
    sharpe_ratio = (annualized_return / volatility) if volatility > 0 else 0

    # Max drawdown
    cumulative = (1 + daily_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = float(drawdown.min() * 100)

    return {
        "start_price": round(start_price, 2),
        "end_price": round(end_price, 2),
        "total_return_pct": round(total_return, 2),
        "annualized_return_pct": round(annualized_return, 2),
        "volatility_pct": round(volatility, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "max_drawdown_pct": round(max_drawdown, 2)
    }


def calculate_correlations(data_dict: dict) -> dict:
    """Calculate correlation matrix between stocks"""
    # Create DataFrame with aligned data
    df = pd.DataFrame(data_dict)

    # Calculate correlation matrix
    corr_matrix = df.corr()

    # Extract pairwise correlations
    correlations = {}
    tickers = list(data_dict.keys())

    for i in range(len(tickers)):
        for j in range(i + 1, len(tickers)):
            ticker1, ticker2 = tickers[i], tickers[j]
            corr_value = float(corr_matrix.loc[ticker1, ticker2])
            key = f"{ticker1}_{ticker2}"
            correlations[key] = round(corr_value, 4)

    return correlations


def compare_stocks(tickers: list, period: str = "6mo") -> dict:
    """
    Compare multiple stocks over the same time period.

    Args:
        tickers: List of ticker symbols
        period: Time period for comparison

    Returns:
        Dictionary with comparison results
    """
    print(f"Comparing {len(tickers)} stocks over {period}...", file=sys.stderr)

    # Fetch data for all stocks
    stock_data = {}
    for ticker in tickers:
        try:
            print(f"  Fetching {ticker}...", file=sys.stderr)
            stock_data[ticker] = fetch_stock_data(ticker, period)
        except Exception as e:
            print(f"  Failed to fetch {ticker}: {e}", file=sys.stderr)
            sys.exit(1)

    # Align all data to same dates (intersection)
    df = pd.DataFrame(stock_data)
    df = df.dropna()  # Remove rows with missing data

    if df.empty:
        raise ValueError("No overlapping data found for all stocks")

    print(f"  Found {len(df)} overlapping data points", file=sys.stderr)

    # Calculate metrics for each stock
    stocks_results = []
    for ticker in tickers:
        metrics = calculate_metrics(df[ticker])
        metrics['ticker'] = ticker
        stocks_results.append(metrics)

    # Calculate correlations
    correlations = calculate_correlations(df.to_dict('series'))

    # Rankings
    rankings = {
        "best_return": max(stocks_results, key=lambda x: x['total_return_pct'])['ticker'],
        "worst_return": min(stocks_results, key=lambda x: x['total_return_pct'])['ticker'],
        "most_volatile": max(stocks_results, key=lambda x: x['volatility_pct'])['ticker'],
        "least_volatile": min(stocks_results, key=lambda x: x['volatility_pct'])['ticker'],
        "best_risk_adjusted": max(stocks_results, key=lambda x: x['sharpe_ratio'])['ticker']
    }

    result = {
        "comparison_date": datetime.now().strftime("%Y-%m-%d"),
        "period": period,
        "date_range": {
            "start": df.index[0].strftime("%Y-%m-%d"),
            "end": df.index[-1].strftime("%Y-%m-%d")
        },
        "stocks": stocks_results,
        "correlations": correlations,
        "rankings": rankings
    }

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Compare performance of multiple stocks"
    )
    parser.add_argument(
        "--tickers",
        nargs="+",
        required=True,
        help="Stock ticker symbols to compare (e.g., AAPL MSFT GOOGL)"
    )
    parser.add_argument(
        "--period",
        default="6mo",
        choices=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
        help="Time period for comparison (default: 6mo)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path for results (e.g., tmp/comparison.json)"
    )

    args = parser.parse_args()

    if len(args.tickers) < 2:
        print("ERROR: Need at least 2 tickers to compare", file=sys.stderr)
        sys.exit(1)

    # Perform comparison
    try:
        results = compare_stocks(args.tickers, args.period)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Comparison complete!", file=sys.stderr)
    print(f"Results saved to {output_path}", file=sys.stderr)

    # Print summary
    print(f"\n{'='*60}")
    print(f"STOCK COMPARISON SUMMARY ({results['period']})")
    print(f"{'='*60}")

    for stock in results['stocks']:
        print(f"\n{stock['ticker']}:")
        print(f"  Return: {stock['total_return_pct']:+.2f}%")
        print(f"  Volatility: {stock['volatility_pct']:.2f}%")
        print(f"  Sharpe Ratio: {stock['sharpe_ratio']:.2f}")

    print(f"\nRANKINGS:")
    print(f"  Best Return: {results['rankings']['best_return']}")
    print(f"  Lowest Risk: {results['rankings']['least_volatile']}")
    print(f"  Best Risk-Adjusted: {results['rankings']['best_risk_adjusted']}")


if __name__ == "__main__":
    main()
