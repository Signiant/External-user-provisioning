import requests
import json

from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getCLIgroups


def inviteUser(email,configMap,allPermissions, plugin_tag, name):

    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            password= plugin['password']
            user=plugin['admin']
            url=plugin['url']

    data = {
        "name": email[:-13], #username
        "password": "test",
        "emailAddress": email,
        "displayName": name,
        "applicationKeys": [
            "jira-server"
        ]
    }
    data=json.dumps(data)

    headers = {'Accept':'application/json',
               'Content-Type': 'application/json'
               }
    create=requests.post(url+'/rest/api/2/user', headers=headers,auth=(user, password), data=data)
    data={'name': email[:-13]}
    data = json.dumps(data)

    groups = getCLIgroups(configMap, plugin_tag, allPermissions)
    for group in groups:
        add=requests.post(url+'/rest/api/2/group/user?groupname='+group, auth=(user, password),headers=headers, data=data )

    log = 'Jira: ' + email[:-13] + ' added to ' + plugin_tag + '\n'
    instruction = inviteMessage(configMap, plugin_tag)
    return getJsonResponse("Jira Server",email, log, instruction)

def removeUser(email, configMap,allPermissions, plugin_tag):

    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            password = plugin['password']
            user = plugin['admin']
            url=plugin['url']

    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json'
               }

    #listing user groups returns empty array. Getting all org groups instead.
    # https://docs.atlassian.com/software/jira/docs/api/REST/7.6.1/#api/2/user-getUser
    #get = requests.get(url+"/rest/api/2/user?username=" +email[:-13], headers=headers,auth=(user, password))

    #list org groups
    getG= requests.get(url+"/rest/api/2/groups/picker?username=" +email[:-13], headers=headers,auth=(user, password))
    my_json = getG.content.decode('utf8')
    data = json.loads(my_json).get('groups')
    groupList=[d['name'] for d in data]


    #Deactivating users is not enabled in the Api, users will be removed from all groups instead
    #https: // jira.atlassian.com / browse / JRASERVER - 44801
    for group in groupList:
        delete=requests.delete(url+'/rest/api/2/group/user?groupname='+group+'&username=' +email[:-13], headers=headers,auth=(user, password))

    log = plugin_tag + ': ' + email[:-13] + ' removed from jira.\n'
    instruction = email[:-13] + removalMessage(configMap, plugin_tag).replace("<username>",email[:-13])
    return getJsonResponse("Jira Server", email, log, instruction)