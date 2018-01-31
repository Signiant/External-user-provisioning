import urllib
import azure
from azure.mgmt.resource import ResourceManagementClient

import user_provision

from plugin import removalMessage

def inviteUser(email,configMap,allPermissions,plugin_tag):

    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            client_id= plugin['Client_Id']
            secret=plugin['Key']
            tenant=plugin['Tenant_Id']
            portalEmail=plugin['email']
            password=plugin["password"]

    credentials = UserPassCredentials(
        portalEmail,  # Your new user
        password,  # Your password
    )
    client = ResourceManagementClient(credentials, 'a')
    for item in client.resource_groups.list():
        print(item)

    log = 'Azure: '+email+' removed from signiant team.\n'
    instruction = email + removalMessage(configMap, plugin_tag)
    return user_provision.getJsonResponse(plugin_tag, email, log, instruction)

