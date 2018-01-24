#return url and message
import datetime
import getpass
import json

import requests


def getApiToken(configMap):
    for apiToken in configMap['plugins']:
        if apiToken['name'] == 'slack':
            return apiToken['ApiToken']

def getDate():
    return datetime.datetime.now()

def send_email_invite(email,configMap):
    for link in configMap['plugins']:
        if link['name'] == 'slack':
            return {"Plugin name": "Slack",
                    "Log": (getpass.getuser()+" "+getDate().strftime("%Y-%m-%d %H:%M") + " | Slack: Instruction sent in email.\n"),
                    "Instruction": "Follow link to activate your account: https://signiant-dev.slack.com/signup "}

def deleteUser(email,configMap): #removes user as a member of dev-signiant

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
   # user = requests.post("https://slack.com/api/users.admin.setInactive" + "?token=" + getApiToken(configMap) + "&user="+slackUserID)

    return {"Plugin name": "Slack",
            "Log": (getpass.getuser() + " " + getDate().strftime(
                "%Y-%m-%d %H:%M") + " | Slack: User removed from dev-signiant\n"),
            "Instruction": "User removed from dev-signiant"}