from matplotlib import pyplot as plt

from config import INDICES


def draw_candle_chart(name: str, df, lines, up_color: str, down_color: str, date_axis: tuple[list[int], list[str]], region=None):
    """
    Draws a candlestick chart with optional highlight regions and additional support and resistance lines.

    This function visualizes price data as candlesticks and allows for overlaying custom regions
    (e.g., for highlighting patterns or events) as well as horizontal lines indicating support
    and resistance levels.
    """
    plt.figure('Candle chart', facecolor='lightgray')
    plt.suptitle(f'Support and Resistance - {name}')
    plt.xlabel("Dates")
    plt.ylabel("Price")

    # define width of candlestick elements
    width = .4
    peak_width = .05

    # define up and down prices
    up = df[df.Close >= df.Open]
    down = df[df.Close < df.Open]

        # plot up prices
    plt.bar(up.index, up.Close-up.Open, width, bottom=up.Open, color=up_color)
    plt.bar(up.index, up.High-up.Close, peak_width, bottom=up.Close, color=up_color)
    plt.bar(up.index, up.Low-up.Open, peak_width, bottom=up.Open, color=up_color)

        # plot down prices
    plt.bar(down.index, down.Close - down.Open, width, bottom=down.Open, color=down_color)
    plt.bar(down.index, down.High - down.Open, peak_width, bottom=down.Open, color=down_color)
    plt.bar(down.index, down.Low - down.Close, peak_width, bottom=down.Close, color=down_color)

    # draw support and resistance lines
    for x in lines:
        plt.hlines(x, 5, len(df), color='lightblue', linewidth=0.7)
        if region is not None:
            plt.fill_between(df.index, x - x * region, x + x * region, alpha=0.4)

    ax = plt.gca()  # get the current axes
    ax.set_facecolor("beige")

    # Set x-ticks with rotation and alignment
    plt.xticks(*date_axis, rotation=45, ha='right', fontsize=8)
    plt.tight_layout(pad=2.0)


def draw_line_chart(name, df, close_df, lines_coords: list, date_axis, linestyles: tuple):
    """
    Draws a financial line chart with closing prices and additional trend lines.
    """
    plt.figure('Line chart', facecolor='lightgray')
    plt.suptitle(f'Trends - {name}')
    plt.xlabel("Dates")
    plt.ylabel("Price")
    plt.grid(True, color='lightgray')

    # Plot main price line
    plt.plot(df.index, close_df, color='black')

    # Plot trend lines
    for coords, style in zip(lines_coords, linestyles):
        plt.plot(INDICES, coords[0], color=style[0], linestyle=style[1], linewidth=0.5, label=style[2])
        plt.plot(INDICES, coords[1], color=style[0], linestyle=style[1], linewidth=0.5)

    plt.legend(fontsize=8)
    ax = plt.gca()  # get the current axes
    ax.set_facecolor("beige")

    # Set x-ticks with rotation and alignment
    plt.xticks(*date_axis, rotation=45, ha='right', fontsize=8)
    plt.tight_layout(pad=2.0)


def draw_turning_points(name: str, close_df, extrema_prices):
    """
    Plots trend reversal (turning) points on a horizontal line.
    This is helpful in time series analysis for identifying critical moments in price movements.
    """
    plt.figure('Turning points', facecolor='lightgray')
    plt.suptitle(f'Trend reversal points - {name}')
    plt.xlabel("Price")
    plt.hlines(1, min(close_df), max(close_df))
    plt.eventplot(extrema_prices, orientation='horizontal', colors='b')

    ax = plt.gca()  # get the current axes
    ax.set_facecolor("beige")
