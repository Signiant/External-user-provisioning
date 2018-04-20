import ast
import json
import requests
from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getGroups


def getKey(configMap):
     for config_key in configMap['plugins']:
          if config_key['plugin']+':'+config_key['tag']  == 'bitbucket:prod':
               return  config_key['key']

def getSecret(configMap):
     for config_key in configMap['plugins']:
          if config_key['plugin']+':'+config_key['tag'] == 'bitbucket:prod':
               return config_key['secret']


def inviteUser(email,configMap,allPermissions, plugin_tag, name):

     #Get Authorization token
     data = {'grant_type': 'client_credentials'}
     credential = requests.post("https://bitbucket.org/site/oauth2/access_token", auth=(getKey(configMap),getSecret(configMap)), data=data)
     my_json = credential.content.decode('utf8')
     data = json.loads(my_json)
     access_token=data.get('access_token')

     cli_groups = []
     for permission in allPermissions:
         thisPermissions = ast.literal_eval(permission)
         if thisPermissions['plugin'] == plugin_tag:
             del thisPermissions['plugin']
             cli_groups = list(thisPermissions.values())
             break

     if len(cli_groups) == 0:
         cli_groups = getGroups(configMap,plugin_tag)

     for group in cli_groups:
         invGroup = requests.put(
             "https://api.bitbucket.org/1.0/users/"+configMap['global']['organization']+"/invitations/"
             + email + "/"+configMap['global']['organization']+"/"+group+ "?access_token=" + access_token)


     log = 'BitBucket: Email invite sent from Bitbucket.\n'
     instruction = inviteMessage(configMap,plugin_tag)
     return getJsonResponse('Bitbucket', email, log, instruction)

def removeUser(email,configMap,allPermissions, plugin_tag):
     #Get Authorization token
     key=getKey(configMap)
     data = {'grant_type': 'client_credentials'}
     credential = requests.post("https://bitbucket.org/site/oauth2/access_token", auth=(getKey(configMap),getSecret(configMap)), data=data)
     my_json = credential.content.decode('utf8')
     data = json.loads(my_json)
     access_token=data.get('access_token')

     #get all groups
     groups=requests.get("https://api.bitbucket.org/1.0/groups/"+configMap['global']['organization']+"?access_token="+access_token)
     my_json=groups.content.decode('utf8')
     data = json.loads(my_json)

     # Remove from groups
     for group in data:
         delMem= requests.delete("https://api.bitbucket.org/1.0/groups/"+configMap['global']['organization']+"/"+group.get('name').lower()+"/members/"+email+"?access_token="+access_token)

     log = 'BitBucket: '+email+' removed from team.\n'
     instruction = email[:-13]+ removalMessage(configMap,plugin_tag)
     return getJsonResponse('Bitbucket', email, log, instruction)

