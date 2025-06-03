from matplotlib import pyplot as plt
import logging

from config import DATE_INTERVAL, LINESTYLES, STEP, KEY, SHEET_ID, SHEET_READ_RANGE,  WRITE_START_CELL
from utils.sheets import GoogleSheets
from utils.yahoo import download_from_yahoo
from analysis.support_resistance import support_resistance_lines
from analysis.trends import predictions
from analysis.visualization import draw_turning_points, draw_candle_chart, draw_line_chart


logging.basicConfig(level=logging.INFO, filename="app.log", filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

logger = logging.getLogger(__name__)


def main():
    gsheet = GoogleSheets(KEY)
    try:
        tickers = gsheet.get_stock_name_from_google(SHEET_ID, SHEET_READ_RANGE)
    except Exception as e:
        logger.critical(f"Failed to fetch tickers: {e}")
        return

    for ticker in tickers:
        stock_data = download_from_yahoo(ticker[0])
        if stock_data.empty:
            continue

        df = stock_data
        close_df = df[['Close']].to_numpy().flatten()
        date_series = df['Date']
        date_list = [d[5:] if isinstance(d, str) else d.strftime('%m-%d') for d in date_series]
        date_axis = (list(range(0, len(date_list), DATE_INTERVAL)), date_list[::DATE_INTERVAL])
        lines, extrema_prices = support_resistance_lines(close_df)
        draw_turning_points(ticker[0], close_df, extrema_prices)

        draw_candle_chart(ticker[0], df, lines, 'green', 'red', date_axis)

        y_values, lines_coords = predictions(df, STEP)

        # Extend date axis for prediction
        extended_positions = range(date_axis[0][-1] + DATE_INTERVAL, date_axis[0][-1] + 60, DATE_INTERVAL)

        date_axis[0].extend(extended_positions)
        date_axis[1].extend(range(DATE_INTERVAL, 60, DATE_INTERVAL))

        draw_line_chart(ticker[0], df, close_df, lines_coords, date_axis, LINESTYLES)
        gsheet.write_to_google_sheet(SHEET_ID, WRITE_START_CELL, y_values)

        plt.show()


if __name__ == "__main__":
    main()

