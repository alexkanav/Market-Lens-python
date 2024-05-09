from config_stock import *
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import googleapiclient.discovery

from pylab import *
import yfinance as yf
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import argrelextrema, find_peaks
from sklearn.neighbors import KernelDensity
from datetime import date
import logging


logging.basicConfig(level=logging.INFO, filename="main.log",filemode="a",
                    format="%(asctime)s %(levelname)s %(message)s")

CREDENTIALS_FILE = 'trade_key.json'
spredsheets_id = google_sheet_id
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)



def get_stock_name_from_google():
    values = service.spreadsheets().values().get(
        spreadsheetId=spredsheets_id,
        range=google_sheet_read,
        majorDimension='ROWS'
    ).execute()
    return values.get('values')


def download_from_yahoo(stock_name):
    today = date.today()
    file_name = stock_name + str(today) + '.csv'

    try:
        data = yf.download(stock_name, period="1y")
        data.to_csv(file_name)
        df = pd.read_csv(file_name)
        if len(df) > 125:
            suc = 1
            rez = df
        else:
            suc = 0
            rez = 0

    except Exception as e:
        suc = 0
        rez = 0
        logging.error("Exception occurred", exc_info=True)

    return suc, rez


def draw_line_chart(s_n, sample_df, end_range, end_array, r_axis3, date_value3):
    mavg_df = sample_df[['Open', 'High', 'Low', 'Close']].rolling(window=3).mean()


    def trend_angle(frame):
        xxtrendline2 = np.array([])
        trendline2 = np.array([])

        for i in range(end_array - frame - 1, end_array, wind2):
            trendline2 = np.append(trendline2, (
                        (mavg_df.Open.loc[i:i + wind2] - mavg_df.Close.loc[i:i + wind2]) / 2 + mavg_df.Close.loc[i:i + wind2]).median())
            xxtrendline2 = np.append(xxtrendline2, mavg_df.Open.index[i])
        tilt_angle, intercmin = np.polyfit(xxtrendline2, trendline2, 1)
        angle = np.arctan(tilt_angle) * 180 / np.pi

        return angle


    wind2 = 5
    tf1 = timeframe[0]
    tf2 = timeframe[1]
    tf3 = timeframe[2]

    angle_1 = trend_angle(tf1)
    angle_2 = trend_angle(tf2)
    angle_3 = 90

    if abs(angle_2 - angle_1) > 45:
        return "prediction is impossible"

    while abs(angle_2 - angle_1) > 10:
        tf2 += 1
        angle_2 = trend_angle(tf2)

    while abs(angle_3 - angle_2) > 20:
        tf3 += 1
        angle_3 = trend_angle(tf3)

    for sn, color_line in ((tf1, 'red'), (tf2, 'green'), (tf3, 'blue')):
        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])
        xxtrendline = np.array([])
        trendline = np.array([])

        time_frame2 = sn
        for i in range(end_array - time_frame2 -1, end_array, wind2):
            trendline = np.append(trendline, ((mavg_df.Open.loc[i:i + wind2] - mavg_df.Close.loc[i:i + wind2]) / 2 + mavg_df.Close.loc[i:i + wind2]).median())
            xxtrendline = np.append(xxtrendline, mavg_df.Open.index[i])

        for i in range(end_array - sn - 1, end_array, wind2):
            minim = np.append(minim, sample_df.Close.iloc[i:i + wind2].min())
            xxmin = np.append(xxmin, sample_df.Close.iloc[i:i + wind2].idxmin())
            maxim = np.append(maxim, sample_df.Close.loc[i:i + wind2].max())
            xxmax = np.append(xxmax, sample_df.Close.iloc[i:i + wind2].idxmax())

        slmid2 = np.polyfit(xxtrendline, trendline, 1)
        yn_mid2 = np.poly1d(slmid2)
        tilt_angle, intercmin = np.polyfit(xxtrendline, trendline, 1)

        asd = pd.DataFrame(range(10, end_range))

        min_str_min = []
        for i in xxmin:
            dd3 = np.interp(i, xxtrendline, yn_mid2(xxtrendline))
            min_str_min.append(dd3 - sample_df.Close.loc[i])

        max_str_max2 = []
        for i in xxmax:
            dd5 = np.interp(i, xxtrendline, yn_mid2(xxtrendline))
            max_str_max2.append(sample_df.Close.loc[i] - dd5)

        if save_chart == 1:
            plt.plot(sample_df.index, sample_df.Close, color='black')
            trendline_drawing = plt.plot(xxtrendline, yn_mid2(xxtrendline), color='gold')
            plt.plot(asd, asd * tilt_angle + intercmin + max(max_str_max2), color=color_line, linewidth=0.5)
            plt.plot(asd, asd * tilt_angle + intercmin - max(min_str_min), color=color_line, linewidth=0.5)

        max_lev = []
        min_lev = []

        if sn == tf3:
            for i in (timeframe[5], timeframe[4], timeframe[3], timeframe[2]):
                max_lev.append((i + end_array) * tilt_angle + intercmin + max(max_str_max2))
                min_lev.append((i + end_array) * tilt_angle + intercmin - max(min_str_min))

            predicted_points['1d min'] = min_lev[0]
            predicted_points['1d max'] = max_lev[0]
            predicted_points['5d min'] = min_lev[1]
            predicted_points['5d max'] = max_lev[1]
            predicted_points['10d min'] = min_lev[2]
            predicted_points['10d max'] = max_lev[2]
            predicted_points['1m min'] = min_lev[3]
            predicted_points['1m max'] = max_lev[3]

        elif sn == tf2:
            max_lev.append((timeframe[1] + end_array) * tilt_angle + intercmin + max(max_str_max2))
            min_lev.append((timeframe[1] + end_array) * tilt_angle + intercmin - max(min_str_min))

            predicted_points['3m min'] = min_lev[0]
            predicted_points['3m max'] = max_lev[0]

        elif sn == tf1:
            max_lev.append((timeframe[0] + end_array) * tilt_angle + intercmin + max(max_str_max2))
            min_lev.append((timeframe[0] + end_array) * tilt_angle + intercmin - max(min_str_min))

            predicted_points['6m min'] = min_lev[0]
            predicted_points['6m max'] = max_lev[0]

    if save_chart == 1:
        # rotate x-axis tick labels
        plt.xticks(rotation=45, ha='right', fontsize=8)
        xticks(r_axis3, date_value3)

        plt.savefig(s_n + '.png')



    print('predicted_points = ', predicted_points)

    return predicted_points



def s_r_lines(stock_data):
    num_peaks = -999
    peaks_range = [2, 10]
    sample = stock_data.iloc[:][['Close']].to_numpy().flatten()
    maxima = argrelextrema(sample, np.greater)  # find_peaks(max)
    minima = argrelextrema(sample, np.less)  # find_peaks(min)
    extrema = np.concatenate((maxima, minima), axis=1)[0]
    extrema_prices = np.concatenate((sample[maxima], sample[minima]))
    interval = extrema_prices[0] / 10000
    bandwidth = interval

    while num_peaks < peaks_range[0] or num_peaks > peaks_range[1]:
        initial_price = extrema_prices[0]
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(extrema_prices.reshape(-1, 1))
        a, b = min(extrema_prices), max(extrema_prices)
        price_range = np.linspace(a, b, 1000).reshape(-1, 1)
        pdf = np.exp(kde.score_samples(price_range))
        peaks = find_peaks(pdf)[0]
        num_peaks = len(peaks)
        bandwidth += interval
        if bandwidth > 100 * interval:
            break

    return price_range[peaks]



def write_to_google_sheet(predicted):
    val = []
    for stn in predicted:
        val.append(predicted[stn])

    values = service.spreadsheets().values().batchUpdate(
        spreadsheetId=spredsheets_id,
        body={
            "valueInputOption" : "USER_ENTERED",
            "data": [
                {"range": start_cell_for_write,
                 "majorDimension":'ROWS',
                 "values": val}
            ]
        }
    ).execute()



def main():
    stock_names = get_stock_name_from_google()
    predicted = {}
    for sn in stock_names:

        if not sn:
            predicted['null'] = ["Invalid stock name",'','','','','','','','','','','']
            continue

        suc, stock_data = download_from_yahoo(sn[0])
        if suc == 0:
            predicted[sn[0]] = ["Invalid stock name",'','','','','','','','','','','']
            continue

        # volume analysis
        vol = stock_data[stock_data['Volume'] == 0]
        if len(vol) > 20:
            predicted[sn[0]] = ["Insufficient data for analysis",'','','','','','','','','','','']
            continue

        # lines = s_r_lines(stock_data)
        end_array = len(stock_data)
        sample_df = stock_data.iloc[:]
        date = stock_data['Date']
        date_dict = date.to_dict()
        list_date = [date_dict[i][5:] for i in date_dict]
        date_value2 = list_date + [x for x in range(0, 180)]
        r_axis2 = [x for x in range(0, len(date_value2))]
        r_axis3 = [x for x in range(0, len(r_axis2), 5)]
        date_value3 = [date_value2[i] for i in r_axis3]
        if save_chart == 1:
            f = plt.figure()
            f.suptitle('Line chart - ' + sn[0])
            f.set_figwidth(15)
            f.set_figwidth(10)
        pred = draw_line_chart(sn[0], sample_df, end_range, end_array, r_axis3, date_value3)
        if pred == "prediction is impossible":
            predicted[sn[0]] = ["prediction is impossible",'','','','','','','','','','','']
        else:
            predicted[sn[0]] = [pred['1d min'], pred['1d max'], pred['5d min'], pred['5d max'], pred['10d min'], pred['10d max'], pred['1m min'], pred['1m max'], pred['3m min'], pred['3m max'], pred['6m min'], pred['6m max']]


    write_to_google_sheet(predicted)


if __name__ == "__main__":
    main()

# plt.show()