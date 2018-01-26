import boto3
import user_provision


def getUrl(configMap):
    for url in configMap['plugins']:
        if  url['name']=='aws-dev1':
            return url['url']

def getGroups(configMap):
    groupsList=[]
    for groups in configMap['plugins']:
        if  groups['name']=='aws-dev2':
            for group in groups['groups']:
                groupsList.append(group['group'])
    return groupsList

def inviteUser(email, configMap,allPermissions,groups):
    username = email[:-13]

    cli_groups = []
    for plugin_groups in groups:
        group = [x.strip() for x in plugin_groups.split(':')]
        if group[0] == 'aws-dev2':
            cli_groups = [x.strip() for x in group[1].split(',')]
            break
    if len(cli_groups) == 0:
        cli_groups = getGroups(configMap)

    for key in configMap['plugins']:
        if  key['name']=='aws-dev2':
            Dev2ID= key['Dev2ID']
            Dev2Secret= key['Dev2Secret']


    client = boto3.client('iam',
        aws_access_key_id=Dev2ID,
        aws_secret_access_key=Dev2Secret
    )
    createUser(username,client,configMap,cli_groups)

    plugin = "AWS-dev2"
    log = 'AWS-dev2: ' + username + ' added to aws DEV2.\n'
    instruction = 'You have been added to signiantdev2 on aws contact your administrator for your password then ' \
                  'follow this link '+ getUrl(configMap)+' \n ' \
                  'account id: signiantdev2 \n' \
                  'IAM username: ' + username
    return user_provision.getJsonResponse(plugin, email, log, instruction)

def removeUser(email, configMap):
    #Deletes the specified IAM user. The user must not belong to any groups or have any access keys, signing certificates, or attached policies.
    for key in configMap['plugins']:
        if  key['name']=='aws-dev2':

            Dev2ID= key['Dev2ID']
            Dev2Secret= key['Dev2Secret']

    username = email[:-13]

    client = boto3.client('iam',
        aws_access_key_id=Dev2ID,
        aws_secret_access_key=Dev2Secret
    )
    deleteUser(username,client)
    plugin = "AWS-dev2"
    log = 'AWS-dev2: ' + username + ' removed from signiant aws dev 2.\n'
    instruction = username + ' has been removed from signiantdev2 on aws  '
    return user_provision.getJsonResponse(plugin, email, log, instruction)

def createUser(username, client,configMap,cli_groups):
    response = client.create_user(UserName=username)

    for group in cli_groups:
        response = client.add_user_to_group(
            GroupName=group,
            UserName=username
        )


def deleteUser(username, client):
    # remove from groups
    response = client.list_groups_for_user(UserName=username)
    groups = response.get('Groups')
    for group in groups:
        response = client.remove_user_from_group(GroupName=group.get('GroupName'), UserName=username)

    # remove access keys
    response = client.list_access_keys(UserName=username)
    keys = response.get('AccessKeyMetadata')
    for key in keys:
        response = client.delete_access_key(
            UserName=username,
            AccessKeyId=key.get('AccessKeyId')
        )
    # delete login profile
    try:
        response = client.delete_login_profile(UserName=username)
    except:
        print('')

    response = client.delete_user(UserName=username)