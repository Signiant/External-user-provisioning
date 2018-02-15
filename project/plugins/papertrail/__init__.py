import requests
import json
import ast
from project.user_provision import getJsonResponse
from project.plugin import getPermissions, getUrl, getApiToken, inviteMessage, removalMessage


def inviteUser(email,configMap,allPermissions,plugin_tag, name):

    rights={}
    for permission in allPermissions:
        thisPermissions=ast.literal_eval(permission)
        if thisPermissions['plugin']==plugin_tag:
            del thisPermissions['plugin']
            rights=thisPermissions
            break
    if len(rights)==0:
        rights = getPermissions(configMap, plugin_tag)
        rights['user[email]'] = email

    users = requests.post(getUrl(configMap, plugin_tag)+"/invite.json",headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)}, data=rights)

    log = plugin_tag+': Email invite sent from Papertrail.\n'
    instruction = inviteMessage(configMap,plugin_tag)
    if users.status_code!=200:
        log=plugin_tag+' error: '+str(users.status_code)+str(users.content)+' Make sure if email doesn\'t exist already.\n'
        instruction=log
    return getJsonResponse( 'Papertrail ' + plugin_tag[11:], email, log, instruction)

def removeUser(email,configMap,allPermissions, plugin_tag):

    users = requests.get(getUrl(configMap, plugin_tag)+".json",
                         headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)})
    my_json = users.content.decode('utf8')
    data = json.loads(my_json)
    for element in data:
        if element['email']==email:
            id=element['id']

    log = plugin_tag+': '+email+' removed from papertrail.\n'
    instruction = email[:-13]+ removalMessage(configMap,plugin_tag)
    try:
        users = requests.delete(getUrl(configMap, plugin_tag)+"/"+str(id)+".json",
                                headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)})
    except (UnboundLocalError):
        log=plugin_tag+' '+ email+' does not exist, delete failed.\n'


    return getJsonResponse('Papertrail ' + plugin_tag[11:], email, log, instruction)
