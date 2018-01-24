import requests
import json
import datetime,getpass

import user_provision


def getDate():
    return datetime.datetime.now()

def getApiToken(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'papertrail':
            return apiToken['PapertrailApiToken']

def inviteUser(email,configMap):
    rights = {'user[email]': email,'user[read_only]': 1,'user[purge_logs]': 0}
    # Send papertrail email invite to user
    users = requests.post("https://papertrailapp.com/api/v1/users/invite.json",headers={'X-Papertrail-Token': getApiToken(configMap)}, data=rights)

    plugin = "PaperTrail"
    log ='PaperTrail: Email invite from papertrail sent.\n'
    instruction = 'Look for email invite from PaperTrail '
    return user_provision.getJsonResponse(plugin, email, log, instruction)

def removeUser(email,configMap):
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
        # if users.status_code==200:
        #     print('User successfully deleted.')
    except (UnboundLocalError):
        return (email[:-13]+" "+getDate().strftime("%Y-%m-%d %H:%M") +' | User does not exist, invite failed.\n')

    plugin = "PaperTrail"
    log = 'PaperTrail: User removed from papertrail.\n'
    instruction = 'User removed from papertrail."  '
    return user_provision.getJsonResponse(plugin, email, log, instruction)


def listUsers(email, configMap):
    users = requests.get("https://papertrailapp.com/api/v1/users.json", headers={'X-Papertrail-Token': getApiToken(configMap)})
    my_json = users.content.decode('utf8')
    data = json.loads(my_json)
    #for element in data:
       #print (element['email'])
       #print (element['id'])

    return {"Plugin name": "PaperTrail",
             "Log": email[:-13]+" "+(getpass.getuser()+" "+getDate().strftime("%Y-%m-%d %H:%M")+" | Papertrail: Listed users.\n"),
             "Instruction":"Look for email invite from PaperTrail"}