import pandas as pd
import numpy as np
from scipy.signal import argrelextrema, find_peaks
from sklearn.neighbors import KernelDensity
from matplotlib import pyplot as plt
import logging

from config import INDICES, TIMEFRAMES, DATE_INTERVAL, PEAKS_RANGE, LINESTYLES, STEP
from yahoo_stock_data import download_from_yahoo
from graphics import draw_turning_points, draw_candle_chart, draw_line_chart
from gsheet_data import get_stock_name_from_google, write_to_google_sheet

logging.basicConfig(level=logging.INFO, filename="main.log",filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")


def support_resistance_lines(close_df: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Estimate support and resistance levels from price data using kernel density estimation.

    Parameters:
    - close_df (np.ndarray): Array of closing prices.

    Returns:
    - Tuple (np.ndarray, np.ndarray):
        - price_range[peaks]: Estimated support/resistance price levels (peak locations in the KDE).
        - ext_prices: Combined local maxima and minima prices used for KDE estimation.
    """
    num_peaks = -999  # Initialize number of peaks to a dummy out-of-range value
    maxima = argrelextrema(close_df, np.greater)  # find_peaks(max)
    minima = argrelextrema(close_df, np.less)  # find_peaks(min)

    # Combine extrema prices into a single array for density estimation
    ext_prices = np.concatenate((close_df[maxima], close_df[minima]))

    if ext_prices.size == 0:
        return np.array([]), np.array([])

    # Define an initial interval and bandwidth for the KDE
    interval = ext_prices[0] / 10000
    bandwidth = interval

    # Tune the bandwidth until the number of peaks in the KDE is within a desired range
    while num_peaks < PEAKS_RANGE[0] or num_peaks > PEAKS_RANGE[1]:
        # Apply Kernel Density Estimation with current bandwidth
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(ext_prices.reshape(-1, 1))

        # Define the price range over which to evaluate the KDE
        a, b = min(ext_prices), max(ext_prices)
        price_range = np.linspace(a, b, 1000).reshape(-1, 1)

        # Evaluate the KDE and find peaks in the estimated density
        pdf = np.exp(kde.score_samples(price_range))
        peaks = find_peaks(pdf)[0]
        num_peaks = len(peaks)

        # Increment bandwidth to smooth more if too many peaks (or sharpen if too few)
        bandwidth += interval

        # Prevent infinite loop by limiting bandwidth expansion
        if bandwidth > 100 * interval:
            break

    return price_range[peaks], ext_prices


def calculate_trend_lines(df: pd.DataFrame, timeframe: int, step: int) -> tuple[tuple[np.ndarray, np.ndarray], list[float]]:
    """
    Calculate trend lines over a given frame.

    """
    maxim = []
    minim = []
    ind_min = []
    ind_max = []
    trendlines_idx = []
    trendlines = []
    mavg_df = df[['Open', 'Close']].rolling(window=3).mean()
    for i in range(len(df) - timeframe - 1, len(df), step):
        # Ensure the slice doesn't exceed bounds
        if i + step > len(mavg_df):
            continue

        open_slice = mavg_df['Open'].iloc[i:i + step]
        close_slice = mavg_df['Close'].iloc[i:i + step]
        mid_price = ((open_slice - close_slice) / 2 + close_slice).median()

        trendlines.append(mid_price)
        trendlines_idx.append(mavg_df.index[i])
        minim.append(df.Close.iloc[i:i + step].min())
        ind_min.append(df.Close.iloc[i:i + step].idxmin())
        maxim.append(df.Close.iloc[i:i + step].max())
        ind_max.append(df.Close.iloc[i:i + step].idxmax())

    # Fit a first-degree polynomial (a straight line) to the data
    if len(trendlines_idx) < 2:
        return (np.zeros(len(INDICES)), np.zeros(len(INDICES))), [0, 0]

    coeffs = np.polyfit(trendlines_idx, trendlines, 1)

    # Create the polynomial function from the coefficients
    fit_fn = np.poly1d(coeffs)
    fitted_values = fit_fn(trendlines_idx)

    # Calculate the difference between interpolated fit and actual Close value at each index in ind_min, ind_max
    fit_residuals_at_minima = [
        np.interp(i, trendlines_idx, fitted_values) - df.Close.loc[i]
        for i in ind_min
    ]
    fit_residuals_at_maxima = [
        df.Close.loc[i] - np.interp(i, trendlines_idx, fitted_values)
        for i in ind_max
    ]

    y_min = INDICES * coeffs[0] + coeffs[1] - max(fit_residuals_at_minima)
    y_max = INDICES * coeffs[0] + coeffs[1] + max(fit_residuals_at_maxima)
    y_mid = (timeframe + len(df)) * coeffs[0] + coeffs[1]
    y_preds = [y_mid - max(fit_residuals_at_minima), y_mid + max(fit_residuals_at_maxima)]

    return (y_min, y_max), y_preds


def predictions(df: pd.DataFrame, step: int) -> tuple[list[list[float]], list[tuple[np.ndarray, np.ndarray]]]:
    """
    Generate trend line predictions for multiple timeframes.

    This function iterates over predefined timeframes, calculates trend lines and their corresponding
    predicted y-values using the given dataframe and step size.
    """
    y_values = []
    lines_coords = []
    for timeframe in TIMEFRAMES:
        line_coords, y_preds = calculate_trend_lines(df, timeframe, step)
        y_values.append(y_preds)
        lines_coords.append(line_coords)
    return y_values, lines_coords


def main():
    stock_names = get_stock_name_from_google()
    for stock_name in stock_names:
        stock_data = download_from_yahoo(stock_name[0])
        if stock_data.empty:
            continue

        df = stock_data
        close_df = df[['Close']].to_numpy().flatten()
        date_series = df['Date']
        date_list = [d[5:] if isinstance(d, str) else d.strftime('%m-%d') for d in date_series]
        date_axis = (list(range(0, len(date_list), DATE_INTERVAL)), date_list[::DATE_INTERVAL])
        lines, extrema_prices = support_resistance_lines(close_df)
        draw_turning_points(stock_name[0], close_df, extrema_prices)

        draw_candle_chart(stock_name[0], df, lines, 'green', 'red', date_axis)

        y_values, lines_coords = predictions(df, STEP)

        # Extend date axis for prediction
        extended_positions = range(date_axis[0][-1] + DATE_INTERVAL, date_axis[0][-1] + 60, DATE_INTERVAL)

        date_axis[0].extend(extended_positions)
        date_axis[1].extend(range(DATE_INTERVAL, 60, DATE_INTERVAL))

        draw_line_chart(stock_name[0], df, close_df, lines_coords, date_axis, LINESTYLES)
        write_to_google_sheet(y_values)

        plt.show()


if __name__ == "__main__":
    main()

