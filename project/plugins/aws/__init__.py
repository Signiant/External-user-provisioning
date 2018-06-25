import ast
import botocore
from botocore.exceptions import ClientError, ParamValidationError
import boto3
from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getGroups


def inviteUser(email, configMap,allPermissions, plugin_tag, name):

    done = False
    cont = True

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

    client = boto3.client('iam', aws_access_key_id=ID, aws_secret_access_key=Secret)

    try:
        response = client.create_user(UserName=username)

    except client.exceptions.EntityAlreadyExistsException as ex:
        log = plugin_tag + "%s" % ex
        instruction = log
        print(log)
        cont = False

    except botocore.exceptions.EndpointConnectionError:
        log = plugin_tag+"Error: No internet connection. Could not connect to aws"
        instruction = log
        print(log)
        cont = False

    except ClientError as ce:
        log = (plugin_tag + " Unexpected Error: {0}".format(ce))
        instruction = log
        print(log)
        cont = False

    if cont:

        try:
           for group in cli_groups:
             response = client.add_user_to_group(GroupName=group,UserName=username)
             done = True

        except client.exceptions.NoSuchEntityException:
            log =  (plugin_tag + ' error: ' + username + ' could not be added to the group, because it does not exist')
            instruction = log
            print(log)

        except client.exceptions.ServiceFailureException:
            log = (plugin_tag + ' error: ' + username + ' could not be added to the group. Service failure')
            instruction = log
            print(log)

        except ClientError:
            log = (plugin_tag + 'Could not add user ' + username + ' to the group')
            instruction = log
            print(log)

    return getJsonResponse('AWS '+plugin_tag[4:],email, log, instruction, done)


def removeUser(email, configMap,allPermissions, plugin_tag):

    done = False
    cont = True
    groups = {}
    keys = {}
    log= ""
    instruction = ""

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

    try:
        # remove from groups
        response = client.list_groups_for_user(UserName=username)
        groups = response.get('Groups')

    except client.exceptions.NoSuchEntityException:
        log = (plugin_tag + ' error: ' + username + ' could not be deleted, because it does not exist')
        instruction = log
        print(log)
        cont = False

    except client.exceptions.ServiceFailureException:
        log = (plugin_tag + ' error: ' + username + ' Service failure while deleting this user')
        instruction = log
        print(log)
        cont = False

    except ClientError:
        log = (plugin_tag + 'error:  ' + username + ' was not deleted')
        instruction = log
        cont = False

    if cont:
        try:
            for group in groups:
                response = client.remove_user_from_group(GroupName=group.get('GroupName'), UserName=username)

        except client.exceptions.NoSuchEntityException:
            log = (plugin_tag + ' error: ' + username + ' could not be removed from the group, because the user does not exist')
            instruction = log
            print(log)
            cont = False

        except client.exceptions.ServiceFailureException:
            log = (plugin_tag + ' error: ' + username + ' could not be removed from the group. Service failure')
            instruction = log
            print(log)
            cont = False

    if cont:
        try:
             # remove access keys
             # there can be multiple access keys returned here
            response = client.list_access_keys(UserName=username)
            keys = response.get('AccessKeyMetadata')

        except client.exceptions.NoSuchEntityException:
            log = (plugin_tag + ' error: Could not list access keys, ' + username + ' does not exist')
            instruction = log
            print(log)
            cont = False

        except client.exceptions.ServiceFailureException:
            log = (plugin_tag + ' error: ' + username + ' Service failure while listing access key')
            instruction = log
            print(log)
            cont = False

        except ClientError:
            log = (plugin_tag + username + ' error: could not list access keys')
            instruction = log
            print(log)
            cont = False

    if cont:
        try:
          for key in keys:
            response = client.delete_access_key(UserName=username, AccessKeyId=key.get('AccessKeyId'))

        except client.exceptions.NoSuchEntityException:
            log = (plugin_tag + ' error: Could not delete access key, ' + username + ' does not exist. ')
            instruction = log
            print(log)
            cont = False

        except client.exceptions.ServiceFailureException:
            log = (plugin_tag + ' error: ' + username + ' Service failure while deleting access key')
            instruction = log
            print(log)
            cont = False

        except ClientError:
            log = (plugin_tag + 'Could not delete access key of a user: ' + username)
            instruction = log
            cont = False

    if cont:
        # this deletes user's password if it exists (password IS the profile).
        # If a user does not have a password, we get an exception BUT we can just ignore this with a pass
        # because we don't care
        # A user cannot be deleted if they have a password (so deleting the password is critical)
        try:
            response = client.delete_login_profile(UserName=username)
        except:
            pass

        try:
            response = client.delete_user(UserName=username)
            log = plugin_tag + ': User ' + username + ' profile has been deleted\n'
            instruction = log
            done = True

        except client.exceptions.NoSuchEntityException:
            log = (plugin_tag + 'error: ' + username +  ' could not be deleted, because it does not exist')
            instruction = log
            print(log)

        except client.exceptions.DeleteConflict:
            log = (plugin_tag + 'error: ' +  username + ' could not delete a resource that has attached subordinate entities')
            instruction = log
            print(log)

        except client.exceptions.ServiceFailureException:
            log = (plugin_tag + 'error: ' + username + ' could not be deleted. Service failure')
            instruction = log
            print(log)

        except ClientError:
            log = (plugin_tag + 'error: ' +  username + ' could not be deleted')
            instruction = log
            print(log)

    return getJsonResponse('AWS '+plugin_tag[4:],email, log, instruction, done)