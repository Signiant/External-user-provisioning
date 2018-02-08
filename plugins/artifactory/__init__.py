#return url and message
from user_provision import getJsonResponse #add folder path (External-user-provisioning-new)
from plugin import getPermissions, getUrl, getApiToken, inviteMessage, removalMessage


def removeUser(email, configMap, allPermissions, plugin_tag):
    log = 'artifactory: '+ email+' removed alongside AD account \n'
    instruction= email+ removalMessage(configMap,plugin_tag)
    return getJsonResponse('Artifactory', email, log, instruction)

#instruct user to join using AD credentials
def inviteUser(email, configMap, allPermissions, plugin_tag, name):
    log = 'Artifactory: Instruction sent in email.\n'
    instruction = inviteMessage(configMap,plugin_tag)
    return getJsonResponse('Artifactory', email, log, instruction)



