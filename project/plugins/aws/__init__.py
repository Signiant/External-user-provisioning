import ast
import botocore
from botocore.exceptions import ClientError, ParamValidationError
import boto3
from project.user_provision import getJsonResponse
from project.plugin import inviteMessage, removalMessage, getGroups


def inviteUser(email, configMap,allPermissions, plugin_tag, name):

    done = False
    cont = False

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

        response = client.create_user(UserName=username)
        cont = True

    except client.exceptions.EntityAlreadyExistsException as ex:
        log = plugin_tag + "%s" % ex
        instruction = log
        print(log)

    except ClientError as ce:
        log = (plugin_tag + " Unexpected Error: {0}".format(ce))
        instruction = log
        print(log)

    if cont == True:

        try:

           for group in cli_groups:
             response = client.add_user_to_group(
                 GroupName=group,
                 UserName=username
           )
             done = True

        except client.exceptions.NoSuchEntityException:
            print (plugin_tag + ' error: ' + username + ' could not be added to the group, because it does not exist')

        except client.exceptions.ServiceFailureException:
            print(plugin_tag + ' error: ' + username + ' could not be added to the group. Service failure')

        except ClientError:
            log = (plugin_tag + 'Could not add user ' + username + ' to the group')
            instruction = log
            print(log)


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

             try:

                 response = client.remove_user_from_group(GroupName=group.get('GroupName'), UserName=username)

             except client.exceptions.NoSuchEntityException:
                 print(plugin_tag + ' error: ' + username + ' could not be removed from the group, because it does not exist')

             except client.exceptions.InvalidUserTypeException:
                 print(plugin_tag + ' error: ' + username + ' of this type could not be removed from the group.')

             except client.exceptions.ServiceFailureException:
                 print(plugin_tag + ' error: ' + username + ' could not be removed from the group. Service failure')

             except client.exceptions.EntityTemporarilyUnmodifiableException:
                 print(plugin_tag + ' error: ' + username + ' could not be removed from the group. Try again')

             except ClientError:
                 log = (plugin_tag + 'Could not remove user ' + username + ' from the group')
                 instruction = log

        # remove access keys
        response = client.list_access_keys(UserName=username)
        keys = response.get('AccessKeyMetadata')

        try:

            for key in keys:
                 client.delete_access_key(
                    UserName=username,
                    AccessKeyId=key.get('AccessKeyId')
                )

        # can the access key be attached to another resource?

        # except client.exceptions.DeleteConflictException:
        #     print(plugin_tag + ' error: access key of a ' + username + ' could not be deleted. Can not delete the resource because it is attached to one or more resources')

        except client.exceptions.EntityTemporarilyUnmodifiableException:
            print(plugin_tag + ' error: access key of a user ' + username + ' could not be deleted. Try again')

        except client.exceptions.UnmodifiableEntityException:
            print(plugin_tag + ' error: access key of a user ' + username + ' could not be deleted. This user cannot be modified')

        except ClientError:
            log = (plugin_tag + 'Could not delete access key of a user: ' + username)
            instruction = log

        # delete login profile
        try:

            response = client.delete_login_profile(UserName=username)

        except:
            pass

        response = client.delete_user(UserName=username)
        log = plugin_tag + ': User ' + username + 'profile has been deleted\n'
        instruction = log
        done = True

    except client.exceptions.NoSuchEntityException:

        print(plugin_tag, username, ' could not be deleted, because it does not exist')

    except client.exceptions.InvalidUserTypeException:
        print(plugin_tag, username, ' of this type could not be deleted')

    except client.exceptions.ServiceFailureException:
        print(plugin_tag, username, ' could not be deleted. Service failure')

    except client.exceptions.EntityTemporarilyUnmodifiableException:
        print(plugin_tag, username, ' could not be deleted. Try again')

    except ClientError:
        print(plugin_tag, username, ' could not be deleted')

    # except (botocore.exceptions.ClientError, botocore.exceptions.ClientError) as e:
    #     if e.response['Error']['Code'] == 'NoSuchEntity':
    #         log = plugin_tag+ str(e)
    #         instruction = log
    #         print(log)
    #     else:
    #         raise e

    return getJsonResponse('AWS '+plugin_tag[4:],email, log, instruction, done)





