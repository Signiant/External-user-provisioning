#return url and message
import datetime
import getpass

def getDate():
    return datetime.datetime.now()

def send_email_invite(email,configMap):
    for link in configMap['plugins']:
        if link['name'] == 'artifactory':
            return {"Plugin name": "Artifactory",
                    "Log": (email[:-13]+" "+getpass.getuser()+" "+getDate().strftime("%Y-%m-%d %H:%M") + " | Artifactory: Instruction sent in email.\n"),
                    "Instruction": "Follow link to activate your account: https://signiant.atlassian.net/wiki/spaces/DevOps/pages/436082/NPM+setup+for+Signiant+s+Artifactory+Online+Repository "}