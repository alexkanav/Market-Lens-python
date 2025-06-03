import pandas as pd
import numpy as np

from config import INDICES, TIMEFRAMES


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

