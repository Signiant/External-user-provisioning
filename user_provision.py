import argparse
import os
import sys
import yaml
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


def main():
    plugin_results = dict()

    #Command Line
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    parser = argparse.ArgumentParser(description='External user provisioning tool')
    parser.add_argument('-c','--config', help='Full path to a config file',required=True)
    parser.add_argument('-p','--plugin', help='the plugin to execute',required=True)
    args = parser.parse_args()
    print(args)
    plugins=[x.strip() for x in args.plugin.split(',')]

    #load Config file
    fpath = os.path.dirname(__file__)

    #configMap = readConfigFile(fpath + '/config-file/config.yaml')
    configMap = readConfigFile(args.config)

    #email=configMap['global']['newUser']

    for config_plugin in configMap['plugins']:
        plugin_name = config_plugin['name']
        for requested_plugin in plugins:
            if plugin_name==requested_plugin:
                print("Loading plugin %s" % plugin_name)
                plugin_handle = plugin.loadPlugin(plugin_name)
                plugin_handle.listUsers(configMap)
            else:
                print(requested_plugin+' is not a valid plugin')
        plugin_handle = plugin.loadPlugin('bitbucket')
        plugin_handle.inviteUser(configMap)

    # inviteUser(email,PaperTrailUserToken)
    # deleteUser(email,PaperTrailUserToken)
    #listUsers(email, PaperTrailUserToken)bcvd

if __name__ == "__main__":
    main()




