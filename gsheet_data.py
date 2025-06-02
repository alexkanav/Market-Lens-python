import httplib2
from oauth2client.service_account import ServiceAccountCredentials
import googleapiclient.discovery

from config import GOOGLE_SHEET_ID, GOOGLE_SHEET_READ, START_CELL_FOR_WRITE, KEY


CREDENTIALS_FILE = KEY
SPREADSHEET_ID = GOOGLE_SHEET_ID
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets',
                                                                                  'https://www.googleapis.com/auth/drive'])
httpAuth = credentials.authorize(httplib2.Http())
service = googleapiclient.discovery.build('sheets', 'v4', http=httpAuth)


def get_stock_name_from_google() -> list[list[str]]:
    values = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=GOOGLE_SHEET_READ,
        majorDimension='ROWS'
    ).execute()
    return values.get('values')


def write_to_google_sheet(values: list[list[float]]):
    service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": START_CELL_FOR_WRITE,
                 "majorDimension": 'ROWS',
                 "values": values}
            ]
        }
    ).execute()
