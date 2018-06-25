import json
import requests
from project.user_provision import getJsonResponse
from project.plugin import getApiToken, inviteMessage, removalMessage


def inviteUser(email,configMap,allPermissions, plugin_tag, name):

    log = 'Slack: Instruction sent in email.\n'
    instruction = inviteMessage(configMap,plugin_tag)
    done = True
    return getJsonResponse('Slack', email, log, instruction, done)

def removeUser(email,configMap,allPermissions, plugin_tag):
    instruction = ''
    log = ''
    done = False
    userName = email.split('@', 1)[0]
    #get team id
    team = requests.get("https://slack.com/api/team.info?token=" + getApiToken(configMap,plugin_tag) )
    my_json = team.content.decode('utf8')
    data = json.loads(my_json)

    if 'error' in data:
        if 'invalid_auth' in team.text:
            log = plugin_tag + ' error: for user: ' + userName + '. Wrong api token'

        if 'not_authed' in team.text:
            log = plugin_tag + ' error: for user: ' + userName + '. No api token provided'

        if 'fatal_error' in team.text:
            log = plugin_tag + ' unexpected error: for user: ' + userName + '. could not be removed'

    elif 'team' not in data:
        log = plugin_tag + ' error: for user: ' + userName + '. Is not in the team'
    else:
        teamId=data['team']['id']

        #get user id
        userId= requests.get("https://slack.com/api/auth.findUser?token=" + getApiToken(configMap,plugin_tag)+"&email="+email+"&team="+teamId )
        if 'user_not_found' in userId.text:
            log = plugin_tag + ' error: for user: ' + userName + ' was not found. Delete failed. '
            print(log)
        else:
            my_json = userId.content.decode('utf8')
            data = json.loads(my_json)
            slackUserID = data['user_id']
            try:
            #disable user
                user = requests.post("https://slack.com/api/users.admin.setInactive" + "?token=" + getApiToken(configMap,plugin_tag) + "&user="+slackUserID)
                log = plugin_tag + ": username " + userName + " has been deactivated\n"
                instruction = log
                print(log)
                done = True
            except Exception as error:
                log = 'Slack: Remove from slack error: '+ userName+' could not be removed'
                instruction =  email+' was not found or is already inactive.'
                print(log)

    return getJsonResponse('Slack', email, log, instruction, done)
