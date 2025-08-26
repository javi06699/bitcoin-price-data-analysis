import yfinance as yf
import os

btc = yf.download("BTC-USD", start="2015-01-01", end="2025-08-25")
#sp500 = yf.download("^GSPC", start="2015-01-01", end="2025-08-25")
header_custom = ['close', 'high', 'low', 'open', 'volume']

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Save to CSV in data directory
btc.to_csv("data/btc_data.csv", header=header_custom)
