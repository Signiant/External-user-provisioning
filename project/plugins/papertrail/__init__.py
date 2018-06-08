import requests
import json
import ast
from project.user_provision import getJsonResponse
from project.plugin import getPermissions, getUrl, getApiToken, inviteMessage, removalMessage

def inviteUser(email,configMap,allPermissions,plugin_tag, name):

    done = False
    log = None
    instruction = None
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

    # If we get a value back from errorCheck, there was an error
    # If it comes back as None, everything worked
    log = errorCheck(users, plugin_tag)

    if log:
        print(log)
        instruction = log
    else:
        instruction = inviteMessage(configMap, plugin_tag)

        if instruction:
            log = plugin_tag + ': Email invite sent to ' + name + ' from Papertrail.\n'
            done = True
        else:
            log = "Error: invitation message was not sent"

    return getJsonResponse( 'Papertrail ' + plugin_tag[11:], email, log, instruction, done)

def removeUser(email,configMap,allPermissions, plugin_tag):

    done = False
    log = None
    instruction = None

    users = requests.get(getUrl(configMap, plugin_tag)+".json", headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)})

    # If we get a value back from errorCheck, there was an error
    # If it comes back as None, everything worked
    log = errorCheck(users, plugin_tag)

    if log :
        print(log)
        instruction = log
    else:
        my_json = users.content.decode('utf8')
        data = json.loads(my_json)

        for element in data:
             if element['email'].lower()==email.lower():
                 id=element['id']

        try:
            req = requests.delete(getUrl(configMap, plugin_tag)+"/"+str(id)+".json", headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)})

            log = errorCheck(req, plugin_tag)
            instruction = log

            if log:
                print(log)
                instruction = log
            else:
                log = plugin_tag + ': ' + email + ' has been removed from Papertrail.\n'
                instruction = log
                done = True

        except (UnboundLocalError):
             log=plugin_tag+' '+ email+' does not exist, delete failed'
             instruction = log
             print(log)

    return getJsonResponse('Papertrail ' + plugin_tag[11:], email, log, instruction, done)


def errorCheck(response, plugin_tag):

    log = None

    if response.status_code != 200:
        if response.status_code == 401:
            log = plugin_tag + ' error: Invalid Papertrail api key entered'
        else:
            log = plugin_tag + ' error: ' + str(response.status_code)  + ' Make sure if email doesn\'t exist already '

    return log