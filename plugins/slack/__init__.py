import json
import requests
from user_provision import getJsonResponse #add folder path (External-user-provisioning-new)
from plugin import getPermissions, getUrl, getApiToken, inviteMessage, removalMessage, getGroups, getCLIgroups

def inviteUser(email,configMap,allPermissions, plugin_tag, name):

    log = 'Slack: Instruction sent in email.\n'
    instruction = inviteMessage(configMap,plugin_tag)
    return getJsonResponse('Slack', email, log, instruction)

def removeUser(email,configMap,allPermissions, plugin_tag): #removes user as a member of dev-signiant
    #get team id
    team = requests.get("https://slack.com/api/team.info?token=" + getApiToken(configMap,plugin_tag) )
    my_json = team.content.decode('utf8')
    data = json.loads(my_json)
    teamId=data['team']['id']

    log = "Slack: "+email+" removed from Slack.\n"
    instruction = email + removalMessage(configMap,plugin_tag)
    try:
        #get user id
        userId= requests.get(	"https://slack.com/api/auth.findUser?token=" + getApiToken(configMap,plugin_tag)+"&email="+email+"&team="+teamId )
        my_json = userId.content.decode('utf8')
        data = json.loads(my_json)
        slackUserID = data['user_id']

        #disable user
        user = requests.post("https://slack.com/api/users.admin.setInactive" + "?token=" + getApiToken(configMap,plugin_tag) + "&user="+slackUserID)
    except Exception as error:
        log = 'Slack: Remove from slack error: '+ email+' does not exist or is already inactive\n error: '+ str(error) +'\n'
        instruction = 'Remove from slack error: '+ email+' does not exist or is already inactive. Exception caught: '+ str(error)

    return getJsonResponse('Slack', email, log, instruction)