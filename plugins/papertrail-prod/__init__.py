import ast

import requests
import json
import datetime
import user_provision

def getDate():
    return datetime.datetime.now()

def getProdApiToken(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'papertrail-prod':
            return apiToken['ProdApiToken']
def getUrl(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'papertrail-dev':
            return apiToken['url']
def getRights(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'papertrail-prod':
            return apiToken['permission']

# Send papertrail email invite to user
def inviteUser(email,configMap,allPermissions,groups):
    plugin = "PaperTrail-prod"
    log = 'PaperTrail-prod: Email invite from papertrail sent.\n'
    instruction = 'Look for email invite from PaperTrail-prod'
    rights = getRights(configMap)
    rights['user[email]'] = email
    for permission in allPermissions:
        permission = ast.literal_eval(permission)
        if permission['plugin'] == 'papertrail-dev':
            del permission['plugin']
            rights = permission
    users = requests.post(getUrl(configMap)+"/invite.json",
                          headers={'X-Papertrail-Token': getProdApiToken(configMap)}, data=rights)

    if users.status_code!=200:
        log='PaperTrail-prod error: '+str(users.status_code)+str(users.content)+'\n'
        instruction=log
        print(log)
    return user_provision.getJsonResponse(plugin, email, log, instruction)

def removeUser(email,configMap):
    plugin = "PaperTrail-prod"
    log = 'PaperTrail-prod: User removed from papertrail-prod.\n'
    instruction = 'User removed from papertrail-prod.  '

    users = requests.get(getUrl(configMap)+".json",
                         headers={'X-Papertrail-Token': getProdApiToken(configMap)})
    my_json = users.content.decode('utf8')
    data = json.loads(my_json)
    for element in data:
        if element['email'] == email:
            id = element['id']
    try:
        users = requests.delete(getUrl(configMap)+"/"+str(id)+ ".json",
                                headers={'X-Papertrail-Token': getProdApiToken(configMap)})
        #print(users.status_code)
    except (UnboundLocalError):
        log = ' User does not exist, delete failed.\n'


    return user_provision.getJsonResponse(plugin, email, log, instruction)

#
# def listUsers(email, configMap):
#     users = requests.get("https://papertrailapp.com/api/v1/users.json", headers={'X-Papertrail-Token': getDevApiToken(configMap)})
#     my_json = users.content.decode('utf8')
#     data = json.loads(my_json)
#     #for element in data:
#        #print (element['email'])
#        #print (element['id'])
#
#     return {"Plugin name": "PaperTrail",
#              "Log": email[:-13]+" "+(getpass.getuser()+" "+getDate().strftime("%Y-%m-%d %H:%M")+" | Papertrail: Listed users.\n"),
#              "Instruction":"Look for email invite from PaperTrail"}