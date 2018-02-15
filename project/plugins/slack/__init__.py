import json
import requests
from project.user_provision import getJsonResponse
from project.plugin import getApiToken, inviteMessage, removalMessage


def inviteUser(email,configMap,allPermissions, plugin_tag, name):

    log = 'Slack: Instruction sent in email.\n'
    instruction = inviteMessage(configMap,plugin_tag)
    return getJsonResponse('Slack', email, log, instruction)

def removeUser(email,configMap,allPermissions, plugin_tag):
    #get team id
    team = requests.get("https://slack.com/api/team.info?token=" + getApiToken(configMap,plugin_tag) )
    my_json = team.content.decode('utf8')
    data = json.loads(my_json)
    teamId=data['team']['id']

    log = "Slack: "+email[:-13]+" was removed from Slack.\n"
    instruction = email[:-13] + removalMessage(configMap,plugin_tag)
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
        instruction =  email+' was not found or is already inactive.'

    return getJsonResponse('Slack', email, log, instruction)
