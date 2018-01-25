import boto3
import user_provision

def getUrl(configMap):
    for url in configMap['plugins']:
        if  url['name']=='aws-dev1':
            return url['url']

def getGroups(configMap):
    groupsList=[]
    for groups in configMap['plugins']:
        if  groups['name']=='aws-dev1':
            for group in groups['groups']:
                groupsList.append(group['group'])
    return groupsList

def inviteUser(email, configMap):
    username = email[:-13]

    for key in configMap['plugins']:
        if  key['name']=='aws-dev1':
            Dev1ID= key['Dev1ID']
            Dev1Secret= key['Dev1Secret']


    client = boto3.client('iam',
        aws_access_key_id=Dev1ID,
        aws_secret_access_key=Dev1Secret
    )
    createUser(username,client,configMap)


    plugin="AWS-dev1"
    log = 'AWS-dev1: '+username+' added to aws DEV1.\n'
    instruction='You have been added to signiantdev on aws contact your administrator for your password then ' \
                'follow this link '+ getUrl(configMap)+' \n ' \
                'account id: signantdev\n' \
                'IAM username: '+ username
    return user_provision.getJsonResponse(plugin,email, log, instruction)

def removeUser(email, configMap):
    #Deletes the specified IAM user. The user must not belong to any groups or have any access keys, signing certificates, or attached policies.
    for key in configMap['plugins']:
        if  key['name']=='aws-dev1':
            Dev1ID= key['Dev1ID']
            Dev1Secret= key['Dev1Secret']

    username = email[:-13]


    client = boto3.client('iam',
        aws_access_key_id=Dev1ID,
        aws_secret_access_key=Dev1Secret
    )
    deleteUser(username,client)



    plugin = "AWS-dev1"
    log = 'AWS-dev1: '+username + ' removed from signiant aws dev 1 .\n'
    instruction = username +'has been removed from signiantdev(1) on aws  '
    return user_provision.getJsonResponse(plugin,email, log, instruction)

def createUser(username, client,configMap):
    groups=getGroups(configMap)
    response = client.create_user(UserName=username)

    for group in groups:
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