import requests
import json
import ast
from project.user_provision import getJsonResponse
from project.plugin import getPermissions, getUrl, getApiToken, inviteMessage, removalMessage

done = False

def done(self):
    return self._done

def inviteUser(email,configMap,allPermissions,plugin_tag, name):

    global done

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

    if users.status_code!=200:
        if users.status_code == 401:
          log=plugin_tag+' error: Invalid Papertrail api key entered.'
          instruction=log
        else:
          log = plugin_tag + ' The user already exists'
          instruction = log
          print(log)


    else:
        log = plugin_tag + ': Email invite sent from Papertrail.\n'
        instruction = inviteMessage(configMap, plugin_tag)
        done = True

    return getJsonResponse( 'Papertrail ' + plugin_tag[11:], email, log, instruction)



def removeUser(email,configMap,allPermissions, plugin_tag):

    global done

    users = requests.get(getUrl(configMap, plugin_tag)+".json",
                         headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)})

    if users.status_code!=200:
        if users.status_code == 401:
          log=plugin_tag+' error: Invalid Papertrail api key entered.\n'
          instruction=log

    else:
     my_json = users.content.decode('utf8')
     data = json.loads(my_json)

     for element in data:
         if element['email']==email:
             id=element['id']

     try:

         requests.delete(getUrl(configMap, plugin_tag)+"/"+str(id)+".json",
                                 headers={'X-Papertrail-Token': getApiToken(configMap, plugin_tag)})

         log = plugin_tag + ': ' + email + ' has been removed from Papertrail.\n'
         instruction = log
         done = True

     except (UnboundLocalError):
         log=plugin_tag+' '+ email+' does not exist, delete failed'
         instruction = log
         print(log)


    return getJsonResponse('Papertrail ' + plugin_tag[11:], email, log, instruction)
