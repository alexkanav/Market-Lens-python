import yfinance as yf
import pandas as pd
from datetime import date
import logging


def download_from_yahoo(stock_name: str) -> pd.DataFrame:
    """
    Downloads 1 year of historical stock data for a given ticker from Yahoo Finance.

    Saves the data to a CSV file named '<stock_name>_<date>.csv'.

    Parameters
    ----------
    stock_name : str
        The stock ticker symbol (e.g., 'AAPL', 'GOOG').

    Returns
    -------
    pandas.DataFrame
        The downloaded DataFrame if successful.
        Returns an empty DataFrame if the download fails or data is insufficient.
    """
    today = date.today().isoformat()
    file_name = f"{stock_name}_{today}.csv"

    try:
        data = yf.download(stock_name, period="1y")

        if data.empty:
            logging.warning(f"No data returned from Yahoo '{stock_name}'.")
            return pd.DataFrame()

        df = data.reset_index()
        df['Date'] = df['Date'].astype(str)
        df.to_csv(file_name, index=False)

        if len(df) < 125:
            logging.warning(f"Data for {stock_name} has less than 125 rows.")
            return pd.DataFrame()

        return df

    except Exception:
        logging.error(f"Exception occurred while downloading data for '{stock_name}'", exc_info=True)
        return pd.DataFrame()
