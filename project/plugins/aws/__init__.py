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
    cont = True
    groups = {}
    keys = {}

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

    except client.exceptions.NoSuchEntityException:
        print(plugin_tag + ' error: ' + username + ' could not be deleted, because it does not exist')
        cont = False

    except client.exceptions.ServiceFailureException:
        print(plugin_tag + ' error: ' + username + ' Service failure while deleting this user')
        cont = False

    except ClientError:
        log = (plugin_tag + 'error:  ' + username + ' was not deleted')
        instruction = log
        cont = False

    if cont == True:

      try:
            for group in groups:
                response = client.remove_user_from_group(GroupName=group.get('GroupName'), UserName=username)

      except client.exceptions.NoSuchEntityException:
                         print(plugin_tag + ' error: ' + username + ' could not be removed from the group, because the user does not exist')
                         cont = False

      except client.exceptions.ServiceFailureException:
                         print(plugin_tag + ' error: ' + username + ' could not be removed from the group. Service failure')
                         cont = False

      if cont == True:

          try:

             # remove access keys
            response = client.list_access_keys(UserName=username)
            keys = response.get('AccessKeyMetadata')


          except client.exceptions.NoSuchEntityException:
                    print(plugin_tag + ' error: Could not list access keys, ' + username + ' does not exist')
                    cont = False

          except client.exceptions.ServiceFailureException:
                    print(plugin_tag + ' error: ' + username + ' Service failure while listing access key')
                    cont = False

          except ClientError:
                    log = (plugin_tag + username + ' error: could not list access keys')
                    instruction = log
                    print(log)
                    cont = False

      if cont == True:

          try:

              for key in keys:

                    response = client.delete_access_key(UserName=username, AccessKeyId=key.get('AccessKeyId'))

          except client.exceptions.NoSuchEntityException:
                    print(plugin_tag + ' error: Could not delete access key, ' + username + ' does not exist. ')
                    cont = False

          except client.exceptions.ServiceFailureException:
                    print(plugin_tag + ' error: ' + username + ' Service failure while deleting access key')
                    cont = False

          except ClientError:
                    log = (plugin_tag + 'Could not delete access key of a user: ' + username)
                    instruction = log
                    cont = False

          # this deletes user password if it exists. User profile cannot be deleted if a password is not deleted
          try:
              response = client.delete_login_profile(UserName=username)
          except:
              pass

          try:

            response = client.delete_user(UserName=username)

            log = plugin_tag + ': User ' + username + 'profile has been deleted\n'
            instruction = log
            done = True

          except client.exceptions.NoSuchEntityException:
                print(plugin_tag + 'error: ' + username +  ' could not be deleted, because it does not exist')
                cont = False

          except client.exceptions.DeleteConflict:
                print(plugin_tag + 'error: ' +  username + ' could not delete a resource that has attached subordinate entities')
                cont = False

          except client.exceptions.ServiceFailureException:
                print(plugin_tag + 'error: ' + username + ' could not be deleted. Service failure')
                cont = False

          except ClientError:
                print(plugin_tag + 'error: ' +  username + ' could not be deleted')
                cont = False




    return getJsonResponse('AWS '+plugin_tag[4:],email, log, instruction, done)





