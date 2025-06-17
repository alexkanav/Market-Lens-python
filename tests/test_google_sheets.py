import pytest
from unittest.mock import patch, MagicMock
from googleapiclient.errors import HttpError

from utils.sheets import GoogleSheets


# Test initialization of GoogleSheets class
@patch('utils.sheets.ServiceAccountCredentials.from_json_keyfile_name')
@patch('utils.sheets.httplib2.Http')
@patch('utils.sheets.build')
def test_initialization(mock_build, mock_http, mock_credentials):
    # Mock ServiceAccountCredentials
    mock_credentials.return_value = MagicMock()

    # Mock Http() instance
    mock_http_instance = MagicMock()
    mock_http.return_value = mock_http_instance

    # Mock the `authorize()` method on the credentials object to return the mock_http_instance
    mock_credentials.return_value.authorize.return_value = mock_http_instance

    # Mock the service object returned by the `build` function
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    # Initialize GoogleSheets with a mock key file
    key_file = 'mock_key.json'
    google_sheets = GoogleSheets(key_file)

    # Assert that the `build()` method was called with the correct parameters
    mock_build.assert_called_once_with('sheets', 'v4', http=mock_http_instance)


# Test get_stock_name_from_google method
@patch('utils.sheets.ServiceAccountCredentials.from_json_keyfile_name')
@patch('utils.sheets.httplib2.Http')
@patch('utils.sheets.build')
def test_get_stock_name_from_google(mock_build, mock_http, mock_credentials):
    # Mocking the Google Sheets API response
    mock_credentials.return_value = MagicMock()
    mock_http.return_value = MagicMock()
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_sheet = MagicMock()
    mock_service.spreadsheets().values().get().execute.return_value = {
        'values': [['AAPL'], ['GOOG'], ['CAT']]
    }

    google_sheets = GoogleSheets('mock_key.json')

    # Call the function to get stock names from the sheet
    stock_names = google_sheets.get_stock_name_from_google('mock_gsheet_id', 'Sheet1!A1:A3')

    # Assert the response is as expected
    assert stock_names == [['AAPL'], ['GOOG'], ['CAT']]

    # Check that the correct API method was called
    mock_service.spreadsheets().values().get().execute.assert_called_once()


# Test error handling in get_stock_name_from_google
@patch('utils.sheets.ServiceAccountCredentials.from_json_keyfile_name')
@patch('utils.sheets.httplib2.Http')
@patch('utils.sheets.build')
def test_get_stock_name_from_google_error(mock_build, mock_http, mock_credentials):
    # Mocking the Google Sheets API to raise an exception
    mock_credentials.return_value = MagicMock()
    mock_http.return_value = MagicMock()
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    mock_service.spreadsheets().values().get().execute.side_effect = HttpError(
        resp=MagicMock(status=500), content=b'Error'
    )

    google_sheets = GoogleSheets('mock_key.json')

    # Call the function and expect an empty list on error
    stock_names = google_sheets.get_stock_name_from_google('mock_gsheet_id', 'Sheet1!A1:A3')

    # Assert that an empty list is returned in case of an error
    assert stock_names == []


