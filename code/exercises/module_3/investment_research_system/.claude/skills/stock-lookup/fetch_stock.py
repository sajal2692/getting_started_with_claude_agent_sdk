#!/usr/bin/env python3
"""
Stock Data Lookup Helper Script

Fetches historical stock data using yfinance and exports to JSON or CSV.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

try:
    import yfinance as yf
    import pandas as pd
except ImportError:
    print("ERROR: Required packages not found. Make sure yfinance and pandas are installed.", file=sys.stderr)
    sys.exit(1)


def fetch_stock_data(ticker: str, period: str = "6mo") -> dict:
    """
    Fetch stock data for a given ticker and period.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL')
        period: Time period ('1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')

    Returns:
        Dictionary containing stock data and statistics
    """
    try:
        print(f"Fetching data for {ticker} (period: {period})...", file=sys.stderr)

        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            raise ValueError(f"No data found for ticker {ticker}")

        # Calculate statistics
        current_price = float(hist['Close'].iloc[-1])
        mean_price = float(hist['Close'].mean())
        min_price = float(hist['Close'].min())
        max_price = float(hist['Close'].max())
        std_dev = float(hist['Close'].std())
        volatility_pct = (std_dev / mean_price) * 100

        # Prepare history data
        history = []
        for date, row in hist.iterrows():
            history.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2),
                "volume": int(row['Volume'])
            })

        result = {
            "ticker": ticker.upper(),
            "period": period,
            "data_points": len(hist),
            "date_range": {
                "start": hist.index[0].strftime("%Y-%m-%d"),
                "end": hist.index[-1].strftime("%Y-%m-%d")
            },
            "current_price": round(current_price, 2),
            "statistics": {
                "mean": round(mean_price, 2),
                "min": round(min_price, 2),
                "max": round(max_price, 2),
                "std_dev": round(std_dev, 2),
                "volatility_pct": round(volatility_pct, 2)
            },
            "history": history
        }

        print(f"Successfully fetched {len(hist)} data points", file=sys.stderr)
        return result

    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


def save_json(data: dict, output_path: Path):
    """Save data as JSON"""
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to {output_path}", file=sys.stderr)


def save_csv(data: dict, output_path: Path):
    """Save data as CSV"""
    df = pd.DataFrame(data['history'])
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch historical stock data using yfinance"
    )
    parser.add_argument(
        "--ticker",
        required=True,
        help="Stock ticker symbol (e.g., AAPL, TSLA, MSFT)"
    )
    parser.add_argument(
        "--period",
        default="6mo",
        choices=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        help="Time period for historical data (default: 6mo)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output file path (e.g., tmp/stock_data.json)"
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "csv"],
        help="Output format (default: json)"
    )

    args = parser.parse_args()

    # Fetch data
    data = fetch_stock_data(args.ticker, args.period)

    # Save to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.format == "json":
        save_json(data, output_path)
    else:
        save_csv(data, output_path)

    # Print summary to stdout for agent to see
    print(f"\n✓ Stock data fetched successfully!")
    print(f"Ticker: {data['ticker']}")
    print(f"Period: {data['period']}")
    print(f"Data points: {data['data_points']}")
    print(f"Current price: ${data['current_price']}")
    print(f"Price range: ${data['statistics']['min']} - ${data['statistics']['max']}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
