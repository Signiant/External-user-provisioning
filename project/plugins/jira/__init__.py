import requests
import json

from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getCLIgroups

def inviteUser(email,configMap,allPermissions, plugin_tag, name):
    done = False
    username = email.split('@', 1)[0]
    instruction = ''

    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            password= plugin['password']
            user=plugin['admin']
            url=plugin['url']

    data = {
        "name": username, #username
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
    #create a user
    create = requests.post(url + '/rest/api/2/user', headers=headers, auth=(user, password), data=data)
    if create.status_code > 201:
        if create.status_code == 400:
            log = plugin_tag + ' error: User already exists. Could not create user ' + username
        elif create.status_code == 401:
            log = plugin_tag + ' error: You are not authenticated to create a user'
        elif create.status_code == 403:
            log = plugin_tag + ' error: ' + str(
                create.status_code) + '  You don\'t have permission to create the user'
        else:
            log = plugin_tag + ' error: ' + str(
                create.status_code) + ' Unexpected error. User ' + name + ' was not registered'

    else:
        data={'name': username}
        data = json.dumps(data)

        groups = getCLIgroups(configMap, plugin_tag, allPermissions)
        #add user to the group
        for group in groups:
            add=requests.post(url+'/rest/api/2/group/user?groupname='+group, auth=(user, password),headers=headers, data=data )

        if add.status_code > 201:
            if add.status_code == 400:
                log = plugin_tag + ": user " + username+ " requested an empty group name or the user already belongs to the group"
            elif add.status_code == 401:
                log = plugin_tag + ": error: You are not authenticated to complete this action"
            elif add.status_code == 403:
                log = plugin_tag + ": error: you do not have administrator permissions to add the user " + username
            elif add.status_code == 404:
                log = plugin_tag + ": the requested group " + group + " was not found or requested user " + username+ " was not found"
            else:
                log = plugin_tag + ": unexpected error. User " + username + " could not be added to the group"
        else:

            log = 'Jira: ' + username + ' added to ' + plugin_tag + '\n'
            instruction = inviteMessage(configMap, plugin_tag)
            done = True
    print(log)
    return getJsonResponse("Jira Server",email, log, instruction, done)

def removeUser(email, configMap,allPermissions, plugin_tag):
    done = False
    cont = False
    username = email.split('@', 1)[0]
    log = ''
    instruction = ''

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
    #status 200 is Returned even if no groups match the given substring
    getG= requests.get(url+"/rest/api/2/groups/picker?username=" + email.split('@', 1)[0], headers=headers,auth=(user, password))

    if getG.status_code > 200:
            log = plugin_tag + ": unexpected error while listing all the groups"
    else:
        my_json = getG.content.decode('utf8')
        data = json.loads(my_json).get('groups')
        groupList=[d['name'] for d in data]

        #Deactivating users is not enabled in the Api, users will be removed from all groups instead
        #https: // jira.atlassian.com / browse / JRASERVER - 44801
        for group in groupList:
            delete=requests.delete(url+'/rest/api/2/group/user?groupname='+group+'&username=' + username, headers=headers,auth=(user, password))
            if delete.status_code > 200:
                if delete.status_code == 400:
                    log = plugin_tag + ": user " + username + " requested an empty group name"
                elif delete.status_code == 401:
                    log = plugin_tag + ": error: You are not authenticated to complete this action"
                elif delete.status_code == 403:
                    log = plugin_tag + ": error: you do not have administrator permissions to remove the user from the group" + username
                elif delete.status_code == 404:
                    log = plugin_tag + ": the requested group " + group + " was not found or requested user " + username + " was not found"
                else:
                    log = plugin_tag + ": unexpected error. User " + username + " could not be added to the group"
            else:
                cont = True
        if cont:

            log = plugin_tag + ': ' + username + ' removed from jira.'
            instruction = username + removalMessage(configMap, plugin_tag).replace("<username>",username) + '\n'
            done = True
    print(log)
    return getJsonResponse("Jira Server", email, log, instruction, done)