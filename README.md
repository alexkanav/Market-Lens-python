# Stock Technical Analysis

A fully automated stock-analysis pipeline that reads tickers from Google Sheets, downloads historical market data from Yahoo Finance, computes technical indicators such as support and resistance levels using Kernel Density Estimation (KDE), performs trend-based price forecasting, and generates rich visualizations. Final predictions and key metrics are automatically written back to Google Sheets.
---

## Features
### Google Sheets Integration
- Automatically imports a list of stock tickers using the Google Sheets API.
- Writes prediction results (trend, forecast levels, support/resistance zones) back to the sheet.

### Market Data Collection
- Fetches historical OHLC data from Yahoo Finance using the yfinance API.
- Supports custom timeframes and intervals.

### Support & Resistance Detection
- Applies Kernel Density Estimation to highlight high-probability support/resistance clusters.
- Produces clean, interpretable levels.

### Trend Line Forecasting
- Identifies upward/downward trend channels.
- Fits regression-based trend lines.
- Projects forward price ranges and potential breakout points.

### High-Quality Visualizations
Automatically generates annotated charts including:

   - Candlestick charts

   - Trend line extrapolations

   - Detected turning points

   - KDE-based support & resistance zones

These visuals are saved locally for analysis or reporting.

---
## Screenshots

![screenshot_1](https://github.com/user-attachments/assets/d96df5eb-7247-4432-a05f-963bef6cf2e5)
![screenshot_2](https://github.com/user-attachments/assets/eda1304d-dff6-43b9-999f-34de9fd613c0)
![screenshot_3](https://github.com/user-attachments/assets/760fa478-830f-407f-91c7-7880e42b719e)

---
## How to Run
Clone the repository:

    bash
    git clone https://github.com/alexkanav/Market-Lens-python
    cd Market-Lens-python
    
Install dependencies:

    bash
    pip install -r requirements.txt

Set up Google Sheets API:

- Enable Google Sheets API in your Google Cloud Console.

- Download the service account credentials JSON file.

- Place it in your project root and update your script to load it.

Run the script:

    bash
    python main.py

---

## License
This project is licensed under the MIT License.


