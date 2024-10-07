#!/usr/bin/python3
import sys
import logging
from pyrfc import Connection
import winrm                   # used to connect to the windows server remotely
import paramiko                # for SSH connection to SAP server

out_dict = {'success':False,'output':'','err_type':''}
def import_modules(os_type,auth_type,host,user,password,pemfile,domain_nm=""):
    try:
        if os_type == 'WINDOWS':
            import winrm                   # used to connect to the windows server remotely
            if not domain_nm:
                conn = winrm.Session(str(host), auth=(str(user), str(password)))
            else:
                conn = winrm.Session(host, auth=(user, password), transport='ntlm')
            return conn
        else:
            import paramiko             # for SSH connection to SAP server
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if auth_type == 'password':
                ssh.connect(str(host), username=user, password=str(password))
            if auth_type == 'ppk':
                ssh.connect(str(host), username=user, key_filename=pemfile)
            if auth_type == 'passwordandppk':
                ssh.connect(str(host), username=user, key_filename=pemfile)
            return ssh
    except ImportError:
        output_dict = {'Output': 'Error', 'ErrorMessage': "Error in general login :%s" %ImportError}
        out_dict['output'] = output_dict
        return


class Login:
    """Main class which include all the connections for linux
    and windows
    """
    def __init__(self, hostname, username, password, operating_system, auth_type, pemfile_path, issudouser):
        '''
        Constructor to establish a connection to the host server
        '''
        try:
            self.hostname = hostname
            self.username = username
            self.password = password
            self.auth_type = auth_type.lower()
            self.output_data=out_dict
            if operating_system.upper() == 'WINDOWS':
                domain_nm = ''
                if '\\' in username:
                    names = username.split('\\')
                    self.username = names[1]
                    domain_nm = names[0]
                    self.username = '{}@{}'.format(self.username, domain_nm)
                else:
                    self.username = username
                self.conn = import_modules(operating_system.upper(), auth_type, hostname, username, password, pemfile_path,domain_nm)

            elif operating_system.upper() == 'LINUX':
                if issudouser.upper() == 'TRUE':
                    self.auth_type = 'ppk'
                self.ssh = import_modules(operating_system.upper(), auth_type, hostname, username, password, pemfile_path)
            self.output_data['success']=True
            #Conditionally import modules
            return
        except Exception as err:
            output_dict={'Output':'Error','ErrorMessage':err}
            self.output_data['output']=output_dict
            return

class SAPLogin:
    """
    Main class which handles SAP connections

    """
    def __init__(self, hostip, instance,username,group, password,client,sncpartnername=None):
        self.hostip = hostip
        self.instance = instance
        self.username = username
        self.group = group
        self.password = password
        self.client = client
        self.sncpartnername = sncpartnername

    def Connect_SAP(self):
        if self.sncpartnername == None or self.sncpartnername == "":
            if self.group == '_NULL': #uses PAS 2 digit instance
                self.conn = Connection(user=self.username, passwd=self.password, ashost=self.hostip, sysnr=self.instance, client=self.client)
            else:
                instance = '36'+str(self.instance)
                self.conn = Connection(user=self.username, passwd=self.password, mshost=self.hostip, msserv=instance, client=self.client, group=self.group )
        else:
            if self.group == '_NULL':  #Uses 2-digit PAS instance
                self.conn = Connection(name=self.username, ashost=self.hostip, sysnr=self.instance, snc_partnername=self.sncpartnername )                       
            else:
                instance = '36'+str(self.instance)
                self.conn = Connection(name=self.username, passwd=self.password, mshost=self.hostip, msserv=instance, group=self.group, snc_partnername=self.sncpartnername )
        return self.conn