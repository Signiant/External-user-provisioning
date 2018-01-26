import user_provision


import os
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient

# subscription_id = os.environ.get(
#     'AZURE_SUBSCRIPTION_ID',
#     '11111111-1111-1111-1111-111111111111') # your Azure Subscription Id
# credentials = ServicePrincipalCredentials(
#     client_id=os.environ['AZURE_CLIENT_ID'],
#     secret=os.environ['AZURE_CLIENT_SECRET'],
#     tenant=os.environ['AZURE_TENANT_ID']
# )
# client = ResourceManagementClient(credentials, subscription_id)

def inviteUser(email, configMap,allPermissions,groups):
    #
    # # Tenant ID for your Azure Subscription
    # TENANT_ID = 'dc3a3f5d-523f-4f85-a01d-9c1adef9010f'
    #
    # # Your Service Principal App ID
    # CLIENT = 'debb7503-259c-4390-8223-1c172cfa3294'
    #
    # # Your Service Principal Password
    # KEY = 'zDEbuarzqq3LuZhhn+MsnAVwvwOLhEKvuEWb27WWnyM='
    #
    # credentials = ServicePrincipalCredentials(
    #     client_id = CLIENT,
    #     secret = KEY,
    #     tenant = TENANT_ID
    # )
    # print(credentials)
    # print(credentials)

    credentials = ServicePrincipalCredentials(
        client_id='ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL',
        secret='XXXXXXXXXXXXXXXXXXXXXXXX',
        tenant='ABCDEFGH-1234-ABCD-1234-ABCDEFGHIJKL'
    )

    plugin = "Azure"
    log = credentials+'Azure: \n'
    instruction = ''
    return user_provision.getJsonResponse(plugin, email, log, instruction)



#from azure.common.credentials import ServicePrincipalCredentials