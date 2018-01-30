import user_provision
from plugin import removalMessage
from azure.common.credentials import ServicePrincipalCredentials


def inviteUser(email,configMap,allPermissions,plugin_tag):

    for plugin in configMap['plugins']:
        if plugin['plugin'] + ':' + plugin['tag'] == plugin_tag:
            client_id= plugin['Client_Id']
            secret=plugin['Key']
            tenant=plugin['Tenant_Id']

    credentials = ServicePrincipalCredentials(
        client_id=client_id,
        secret=secret,
        tenant=tenant
    )


    log = 'Azure: '+email+' removed from signiant team.\n'
    instruction = email + removalMessage(configMap, plugin_tag)
    return user_provision.getJsonResponse(plugin_tag, email, log, instruction)