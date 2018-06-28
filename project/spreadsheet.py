from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client import clientsecrets
import datetime
from apiclient import discovery
import getpass
import googleapiclient.errors
from project import GoogleDriveV3


newLine = 9
resultGlobal = None

def writeHeaderColumnNamesToSheet(SPREADSHEET_ID, service, email, configMap):

    range1 = 'A1:H14'
    range2 = 'A8:P20'
    values1 = [
        [
            'New Hire/Exit IT Systems Access\n',
            '\n'
            'The following systems require action taken when a new hire is onboarded or when there is an employee exit.  Please clone per new hire or exit.\n',
            "If you want to add more columns into the table, please, follow the instructions in the README.md file https://github.com/Signiant/External-user-provisioning\n",
            "ROLE: Product Marketing Manager",
            "Email:  " + email,
            "AD Login:  " + email.split('@', 1)[0],
            "\n",
        ],
    ]

    values2 = [
        [
            'Plugin:tag', 'Success (add)', 'Log Message (add)','Update Method', 'User Created', 'Date In', 'Admin', 'Date Out', 'Admin', 'Success (remove)', 'Log Message (remove)',
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

    cont = True

    try:
        service.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

    except googleapiclient.errors.HttpError:
        print("Error. Could not create a spreadsheet for a user " + email + ". The value list might be out of index range ")
        print("\nFirst set of values is: ")
        print(values1)
        print("for range: " + range1)
        print("Second set: " )
        print(values2)
        print("for range: " + range2)
        cont =  False

    if cont:
        writeIDandNameToList(configMap, email.split('@', 1)[0], SPREADSHEET_ID, service)


# this method will write names and ids of every spreadsheet created for a user
# into the list
def writeIDandNameToList(configMap, fileName, fileID, service):

    rangeRow = 'A1:D1000'

    values1 = [
        [
            fileName, fileID,
        ],
    ]

    body = {
        'values': values1,
    }
    try:
        service.spreadsheets().values().append(
            spreadsheetId = configMap['spreadsheet_database']['id'], range=rangeRow,
            valueInputOption="RAW", body=body).execute()

    except googleapiclient.errors.HttpError:
        print("Error. User information was not updated in the list spreadsheet. The value list might be out of index range ")
        print("\nThe values are: ")
        print(values1)
        print("The range is: " + rangeRow)

def writeRowsToSheetToAddUser(SPREADSHEET_ID, email, plugin_tag, log, success):

    global newLine
    credentials = getCredentials()
    service = getService(credentials)
    now = datetime.datetime.now()
    #to add each plugin at a new line of a sheet
    rangeRow = 'A'+str(newLine)+':W1000'

    values1 = [
        [
            plugin_tag, success, log, 'Tool', email.split('@', 1)[0], now.strftime("%Y-%m-%d %H:%M"), getpass.getuser(),
        ],
    ]

    data = [
        {
            'range': rangeRow,
            'values': values1,
            'majorDimension': "ROWS",
        },
    ]

    body = {
        'valueInputOption': "RAW",
        'data': data
    }

    try:

        service.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

    except googleapiclient.errors.HttpError:
        print("Error. User " + email + " information was not added to the spreadsheet. The value list might be out of index range ")
        print("\nThe values are: ")
        print(values1)
        print("The range is: " + rangeRow)
        return False

    newLine+=1

    return True


def writeRowsToSheetToRemoveUser(SPREADSHEET_ID, log, success, plugin_tag):

    global newLine
    credentials = getCredentials()
    service = getService(credentials)
    now = datetime.datetime.now()
    rangeRow = 'A'+str(newLine)+':W1000'
    global resultGlobal

    try:
        #initialize it only ones
        if resultGlobal is None:
        # gets all the data from the entry file and store it globally so that every plugin has access to it.
            resultGlobal = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range= 'A1:W1000').execute()

    except googleapiclient.errors.HttpError:
        print("Could not connect to the spreadsheetList file. Possible reasons:"
              "\n Errors in config file"
              "\n Internet connection problems"
              "\n File does not exist")
        return None

    # gets all the rows of the entry file
    numRows = resultGlobal.get('values') if resultGlobal.get('values') is not None else 0

    # search nested lists of the file for the values equal to the plugin_tag being passed
    foundRow = search_nested(numRows, plugin_tag)

    #if the plugin tag is not found, appends new line with the tag name and remove info
    if foundRow == None:

        values1 = [
            [
                plugin_tag, " ", " ", " ", " ", " ", " ", now.strftime("%Y-%m-%d %H:%M"),
                getpass.getuser(), success, log
            ],
        ]
    #if it's found, takes the existing values + new values and appends new row
    else:

        values1 = [
            [
                foundRow[0], foundRow[1],foundRow[2], foundRow[3],
                foundRow[4], foundRow[5], foundRow[6], now.strftime("%Y-%m-%d %H:%M"), getpass.getuser(), success, log
            ],
        ]

    data = [
        {
            'range': rangeRow,
            'values': values1,
            'majorDimension': "ROWS",
        },
    ]

    body = {
        'valueInputOption': "RAW",
        'data': data
    }

    try:
        service.spreadsheets().values().batchUpdate(spreadsheetId=SPREADSHEET_ID, body=body).execute()

    except googleapiclient.errors.HttpError:
        print("User information could not be updated in the spreadsheet, because \nthe spreadsheet does not exist or the value list might be out of index range ")
        print("\nThe values are: ")
        print(values1)
        print("The range is: " + rangeRow)

        return False

    newLine += 1

    return True


#creates a google spreadsheet with the header, user name and email and column names
def initialize(email, configMap, arg):

    credentials = getCredentials()
    service = getService(credentials)
    if service is None:
        return None
    else:
        fileName = email.split('@', 1)[0]

        if 'spreadsheet_database' in configMap:
            spreadSheetDatabase_ID = configMap['spreadsheet_database']['id']
        else:
            print("Spreadsheet_database section is missing in your config file")
            return None

        #looks for a value in the spreadsheet list
        foundRow = findSpecificEntryInAllRows(service, spreadSheetDatabase_ID, fileName)

        #if the name is found, return ID of that spreadsheet
        if foundRow:
            return foundRow[1]
        #if not, it creates a new spreadsheet
        else:
            #if you need to add a user, new spreadsheet will be created
            if arg == 'add':

                SHEETS = discovery.build('sheets', 'v4', http=credentials.authorize(Http()))
                data = {'properties': {'title': fileName}}

                try:
                    #create spreadsheet
                    sheetCreated = SHEETS.spreadsheets().create(body=data).execute()

                except googleapiclient.errors.HttpError:
                    print("Could not create new spreadsheet for a user " + email)
                    return None

                SPREADSHEET_ID = sheetCreated['spreadsheetId']

                if 'spreadsheet_database' in configMap:
                    folderID = configMap['spreadsheet_database']['folderID']
                else:
                    print("Spreadsheet_database section is missing in your config file")
                    return None

                googleDriveServiceV3 = GoogleDriveV3.buildService()

                if googleDriveServiceV3:
                    newFolder = GoogleDriveV3.moveFileToFolder(SPREADSHEET_ID, folderID, googleDriveServiceV3)

                    if newFolder == None:
                        print("File was not moved to the expected folder. It was created in the authorized google drive account")
                else:
                    print("Could not authorize the user")

                # writes header data to a spreadsheet:
                writeHeaderColumnNamesToSheet(SPREADSHEET_ID, service, email, configMap)

                #returns the ID of the new spreadsheet
                return SPREADSHEET_ID
            # if you need to remove a user, but the spreadsheet does not exists, returns None
            else:
                return None


def getService(creds):

    service = None
    try:
        service = build('sheets', 'v4', http=creds.authorize(Http()))

    except AttributeError:
        print("client_secret.json is missing from your project")

    return service

def getCredentials():
   # CLIENT_SECRETS_FILE = "\client_secrets.json"

    # Full, permissive scope to access all of a user's files
    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        try:
            flow = client.flow_from_clientsecrets("project/client_secret.json", SCOPES)
            flags = tools.argparser.parse_args(args=[])
            creds = tools.run_flow(flow, store, flags)

        except clientsecrets.InvalidClientSecretsError:
            print('The client secrets were missing or invalid: ')
        except client.UnknownClientSecretsFlowError:
            print('This OAuth 2.0 flow is unsupported')
        except client.Error:
            print('Unexpected Error')

    return creds

#this function will search through every row in the list and return a value if it is equal to the value of a first cell
def findSpecificEntryInAllRows(service, SPREADSHEET_ID, searchValue):

    try:
        # gets the database spreadsheet
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range= 'A1:W1000').execute()

    except googleapiclient.errors.HttpError:
        print("Could not connect to the spreadsheetList file. Possible reasons:"
              "\n Errors in config file"
              "\n Internet connection problems"
              "\n File does not exist")
        return None

    # gets all the rows of the database (the section where the user was added)
    numRows = result.get('values') if result.get('values') is not None else 0

    if numRows == 0:
        writeNameAndIDtoDatabaseSpreadsheet(service, SPREADSHEET_ID)

    # search nested lists of the database for the values equal to the plugin_tag being removed
    foundRow = search_nested(numRows, searchValue)

    # if the name is found, return ID of that spreadsheet
    if foundRow:
        return foundRow
    else:
        return None

# This function will search each cell of mylist for val and if found will return entire row
def search_nested(mylist, val):

    if not mylist:
        print("The spreadsheet is empty")
        return None
    else:

        for i in range(len(mylist)):
            for j in range(len(mylist[i])):
                if mylist[i][j] == val:
                    return mylist[i]


def writeNameAndIDtoDatabaseSpreadsheet(service, SPREADSHEET_ID):

    rangeRow = 'A1:D1000'

    values1 = [
        [
            "Name", "ID",
        ],
    ]

    body = {
        'values': values1,
    }
    try:
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=rangeRow,
            valueInputOption="RAW", body=body).execute()

    except googleapiclient.errors.HttpError:
        print(
            "Error. Name and ID values were not updated in the database list spreadsheet. The value list might be out of index range ")
        print("\nThe values are: ")
        print(values1)
        print("The range is: " + rangeRow)



# automatically resize columns
# https://developers.google.com/sheets/api/samples/rowcolumn