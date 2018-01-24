import json
import requests
import user_provision

def getApiToken(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'slack':
            return apiToken['ApiToken']


def inviteUser(email,configMap):
    plugin = "Slack"
    log = 'Slack: Instruction sent in email.\n'
    instruction = 'Follow link to activate your account using your AD username and password: https://signiant-dev.slack.com/signup '
    return user_provision.getJsonResponse(plugin, email, log, instruction)

def removeUser(email,configMap): #removes user as a member of dev-signiant

    #get team id
    team = requests.get("https://slack.com/api/team.info?token=" + getApiToken(configMap) )
    my_json = team.content.decode('utf8')
    data = json.loads(my_json)
    teamId=data['team']['id']

    #get user id
    userId= requests.get(	"https://slack.com/api/auth.findUser?token=" + getApiToken(configMap)+"&email="+email+"&team="+teamId )
    my_json = userId.content.decode('utf8')
    data = json.loads(my_json)
    slackUserID = data['user_id']

    #disable user
    user = requests.post("https://slack.com/api/users.admin.setInactive" + "?token=" + getApiToken(configMap) + "&user="+slackUserID)

    plugin = "Slack"
    log = 'Slack: User removed from Slack dev-signiant.\n'
    instruction = 'User removed from Slack dev-signiant."  '
    return user_provision.getJsonResponse(plugin, email, log, instruction)
