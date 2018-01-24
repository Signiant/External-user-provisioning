import argparse
import os
import sys
import yaml
import boto3
import plugin


def readConfigFile(path):
    configMap = []

    try:
        config_file_handle = open(path)
        configMap = yaml.load(config_file_handle)
        config_file_handle.close()
    except:
        print
        "Error: Unable to open config file %s or invalid yaml" % path

    return configMap

    # current params
    #-c "/Users/elaroche/PycharmProjects/External-user-provisioning-new/config-file/config.yaml"
    #-p papertrail,hello,bitbucket

def main():
    plugin_results = dict()
    if os.path.isfile('log.txt'):
        print("file already exists")
        log= open('log.txt','a')
        log.write('------------------------------\n')
    else:
        print('creating file')
        log = open("log.txt", "w+")

    client = boto3.client('iam')
    response = client.create_user(
        UserName='test_signiant'
    )
    print (response)
    # session = boto3.client(
    #     'iam'
    # )
    # paginator = session.get_paginator('list_users')
    # for response in paginator.paginate():
    #     print(response)


    #Command Line
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    parser = argparse.ArgumentParser(description='External user provisioning tool')
    parser.add_argument('-c','--config', help='Full path to a config file',required=True)
    parser.add_argument('-p','--plugin', help='the plugin to execute',required=True)
    args = parser.parse_args()
    print(args)
    plugins=[x.strip() for x in args.plugin.split(',')]

    # load Config file
    configMap = readConfigFile(args.config)
    if plugins[0]=="all":
        plugins.pop()
        for config_plugin in configMap['plugins']:
            plugins.append(config_plugin['name'])

    email=configMap['global']['newUser']
    validPlugins=[]
    print(email)
    #run required plugins
    for config_plugin in configMap['plugins']:#loop plugins
        plugin_name = config_plugin['name']
        for requested_plugin in plugins: #loop args
            if plugin_name==requested_plugin: # check if args is valid
                print("Loading plugin: %s  " % plugin_name)
                # if plugin_name=='papertrail': ###MAKE ALL METHOD NAMES THE SAME, then create new method
                #     plugin_handle = plugin.loadPlugin(plugin_name) #listUsers
                #     json =(plugin_handle.listUsers(email, configMap))
                #     validPlugins.append(json)
                #     log.write(json['Log'])
           #      elif plugin_name=='bitbucket':#removing from all groups
           #          plugin_handle = plugin.loadPlugin(plugin_name)
           #          json =(plugin_handle.removeUser(email, configMap))
           #          validPlugins.append(json)
           #          log.write(json['Log'])
           #      elif plugin_name == 'slack': #returns link only
           #          plugin_handle = plugin.loadPlugin(plugin_name)
           #          json=(plugin_handle.deleteUser(email,configMap))
           #          validPlugins.append(json)
           #          log.write(json['Log'])
           #      elif plugin_name == 'artifactory': #returns link only
           #          plugin_handle = plugin.loadPlugin(plugin_name)
           #          json = (plugin_handle.send_email_invite(email, configMap))
           #          validPlugins.append(json)
           #          log.write(json['Log'])

    #mail.emailOutput(configMap,validPlugins)


    # inviteUser(email,PaperTrailUserToken)
    # deleteUser(email,PaperTrailUserToken)
    #listUsers(email, PaperTrailUserToken)bcvd


    #team-cost-reporter, output.outputresults,



    log.close()

if __name__ == "__main__":
    main()




