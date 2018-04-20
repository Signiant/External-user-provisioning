import random
import string
from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getCLIgroups

from azure.graphrbac.models import UserCreateParameters, PasswordProfile
from azure.graphrbac import GraphRbacManagementClient
from msrestazure.azure_active_directory import UserPassCredentials

def inviteUser(email,configMap,allPermissions,plugin_tag, name):

    groups= getCLIgroups(configMap, plugin_tag, allPermissions)

    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            azureConfig=plugin

    log = 'Azure: ' + email[:-13] + ' added to ' + azureConfig["directory"] + '.\n'
    instruction =  inviteMessage(configMap, plugin_tag).replace("<username>",email[:-13]+"@{}".format(azureConfig["directory"]) )
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
        user = graphrbac_client.users.create(
            UserCreateParameters(
                user_principal_name=email[:-13]+"@{}".format(azureConfig["directory"]),
                account_enabled=True,
                display_name=name,
                mail_nickname=email[:-13],
                password_profile=PasswordProfile(
                    password=pw,
                    force_change_password_next_login=True
                )
            )
        )

        url=azureConfig['url']+ user.object_id

        groupIDs = []
        azureGroups = graphrbac_client.groups.list()
        for group in groups:
            for azureGroup in azureGroups:
                if group == azureGroup.display_name:
                    groupIDs.append(azureGroup.object_id)

        for groupId in groupIDs:
            addGroup=graphrbac_client.groups.add_member(groupId, url)
    except:
        log = 'Azure: failed to add, ' + email + ', user already exists  .\n'
        instruction = email + ' already exists.'

    return getJsonResponse("Azure Active Directory", email, log, instruction)

def removeUser(email,configMap,allPermissions, plugin_tag):
    log = plugin_tag + ': ' + email[:-13] + removalMessage(configMap, plugin_tag) + '\n'
    instruction = email[:-13] + removalMessage(configMap, plugin_tag)

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
        if user.user_principal_name[:-29]== email[:-13]:
            userID=user.object_id
            break
    try:
        graphrbac_client.users.delete(userID)
    except:
        log = plugin_tag + ': ' + email[:-13] +  ' does not exist in Azure AD\n'
        instruction = email[:-13] + ' does not exist in Azure AD'
    return getJsonResponse("Azure Active Directory", email, log, instruction)

