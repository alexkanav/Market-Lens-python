import yfinance as yf
import pandas as pd
from datetime import date
import logging


logger = logging.getLogger(__name__)


def download_from_yahoo(ticker: str) -> pd.DataFrame:
    """
    Downloads 1 year of historical stock data for a given ticker from Yahoo Finance.

    Saves the data to a CSV file named '<ticker>_<date>.csv'.

    Parameters
    ----------
    ticker : str
        The stock ticker symbol (e.g., 'AAPL', 'GOOG').

    Returns
    -------
    pandas.DataFrame
        The downloaded DataFrame if successful.
        Returns an empty DataFrame if the download fails or data is insufficient.
    """
    today = date.today().isoformat()
    file_name = f"data/{ticker}_{today}.csv"

    try:
        data = yf.download(ticker, period="1y")

        if data.empty:
            logging.warning(f"No data returned from Yahoo '{ticker}'.")
            return pd.DataFrame()

        df = data.reset_index()
        df['Date'] = df['Date'].astype(str)
        df.to_csv(file_name, index=False)

        if len(df) < 125:
            logging.warning(f"Data for '{ticker}' has less than 125 rows.")
            return pd.DataFrame()

        return df

    except Exception as e:
        logger.error(f"Exception occurred while downloading data for '{ticker}': {e}")
        return pd.DataFrame()
