import requests
import json
import datetime
import user_provision
import ast
def getDate():
    return datetime.datetime.now()

def getDevApiToken(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'papertrail-dev':
            return apiToken['DevApiToken']

def getUrl(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'papertrail-dev':
            return apiToken['url']
def getRights(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'papertrail-dev':
            return apiToken['permission']

# Send papertrail email invite to user
def inviteUser(email,configMap,allPermissions,groups):
    rights = getRights(configMap)
    rights['user[email]'] = email

    for permission in allPermissions:
        permission=ast.literal_eval(permission)
        if permission['plugin']=='papertrail-dev':
            del permission['plugin']
            rights=permission

    users = requests.post(getUrl(configMap)+"/invite.json",headers={'X-Papertrail-Token': getDevApiToken(configMap)}, data=rights)

    plugin = "PaperTrail-dev"
    log = 'PaperTrail-dev: Email invite from papertrail sent.\n'
    instruction = 'Look for email invite from PaperTrail Dev '
    if users.status_code!=200:
        log='PaperTrail-dev error: '+str(users.status_code)+str(users.content)+' Make sure if email doesn\'t exist already.\n'
        instruction=log
        print(log)
    return user_provision.getJsonResponse(plugin, email, log, instruction)

def removeUser(email,configMap):
    #get id of user, Dev
    plugin = "PaperTrail-dev"
    log = 'PaperTrail-dev: User removed from papertrail.\n'
    instruction = 'User removed from papertrail-dev.'

    users = requests.get(getUrl(configMap)+".json",
                         headers={'X-Papertrail-Token': getDevApiToken(configMap)})
    my_json = users.content.decode('utf8')
    data = json.loads(my_json)
    for element in data:
        if element['email']==email:
            id=element['id']
    try:
        users = requests.delete(getUrl(configMap)+"/"+str(id)+".json",
                                headers={'X-Papertrail-Token': getDevApiToken(configMap)})
        #print(users.status_code)
    except (UnboundLocalError):
        log=' User does not exist, delete failed.\n'


    return user_provision.getJsonResponse(plugin, email, log, instruction)
