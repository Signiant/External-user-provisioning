import json

import boto3
import user_provision



def inviteUser(email, configMap):

    for key in configMap['plugins']:
        if  key['name']=='aws':
            Dev1ID= key['Dev1ID']
            Dev1Secret= key['Dev1Secret']
            Dev2ID= key['Dev2ID']
            Dev2Secret= key['Dev2Secret']

    client = boto3.client( #Signiant DEV1
        'iam',
        aws_access_key_id=Dev1ID,
        aws_secret_access_key=Dev1Secret
    )
   #NO MORE client = boto3.client('iam')
    username=email[:-13] #user's email without @signiant.com
    response = client.create_user(UserName=username)
    response = client.add_user_to_group(
        GroupName='IAMChangeMyPW_ManageMyKeys',
        UserName=username
    )
    response = client.add_user_to_group(
        GroupName='SigniantDevelopers',
        UserName=username
    )

    client = boto3.client(#Signiant DEV2
        'iam',
        aws_access_key_id=Dev2ID,
        aws_secret_access_key=Dev2Secret
    )
    response = client.create_user(UserName=username)
    response = client.add_user_to_group(
        GroupName='IAMChangeMyPW_ManageMyKeys',
        UserName=username
    )
    response = client.add_user_to_group(
        GroupName='SigniantDevelopers',
        UserName=username
    )

    plugin="AWS"
    log = 'AWS: '+username+' added to aws.\n'
    instruction='You have been added to signiantdev on aws contact your administrator for your password then ' \
                'follow this link https://signiantdev.signin.aws.amazon.com/console \n ' \
                'account id: signantdev and signiantdev2 \n' \
                'IAM username: '+ username

    return user_provision.getJsonResponse(plugin,email, log, instruction)

def removeUser(email, configMap):
    #Deletes the specified IAM user. The user must not belong to any groups or have any access keys, signing certificates, or attached policies.
    for key in configMap['plugins']:
        if  key['name']=='aws':
            Dev1ID= key['Dev1ID']
            Dev1Secret= key['Dev1Secret']
            Dev2ID= key['Dev2ID']
            Dev2Secret= key['Dev2Secret']

    username = email[:-13]

    # Signiant DEV1
    client = boto3.client(
        'iam',
        aws_access_key_id=Dev1ID,
        aws_secret_access_key=Dev1Secret
    )

    #remove from groups
    response = client.list_groups_for_user(UserName=username)
    groups=response.get('Groups')
    for group in groups:
        response = client.remove_user_from_group(GroupName=group.get('GroupName'),UserName=username)

    #remove access keys
    response = client.list_access_keys(UserName=username)
    keys= response.get('AccessKeyMetadata')
    for key in keys:
        response = client.delete_access_key(
            UserName=username,
            AccessKeyId=key.get('AccessKeyId')
        )
    #delete login profile
    try:
        response = client.delete_login_profile(UserName=username)
    except:
        print ('no aws login profile, proceeding...')

    response = client.delete_user(UserName=username)

    # Signiant DEV2 repeat of above
    client = boto3.client(
        'iam',
        aws_access_key_id=Dev2ID,
        aws_secret_access_key=Dev2Secret
    )

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


    plugin = "AWS"
    log = 'AWS: '+username + ' removed from signiant aws dev 1 and 2.\n'
    instruction = username +'has been removed from signiantdev on aws  '
    return user_provision.getJsonResponse(plugin,email, log, instruction)