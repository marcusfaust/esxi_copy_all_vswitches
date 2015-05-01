__author__ = 'mxf7'

from pyVim import connect
from pyVmomi import vim
from pyVim.connect import SmartConnect
import getpass
import ssl


def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break

    return obj


def get_all_objs(content, vimtype):
    """
    Get all the vsphere objects associated with a given type
    """
    obj = {}
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        obj.update({c: c.name})
    return obj


if __name__ == '__main__':

    source_vswitch_info = {}
    dest_vswitch_info = {}
    sourcehost = raw_input('Enter Source Host IP: ')
    desthost = raw_input('Enter Destination Host IP: ')
    pswd = getpass.getpass('Password: ')

    ssl._create_default_https_context = ssl._create_unverified_context

    #Connect to source
    sourcesi = SmartConnect(
        host=sourcehost,
        user='root',
        pwd=pswd,
        port='443')

    #Establish content with sourcesi
    content = sourcesi.RetrieveContent()

    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.HostSystem],True)
    esxihosts = objView.view

    #Get all vswitches and populate dictionary
    for switch in esxihosts[0].configManager.networkSystem.networkConfig.vswitch:
        source_vswitch_info[switch.name] = switch.__dict__
        source_vswitch_info[switch.name]['portgroup'] = []

    #Get all portgroups and add them into corresponding vswitches
    portgroups = esxihosts[0].configManager.networkSystem.networkConfig.portgroup

    for pg in portgroups:
        print pg.spec.vswitchName
        source_vswitch_info[pg.spec.vswitchName]['portgroup'].append(pg.__dict__)


    #Connect to destination
    destsi = SmartConnect(
        host=desthost,
        user='root',
        pwd=pswd,
        port='443')

    #Establish content with destsi
    content = destsi.RetrieveContent()

    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.HostSystem],True)
    esxihosts = objView.view

    #Get all vswitches and populate dictionary
    for switch in esxihosts[0].configManager.networkSystem.networkConfig.vswitch:
        dest_vswitch_info[switch.name] = switch.__dict__
        dest_vswitch_info[switch.name]['portgroup'] = []

    #Get all portgroups and add them into corresponding vswitches
    portgroups = esxihosts[0].configManager.networkSystem.networkConfig.portgroup

    for pg in portgroups:
        print pg.spec.vswitchName
        dest_vswitch_info[pg.spec.vswitchName]['portgroup'].append(pg.__dict__)

    #Create all vswitches from source that aren't on the destination host.

    for vswitch in source_vswitch_info:
        if not dest_vswitch_info.has_key(vswitch):

            print "Adding " + vswitch + " to Network Configuration for " + desthost
            esxihosts[0].configManager.networkSystem.AddVirtualSwitch(vswitch)

            for vswitch_pg in source_vswitch_info[vswitch]['portgroup']:
                print "Adding Portgroup " + vswitch_pg['spec'].name + " to " + vswitch
                esxihosts[0].configManager.networkSystem.AddPortGroup(vswitch_pg['spec'])




