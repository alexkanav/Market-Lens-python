# Stock Technical Analysis from Google Sheets

This project reads a list of stock tickers from a Google Sheet, downloads price data from Yahoo Finance, estimates support and resistance levels using Kernel Density Estimation (KDE), computes trend-based price predictions, and generates detailed visualizations including candlestick charts and trend lines. Writes prediction results back to Google Sheets.

---

## Features
1. Google Sheets Integration
Automatically loads a list of stock tickers from a Google Sheet.

2. Data Collection from Yahoo Finance
Fetches historical OHLC (Open, High, Low, Close) data using the yfinance API.

3. Support & Resistance Levels
Uses Kernel Density Estimation on local extrema to detect key levels.

4. Trend Line Forecasting
Computes upward/downward trends and predicts future price ranges.

5. Visualizations -- Generates:

   - Candlestick charts

   - Support & resistance levels

   - Trend line extrapolations

   - Annotated turning points

---
## Results Export
Writes prediction results back to Google Sheets.

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


