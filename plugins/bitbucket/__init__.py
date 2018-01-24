import json
import requests
import user_provision

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
     data = {'grant_type': 'client_credentials'}
     credential = requests.post("https://bitbucket.org/site/oauth2/access_token", auth=(getKey(configMap),getSecret(configMap)), data=data)
     my_json = credential.content.decode('utf8')
     data = json.loads(my_json)
     access_token=data.get('access_token')

     #Invite
     invGroup= requests.put("https://api.bitbucket.org/1.0/users/signiant/invitations/"+email+"/signiant/developers"+"?access_token="+access_token)

     plugin = "BitBucket"
     log = 'BitBucket: Email invite sent.\n'
     instruction = 'Look for email invite from BitBucket '
     return user_provision.getJsonResponse(plugin, email, log, instruction)

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
     plugin = "BitBucket"
     log = 'BitBucket: User removed from signiant team.\n'
     instruction = 'User removed from signiant team."  '
     return user_provision.getJsonResponse(plugin, email, log, instruction)

