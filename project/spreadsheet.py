from __future__ import print_function
from apiclient.discovery import build
import httplib2
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client import clientsecrets
from apiclient import discovery
# from oauth2client import clientsecrets

def createSheet(creds, email):

    fileName = email.split('@', 1)[0] + ' - ENTRY'

    SHEETS = discovery.build('sheets', 'v4', http=creds.authorize(Http()))
    data = {'properties': {'title': fileName}} # replace with user name
    sheetCreated = SHEETS.spreadsheets().create(body=data).execute()
    if not sheetCreated:
        print("Unexpected error: sheet could not be created")
    else:
        return sheetCreated

def writeHeaderColumnNamesToSheet(SPREADSHEET_ID, service, email):
    range1 = 'A1:H14'
    range2 = 'A7:H20'
    values1 = [
        [
            'New Hire/Exit IT Systems Access\n',
            '\n'
            'The following systems require action taken when a new hire is onboarded or when there is an employee exit.  Please clone per new hire or exit.\n',
            '\n'
            "ROLE: Product Marketing Manager",
            "Email:  " + email,  # add user vemail
            "AD Login:  " + email.split('@', 1)[0],  # add user name
            "\n",
        ],
    ]

    # to add values here:
    values2 = [
        [
            'Update Method', 'Plugin:tag', 'User Created', 'Date In', 'Admin', 'Date Out', 'Admin',

        ],
    ]

    data = [
        {
            'range': range1,
            'values': values1,
            'majorDimension': "COLUMNS",
        },
        {
            'range': range2,
            'values': values2,
            'majorDimension': "ROWS",
        },
    ]

    body = {
        'valueInputOption': "RAW",
        'data': data
    }
    valuesUpdated = service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID, body=body).execute()

    return valuesUpdated

def writeRowsToSheet():

    return None


def initialize():

    #I'm hard coding it now, but email will be passed with each plugin
    email = "user-prov-dev@signiant.com"
    cont = True

    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        try:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            flags = tools.argparser.parse_args(args=[])
            creds = tools.run_flow(flow, store, flags)

        except clientsecrets.InvalidClientSecretsError:
            print ('The client secrets were missing or invalid: ')
            cont = False
        except client.UnknownClientSecretsFlowError:
            print('This OAuth 2.0 flow is unsupported')
            cont = False
        except client.Error:
            print('Unexpected Error')
            cont = False

    if cont:

        service = build('sheets', 'v4', http=creds.authorize(Http()))
        sheet = createSheet(creds, email)

        SPREADSHEET_ID = sheet['spreadsheetId']
        # to write pattern data to a spreadsheet:
        writeHeaderColumnNamesToSheet(SPREADSHEET_ID, service, email)

    return SPREADSHEET_ID
