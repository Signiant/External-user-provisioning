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

def getGroups(configMap):
    groupsList=[]
    for groups in configMap['plugins']:
        if  groups['name']=='bitbucket':
            for group in groups['groups']:
                groupsList.append(group['group'])
    return groupsList

def inviteUser(email,configMap,allPermissions,groups):

     #Get Authorization token
     data = {'grant_type': 'client_credentials'}
     credential = requests.post("https://bitbucket.org/site/oauth2/access_token", auth=(getKey(configMap),getSecret(configMap)), data=data)
     my_json = credential.content.decode('utf8')
     data = json.loads(my_json)
     access_token=data.get('access_token')

     #Invite
     cli_groups = []
     for plugin_groups in groups:
         group = [x.strip() for x in plugin_groups.split(':')]
         if group[0] == 'bitbucket':
             cli_groups = [x.strip() for x in group[1].split(',')]
             break
     if len(cli_groups) == 0:
         cli_groups = getGroups(configMap)
     for group in cli_groups:
         invGroup = requests.put(
             "https://api.bitbucket.org/1.0/users/signiant/invitations/" + email + "/signiant/"+group+ "?access_token=" + access_token)

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
     delMem= requests.delete("https://api.bitbucket.org/1.0/groups/signiant/developers/members/"+email+"?access_token="+access_token)
     delMem = requests.delete(
          "https://api.bitbucket.org/1.0/groups/signiant/administrators/members/"+email+ "?access_token=" + access_token)
     delMem = requests.delete(
          "https://api.bitbucket.org/1.0/groups/signiant/documentation/members/"+email+"?access_token=" + access_token)
     plugin = "BitBucket"
     log = 'BitBucket: User removed from signiant team.\n'
     instruction = 'User removed from bitbucket signiant team.  '
     return user_provision.getJsonResponse(plugin, email, log, instruction)

