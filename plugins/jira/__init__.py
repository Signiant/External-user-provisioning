import ast

import requests
import json

import user_provision
from plugin import getGroups, inviteMessage, getCLIgroups, removalMessage


def inviteUser(email,configMap,allPermissions, plugin_tag):

    #Authentication
    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            password= plugin['password']
            user=plugin['admin']
    #new user fields
    data = {
        "name": email[:-13], #username
        "password": "test",
        "emailAddress": email,
        "displayName": configMap['global']['full name'],
        "applicationKeys": [
            "jira-server"
        ]
    }
    data=json.dumps(data)

    headers = {'Accept':'application/json',
               'Content-Type': 'application/json'
               }
    #create user
    create=requests.post('http://ott-jira.ott.signiant.com:8080/rest/api/2/user', headers=headers,auth=(user, password), data=data)
    print(create)
    data={'name': email[:-13]}
    data = json.dumps(data)

    #add to groups
    groups = getCLIgroups(configMap, plugin_tag, allPermissions)
    for group in groups:
        add=requests.post('http://ott-jira.ott.signiant.com:8080/rest/api/2/group/user?groupname='+group, auth=(user, password),headers=headers, data=data )
        print(add)

    log = plugin_tag + ': ' + email[:-13] + ' added to ' + plugin_tag + '\n'
    instruction = inviteMessage(configMap, plugin_tag)
    return user_provision.getJsonResponse("Jira Server",email, log, instruction)

def removeUser(email, configMap,allPermissions, plugin_tag):

    # Authentication
    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            password = plugin['password']
            user = plugin['admin']
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json'
               }

    delete=requests.delete('http://ott-jira.ott.signiant.com:8080/rest/api/2/user?username='+email[:-13] , headers=headers,auth=(user, password))

    log = plugin_tag + ': ' + email[:-13] + ' removed from jira.\n'
    instruction = email + removalMessage(configMap, plugin_tag)
    return user_provision.getJsonResponse("Jira Server", email, log, instruction)