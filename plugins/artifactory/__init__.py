#return url and message
import user_provision
from plugin import getUrl, inviteMessage, removalMessage


def removeUser(email, configMap, allPermissions, plugin_tag):
    log = 'artifactory: Removed alongside AD account \n'
    instruction= removalMessage(configMap,plugin_tag)
    return user_provision.getJsonResponse(plugin_tag, email, log, instruction)

#instruct user to join using AD credentials
def inviteUser(email, configMap, allPermissions, plugin_tag):
    log = 'Artifactory: Instruction sent in email.\n'
    instruction = inviteMessage(configMap,plugin_tag)
    return user_provision.getJsonResponse(plugin_tag, email, log, instruction)



