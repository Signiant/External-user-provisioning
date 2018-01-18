# def inviteUser(email,configMap):
#     rights = {'user[email]': email,'user[read_only]': 1,'user[purge_logs]': 0}
#     # Send invite to user
#     users = requests.post("https://papertrailapp.com/api/v1/users/invite.json",headers={'X-Papertrail-Token': getApiToken(configMap)}, data=rights)
#     print(users.status_code+': User succesfully invited.')

#"http://localhost:7990/bitbucket/rest/api/1.0/admin/users?name=<USERNAME_TO_ADD>&password=<PASSWORD_FOR_USER>&displayName=<DISPLAY_NAME_FOR_USER>&emailAddress=<EMAIL_ADDRESS_FOR_USER>&addToDefualtGroup=true&notify=false"


#To add a member with the username brao to the group developers:
#curl --request PUT --user username:password --header "Content-Type: application/json" https://api.bitbucket.org/1.0/groups/username/developers/members/brao/ --data '{}'


#PUT https://api.bitbucket.org/1.0/users/{accountname}/invitations/{email_address}/{group_owner}/{group_slug}

import json
import requests


def inviteUser():
     #users = requests.put("https://api.bitbucket.org/1.0/users/signiant/invitations/test@signiant.com/signiant/developers")
     users = requests.get("https://api.bitbucket.org/1.0/users/signiant/invitations/test@signiant.com/signiant/developers")

     print(users.status_code)