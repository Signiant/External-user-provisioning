import random
import string
from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getCLIgroups
from azure.graphrbac.models.graph_error import GraphErrorException

from azure.graphrbac.models import UserCreateParameters, PasswordProfile
from azure.graphrbac import GraphRbacManagementClient
from msrestazure.azure_active_directory import UserPassCredentials

def inviteUser(email,configMap,allPermissions,plugin_tag, name):

    done = False
    userName = email.split('@', 1)[0]

    groups= getCLIgroups(configMap, plugin_tag, allPermissions)

    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            azureConfig=plugin

    log = 'Azure: ' + userName + ' added to ' + azureConfig["directory"] + '.\n'
    instruction =  inviteMessage(configMap, plugin_tag).replace("<username>", userName +"@{}".format(azureConfig["directory"]) )
    pw = 'Ab1'+''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase+string.digits, k=13))

    credentialsToken = UserPassCredentials(
        azureConfig['email'],  #new user
        azureConfig["password"],
        resource="https://graph.windows.net"
    )

    graphrbac_client = GraphRbacManagementClient(
        credentialsToken,
        azureConfig["directory"]
    )
    try:
        userParameters = UserCreateParameters(
                user_principal_name= userName +"@{}".format(azureConfig["directory"]),
                account_enabled=True,
                display_name=name,
                mail_nickname= userName,
                password_profile=PasswordProfile(
                    password=pw,
                    force_change_password_next_login=True
                )
            )

        user = graphrbac_client.users.create(userParameters)
        url=azureConfig['url']+ user.object_id

        groupIDs = []
        azureGroups = graphrbac_client.groups.list()
        for group in groups:
            for azureGroup in azureGroups:
                 if group == azureGroup.display_name:
                     groupIDs.append(azureGroup.object_id)

        for groupId in groupIDs:
                addGroup=graphrbac_client.groups.add_member(groupId, url)

        done = True

    except GraphErrorException:
        log = 'error: Azure: failed to add ' + userName + ', user already exists'
        instruction = log
        print(log)

    except:
        log = 'error: Azure: failed to add ' + userName + ', unexpected error'
        instruction = log
        print(log)

    return getJsonResponse("Azure Active Directory", email, log, instruction, done)

def removeUser(email,configMap,allPermissions, plugin_tag):

    userName = email.split('@', 1)[0]
    done = False
    cont = False
    log = plugin_tag + ': ' + userName + removalMessage(configMap, plugin_tag) + '\n'
    instruction = userName + removalMessage(configMap, plugin_tag)

    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            azureConfig=plugin

    credentialsToken = UserPassCredentials(
        azureConfig['email'],
        azureConfig["password"],
        resource="https://graph.windows.net"
    )

    graphrbac_client = GraphRbacManagementClient(
        credentialsToken,
        azureConfig["directory"]
    )

    users = graphrbac_client.users.list();
    for user in users:
        if user.user_principal_name.split('@', 1)[0].lower()== userName.lower():
            userID=user.object_id
            cont = True
            break

    if cont:
        try:
            graphrbac_client.users.delete(userID)
            done = True
        except GraphErrorException:
            log = "The user " + userName + " does not exist or one of its queried reference-property objects are not present"
            instruction = log
            print(log)
        except:
            log = 'error: Azure: failed to remove ' + userName + ', unexpected error'
            instruction = log
            print(log)
    else:
        log = "user " + userName + " is not in the group. Could not be removed"
        instruction = log
        print(log)

    return getJsonResponse("Azure Active Directory", email, log, instruction, done)