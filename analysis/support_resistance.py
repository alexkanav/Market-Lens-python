import numpy as np
from scipy.signal import argrelextrema, find_peaks
from sklearn.neighbors import KernelDensity

from config import PEAKS_RANGE


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

