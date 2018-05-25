from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage


def removeUser(email, configMap, allPermissions, plugin_tag):
    log = 'artifactory: '+ email+' removed alongside AD account \n'
    instruction= email.split('@', 1)[0] + removalMessage(configMap,plugin_tag)
    return getJsonResponse('Artifactory', email, log, instruction)


def inviteUser(email, configMap, allPermissions, plugin_tag, name):
    log = 'Artifactory: Instruction sent in email.\n'
    instruction = inviteMessage(configMap,plugin_tag)
    return getJsonResponse('Artifactory', email, log, instruction)



