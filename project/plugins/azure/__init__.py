import random
import string
from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getCLIgroups
from azure.graphrbac.models.graph_error import GraphErrorException

from azure.graphrbac.models import UserCreateParameters, PasswordProfile
from azure.graphrbac import GraphRbacManagementClient
import azure.common.credentials
from azure.common.credentials import ServicePrincipalCredentials


def getCredentials(configMap, plugin_tag):

    azureConfig = azure_in_config(configMap, plugin_tag)

    if azureConfig is None:
        print("Plugin azure is missing from you config file")
        return None
    else:

        TENANT_ID = azureConfig["tenant_id"]
        CLIENT = azureConfig["client"]
        KEY = azureConfig["client_secret"]

        credentialsToken = ServicePrincipalCredentials(
            client_id=CLIENT,
            secret=KEY,
            tenant=TENANT_ID,
            resource = "https://graph.windows.net"
        )

        return credentialsToken

def azure_in_config(configMap, plugin_tag):


    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            azureConfig=plugin
            return azureConfig

    return None


def get_graphrbac_client(configMap, plugin_tag):

    try:
        credentials = getCredentials(configMap, plugin_tag)
    except Exception:
        print("Azure credentials are missing from config file or invalid")
        return None

    directory = azure_in_config(configMap, plugin_tag)["directory"]

    graphrbac_client = GraphRbacManagementClient(
        credentials,
        directory
    )
    return graphrbac_client


def inviteUser(email,configMap,allPermissions,plugin_tag, name):

    done = False
    userName = email.split('@', 1)[0]
    azureConfig = azure_in_config(configMap, plugin_tag)

    groups= getCLIgroups(configMap, plugin_tag, allPermissions)

    log = 'Azure: ' + userName + ' added to ' + azureConfig["directory"] + '.\n'
    instruction =  inviteMessage(configMap, plugin_tag).replace("<username>", userName +"@{}".format(azureConfig["directory"]) )
    pw = 'Ab1'+''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase+string.digits, k=13))

    graphrbac_client = get_graphrbac_client(configMap, plugin_tag)

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
                graphrbac_client.groups.add_member(groupId, url)

        done = True

    except GraphErrorException as e:
            log = "User " + userName + " could not be added: " + str(e)
            instruction = log
            print(log)
    except:
        log = 'error: Azure: failed to add ' + userName + ', unexpected error'
        instruction = log
        print(log)

    return getJsonResponse("Azure Active Directory", email, log, instruction, done)

def removeUser(email,configMap,allPermissions, plugin_tag):

    userName = email.split('@', 1)[0]
    userID = None
    done = False
    cont = False
    log = plugin_tag + ': ' + userName + removalMessage(configMap, plugin_tag) + '\n'
    instruction = userName + removalMessage(configMap, plugin_tag)

    graphrbac_client = get_graphrbac_client(configMap, plugin_tag)

    users = graphrbac_client.users.list()

    for user in users:
        if user.user_principal_name.split('@', 1)[0].lower()== userName.lower():
            userID=user.object_id
            cont = True
            break

    if cont:
        try:
            graphrbac_client.users.delete(userID)
            done = True

        except GraphErrorException as e:
            log = "User " + userName + " could not be removed: " + str(e)
            instruction = log
            print(log)
        except:
            log = 'error: Azure: failed to remove ' + userName + ', unexpected error'
            instruction = log
            print(log)
    else:
        log = "user " + userName + " is not in the group or does not exist at all. Could not be removed"
        instruction = log
        print(log)

    return getJsonResponse("Azure Active Directory", email, log, instruction, done)