# cDanQ4xL2nuK0iwuNiT

# Make a get request to get the latest position of the international space station from the opennotify api.
import requests
import json


def getApiToken(configMap):
    return configMap['global']['PapertrailApiToken']


def inviteUser(email,configMap):
    rights = {'user[email]': email,'user[read_only]': 1,'user[purge_logs]': 0}
    # Send invite to user
    users = requests.post("https://papertrailapp.com/api/v1/users/invite.json",headers={'X-Papertrail-Token': getApiToken(configMap)}, data=rights)
    print(users.status_code+': User succesfully invited.')

def deleteUser(email,configMap):
    #get id of user
    users = requests.get("https://papertrailapp.com/api/v1/users.json", headers={'X-Papertrail-Token': getApiToken(configMap)})
    my_json = users.content.decode('utf8')
    data = json.loads(my_json)
    for element in data:
        if element['email']==email:
            id=element['id']
            print(element['email'])
            print(element['id'])
    try:
        users = requests.delete("https://papertrailapp.com/api/v1/users/"+str(id)+".json",headers={'X-Papertrail-Token': getApiToken(configMap)})
        print(users.status_code)
        if users.status_code==200:
            print('User successfully deleted.')
    except (UnboundLocalError):
        print('User does not exist, invite failed.')

def listUsers(configMap):
    users = requests.get("https://papertrailapp.com/api/v1/users.json", headers={'X-Papertrail-Token': getApiToken(configMap)})
    my_json = users.content.decode('utf8')
    data = json.loads(my_json)
    #for element in data:
       #print (element['email'])
       #print (element['id'])
