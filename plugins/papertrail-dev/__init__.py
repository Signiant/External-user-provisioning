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
def inviteUser(email,configMap):

    #rights = {'user[email]': email,'user[read_only]': 1,'user[manage_members]':0, 'user[manage_billing]':0,'user[purge_logs]': 0,}
    rights=getRights(configMap)
    rights['user[email]']=email
    users = requests.post(getUrl(configMap)+"/invite.json",headers={'X-Papertrail-Token': getDevApiToken(configMap)}, data=rights)

    plugin = "PaperTrail-dev"
    log = 'PaperTrail-dev: Email invite from papertrail sent.\n'
    instruction = 'Look for email invite from PaperTrail Dev '
    if users.status_code!=200:
        log='PaperTrail-dev error: '+str(users.status_code)+str(users.content)+'\n'
        instruction=log
        print(log)
    return user_provision.getJsonResponse(plugin, email, log, instruction)

def removeUser(email,configMap):
    #get id of user, Dev

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
        print (email[:-13]+" "+getDate().strftime("%Y-%m-%d %H:%M") +' | User does not exist, invite failed.\n')

    plugin = "PaperTrail-dev"
    log = 'PaperTrail-dev: User removed from papertrail.\n'
    instruction = 'User removed from papertrail-dev."  '
    return user_provision.getJsonResponse(plugin, email, log, instruction)
