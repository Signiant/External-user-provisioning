#return url and message
import user_provision

def getUrl(configMap):
    for url in configMap['plugins']:
        if  url['name']=='artifactory':
            return url['url']

def removeUser(email,configMap):
    plugin="artifactory"
    log = 'artifactory: \n'
    instruction=' '
    return user_provision.getJsonResponse(plugin,email, log, instruction)

#instruct user to join using AD credentials
def inviteUser(email,configMap,allPermissions,groups):
    plugin = "Artifactory"
    log = 'Artifactory: Instruction sent in email.\n'
    instruction = 'Follow link to activate your account using your AD username and Password:'+getUrl(configMap)
    return user_provision.getJsonResponse(plugin, email, log, instruction)

