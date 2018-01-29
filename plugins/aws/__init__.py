import ast

import botocore
from botocore.exceptions import ClientError
import boto3
import user_provision
from plugin import getUrl, getGroups, inviteMessage


def inviteUser(email, configMap,allPermissions, plugin_tag):
    username = email[:-13]
    cli_groups = []


    for permission in allPermissions:
        thisPermissions = ast.literal_eval(permission)  # to dictionnary
        if thisPermissions['plugin'] == plugin_tag:
            del thisPermissions['plugin']
            cli_groups=list(thisPermissions.values())
            break

    # for plugin_groups in groups:
    #     group = [x.strip() for x in plugin_groups.split(':')]
    #     if group[0] == plugin_tag:
    #         cli_groups = [x.strip() for x in group[1].split(',')]
    #         break

    if len(cli_groups) == 0:
        cli_groups = getGroups(configMap, plugin_tag)

    for key in configMap['plugins']:
        if key['tag'] == plugin_tag:
            ID = key['ID']
            Secret = key['Secret']

    client = boto3.client('iam',
                          aws_access_key_id=ID,
                          aws_secret_access_key=Secret
                          )
    # createUser(username, client, configMap, cli_groups)

    # response = client.create_user(UserName=username)
    #
    # for group in cli_groups:
    #     response = client.add_user_to_group(
    #         GroupName=group,
    #         UserName=username
    #     )

    log = plugin_tag+': '+username+' added to '+plugin_tag+'\n'
    instruction= inviteMessage(configMap, plugin_tag)
    return user_provision.getJsonResponse(plugin_tag,email, log, instruction)


def deleteMessage(configMap, plugin_tag):
    pass


def removeUser(email, configMap,allPermissions, plugin_tag):
    #Deletes the specified IAM user. The user must not belong to any groups or have any access keys, signing certificates, or attached policies.
    for key in configMap['plugins']:
        if  key['tag']==plugin_tag:
            ID= key['ID']
            Secret= key['Secret']

    username = email[:-13]

    client = boto3.client('iam',
        aws_access_key_id=ID,
        aws_secret_access_key=Secret
    )

    log = plugin_tag + ': ' + username + ' removed from signiant.\n'
    instruction = deleteMessage(configMap, plugin_tag)
    try:
        # remove from groups
        response = client.list_groups_for_user(UserName=username)
        groups = response.get('Groups')
        for group in groups:
            response = client.remove_user_from_group(GroupName=group.get('GroupName'), UserName=username)

        # log = 'Failed to remove user. ' + str(e)
        # instruction = 'Failed to remove user.' + str(e)

        # remove access keys
        response = client.list_access_keys(UserName=username)
        keys = response.get('AccessKeyMetadata')
        for key in keys:
            response = client.delete_access_key(
                UserName=username,
                AccessKeyId=key.get('AccessKeyId')
            )

        # delete login profile
        response = client.delete_login_profile(UserName=username)

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            log = 'Failed to remove user. ' + str(e)
            instruction = 'Failed to remove user.' + str(e)
        else:
            raise e

    return user_provision.getJsonResponse(plugin_tag,email, log, instruction)