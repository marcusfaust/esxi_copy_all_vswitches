__author__ = 'mxf7'

from pyVim import connect
from pyVmomi import vim
from pyVim.connect import SmartConnect
import getpass
import ssl


if __name__ == '__main__':

    sourcehost = raw_input('Enter Source Host IP: ')
    desthost = raw_input('Enter Destination Host IP: ')
    pswd = getpass.getpass('Password: ')

    ssl._create_default_https_context = ssl._create_unverified_context

    #Connect
    sourcesi = SmartConnect(
        host=sourcehost,
        user='root',
        pwd=pswd,
        port='443')

    print "hello"


