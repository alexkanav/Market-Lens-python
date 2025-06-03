import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import logging


logger = logging.getLogger(__name__)


class GoogleSheets:
    def __init__(self, key_file: str):
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                key_file, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            )
            http_auth = credentials.authorize(httplib2.Http())
            self.service = build('sheets', 'v4', http=http_auth)
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets API client: {e}")
            raise

    def get_stock_name_from_google(self, gsheet_id: str, sheet_range: str) -> list[list[str]]:
        """
        Reads stock names (tickers) from a Google Sheet.
        """
        try:
            values = self.service.spreadsheets().values().get(
                spreadsheetId=gsheet_id,
                range=sheet_range,
                majorDimension='ROWS'
            ).execute()
            return values.get('values')
        except Exception as e:
            logger.error(f"Google Sheets API error during read: {e}")
            return []

    def write_to_google_sheet(self, gsheet_id, start_sell, values: list[list[float]]):
        """
        Writes prediction results to a specified range in a Google Sheet.
        """
        try:
            self.service.spreadsheets().values().batchUpdate(
                spreadsheetId=gsheet_id,
                body={
                    "valueInputOption": "USER_ENTERED",
                    "data": [
                        {"range": start_sell,
                         "majorDimension": 'ROWS',
                         "values": values}
                    ]
                }
            ).execute()
        except Exception as e:
            logger.error(f"Google Sheets API error during write: {e}")

