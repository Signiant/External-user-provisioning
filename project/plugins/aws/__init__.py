import ast
import botocore
from botocore.exceptions import ClientError
import boto3
from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getGroups


def inviteUser(email, configMap,allPermissions, plugin_tag, name):

    done = False

    username = email.split('@', 1)[0]

    cli_groups = []

    log =  'AWS: ' + username + ' added to ' + plugin_tag + '\n'
    instruction = inviteMessage(configMap, plugin_tag).replace("<username>", username)

    for permission in allPermissions:
        thisPermissions = ast.literal_eval(permission)
        if thisPermissions['plugin'] == plugin_tag:
            del thisPermissions['plugin']
            cli_groups=list(thisPermissions.values())
            break

    if len(cli_groups) == 0:
        cli_groups = getGroups(configMap, plugin_tag)

    for key in configMap['plugins']:
        if key['plugin']+':'+key['tag'] == plugin_tag:
            ID = key['ID']
            Secret = key['Secret']


    client = boto3.client('iam',
                          aws_access_key_id=ID,
                          aws_secret_access_key=Secret
                          )
    try:

        client.create_user(UserName=username)
        done = True

    except:
        log = plugin_tag + ' The user ' + username + ' already exists'
        instruction = log
        print(log)

    for group in cli_groups:
        client.add_user_to_group(
            GroupName=group,
            UserName=username
        )

    return getJsonResponse('AWS '+plugin_tag[4:],email, log, instruction, done)


def removeUser(email, configMap,allPermissions, plugin_tag):

    done = False
    #Deletes the specified IAM user. The user must not belong to any groups or have any access keys, signing certificates, or attached policies.
    for key in configMap['plugins']:
        if  key['plugin']+':'+key['tag']==plugin_tag:
            ID= key['ID']
            Secret= key['Secret']

    username = email.split('@', 1)[0]

    client = boto3.client('iam',
        aws_access_key_id=ID,
        aws_secret_access_key=Secret
    )

    log = plugin_tag + ': ' + username + ' removed from organization.\n'
    instruction = email.split('@', 1)[0] + removalMessage(configMap, plugin_tag)

    try:
        # remove from groups
        response = client.list_groups_for_user(UserName=username)
        groups = response.get('Groups')
        for group in groups:
            client.remove_user_from_group(GroupName=group.get('GroupName'), UserName=username)

        # remove access keys
        response = client.list_access_keys(UserName=username)
        keys = response.get('AccessKeyMetadata')
        for key in keys:
             client.delete_access_key(
                UserName=username,
                AccessKeyId=key.get('AccessKeyId')
            )

        # delete login profile
        try:

            log = plugin_tag+': User ' +username+ '. ' + 'profile has been deleted\n'
            instruction = log
            done = True

            client.delete_login_profile(UserName=username)

        except:
            pass
        client.delete_user(UserName=username)
    except (botocore.exceptions.ClientError, botocore.exceptions.ClientError) as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            log = plugin_tag+ str(e)
            instruction = log
            print(log)
        else:
            raise e

    return getJsonResponse('AWS '+plugin_tag[4:],email, log, instruction, done)