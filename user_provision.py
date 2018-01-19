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


    # current params
    #-c "/Users/elaroche/PycharmProjects/External-user-provisioning-new/config-file/config.yaml"
    #-p papertrail,hello,bitbucket

def main():
    plugin_results = dict()
    if os.path.isfile('log.txt'):
        print("file already exists")
        log= open('log.txt','a')
        log.write('--------------------------\n')
    else:
        print('creating file')
        log = open("log.txt", "w+")

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
    configMap = readConfigFile(args.config)
    email=configMap['global']['newUser']
    pluginsarr=configMap['plugins']

    #run required plugins
    for config_plugin in configMap['plugins']:#loop plugins
        plugin_name = config_plugin['name']
        for requested_plugin in plugins: #loop args
            if plugin_name==requested_plugin: # check if args is valid
                print("Loading plugin: %s  " % plugin_name)
                if plugin_name=='papertrail':
                    plugin_handle = plugin.loadPlugin(plugin_name)
                    log.write(  plugin_handle.listUsers(configMap))
                elif plugin_name=='bitbucket':
                    plugin_handle = plugin.loadPlugin(plugin_name)
                    log.write( plugin_handle.inviteUser(email, configMap))

            #else:
                #print(requested_plugin+' is not a valid plugin for: '+plugin_name)


    # inviteUser(email,PaperTrailUserToken)
    # deleteUser(email,PaperTrailUserToken)
    #listUsers(email, PaperTrailUserToken)bcvd
    log.close()

if __name__ == "__main__":
    main()




