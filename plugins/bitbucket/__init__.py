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
import datetime,getpass

def getDate():
    return datetime.datetime.now()

def getKey(configMap):
     for config_key in configMap['plugins']:
          if config_key['name'] == 'bitbucket':
               return  config_key['key']

def getSecret(configMap):
     for config_key in configMap['plugins']:
          if config_key['name'] == 'bitbucket':
               return config_key['secret']


def inviteUser(email,configMap):

     #Get Authorization token
     # data = {'grant_type': 'client_credentials'}
     # credential = requests.post("https://bitbucket.org/site/oauth2/access_token", auth=(getKey(configMap),getSecret(configMap)), data=data)
     # my_json = credential.content.decode('utf8')
     # data = json.loads(my_json)
     # access_token=data.get('access_token')
     # print(credential.status_code)
     #
     #Invite
     # invGroup= requests.put("https://api.bitbucket.org/1.0/users/signiant/invitations/"+email+"/signiant/developers"+"?access_token="+access_token)
     # print(invGroup.status_code)

     return {"Plugin name": "BitBucket",
             "Log": (email[:-13]+" "+getpass.getuser()+" "+getDate().strftime("%Y-%m-%d %H:%M")+" | BitBucket: Email invite sent. \n"),
             "Instruction":"Look for email invite from BitBucket"}

def removeUser(email,configMap):
     #Get Authorization token
     data = {'grant_type': 'client_credentials'}
     credential = requests.post("https://bitbucket.org/site/oauth2/access_token", auth=(getKey(configMap),getSecret(configMap)), data=data)
     my_json = credential.content.decode('utf8')
     data = json.loads(my_json)
     access_token=data.get('access_token')
     print(credential.status_code)

     #Remove from groups
     # delMem= requests.delete("https://api.bitbucket.org/1.0/groups/signiant/developers/members/"+email+"?access_token="+access_token)
     # print(delMem.status_code)
     # delMem = requests.delete(
     #      "https://api.bitbucket.org/1.0/groups/signiant/administrators/members/"+email+ "?access_token=" + access_token)
     # print(delMem.status_code)
     # delMem = requests.delete(
     #      "https://api.bitbucket.org/1.0/groups/signiant/documentation/members/"+email+"?access_token=" + access_token)
     # print(delMem.status_code)

     return {"Plugin name": "BitBucket",
             "Log": (email[:-13]+" "+getpass.getuser() + " " + getDate().strftime(
                  "%Y-%m-%d %H:%M") + " | BitBucket: User removed from signiant team. \n"),
             "Instruction": "User removed from signiant team."}