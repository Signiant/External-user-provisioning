#return url and message
import user_provision

def removeUser(email,configMap):
    pass

#instruct user to join using AD credentials
def inviteUser(email,configMap):
    plugin = "Artifactory"
    log = 'Artifactory: Instruction sent in email.\n'
    instruction = 'Follow link to activate your account using your AD username and Password: https://signiant.atlassian.net/wiki/spaces/DevOps/pages/436082/NPM+setup+for+Signiant+s+Artifactory+Online+Repository '
    return user_provision.getJsonResponse(plugin, email, log, instruction)

