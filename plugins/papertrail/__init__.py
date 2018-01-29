import requests
import json
import user_provision
import ast

# Send papertrail email invite to user
from plugin import getPermissions, getUrl, getApiToken, inviteMessage, removalMessage


def inviteUser(email,configMap,allPermissions,plugin_tag):

    rights={}
    for permission in allPermissions:
        thisPermissions=ast.literal_eval(permission) #to dictionnary
        if thisPermissions['plugin']==plugin_tag:
            del thisPermissions['plugin']
            rights=thisPermissions
            break
    if len(rights)==0:
        rights = getPermissions(configMap, plugin_tag)
        rights['user[email]'] = email

    users = requests.post(getUrl(configMap, plugin_tag)+"/invite.json",headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)}, data=rights)

    log = plugin_tag+': Email invite from papertrail sent.\n'
    instruction = inviteMessage(configMap,plugin_tag)
    if users.status_code!=200:
        log=plugin_tag+' error: '+str(users.status_code)+str(users.content)+' Make sure if email doesn\'t exist already.\n'
        instruction=log
        print(log)
    return user_provision.getJsonResponse( plugin_tag, email, log, instruction)

def removeUser(email,configMap,allPermissions, plugin_tag):
    #get id of user
    users = requests.get(getUrl(configMap, plugin_tag)+".json",
                         headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)})
    my_json = users.content.decode('utf8')
    data = json.loads(my_json)
    for element in data:
        if element['email']==email:
            id=element['id']

    log = plugin_tag+': User removed from papertrail.\n'
    instruction = removalMessage(configMap,plugin_tag)
    try:
        users = requests.delete(getUrl(configMap, plugin_tag)+"/"+str(id)+".json",
                                headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)})
        #print(users.status_code)
    except (UnboundLocalError):
        log=plugin_tag+' user does not exist, delete failed.\n'


    return user_provision.getJsonResponse(plugin_tag, email, log, instruction)
