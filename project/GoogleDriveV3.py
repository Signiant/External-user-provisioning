from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client import clientsecrets
import googleapiclient.errors

#this module uses Google Drive v3 API because there is no option to
# work with folders in Google Spreadsheet v4 API

def buildService():

    global file

    # Setup the Drive v3 API
    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        try:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)
        except clientsecrets.InvalidClientSecretsError:
            print('The client secrets were missing or invalid: ')
        except client.UnknownClientSecretsFlowError:
            print('This OAuth 2.0 flow is unsupported')
        except client.Error:
            print('Unexpected Error')

    service = build('drive', 'v3', http=creds.authorize(Http()))

    return service

def moveFileToFolder(fileID, folderID, service):

    global file

    file_id = fileID
    folder_id = folderID
    # Retrieve the existing parents to remove
    try:
        file = service.files().get(fileId=file_id, fields='parents').execute()
    except googleapiclient.errors.HttpError:
        print("Error: Could not retrieve an existing parent of a file ")
        return None


    previous_parents = ",".join(file.get('parents'))
    try:
        # Move the file to the new folder
        file = service.files().update(fileId=file_id,
                                            addParents=folder_id,
                                            removeParents=previous_parents,
                                            fields='id, parents').execute()
    except googleapiclient.errors.HttpError:
        print("Could not move a file to the excpected folder. Check the folder ID in your config.yaml file")
        return None

    return file