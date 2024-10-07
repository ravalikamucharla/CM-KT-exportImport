#!/usr/bin/python3
import sys
import winrm                   # used to connect to the windows server remotely
import paramiko                # for SSH connection to SAP server


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
            self.output_data={'success':False,'output':'','err_type':''}
            if operating_system.upper() == 'WINDOWS':
                domain_nm = ''
                if '\\' in username:
                    names = username.split('\\')
                    self.username = names[1]
                    domain_nm = names[0]
                    self.username = '{}@{}'.format(self.username, domain_nm)
                else:
                    self.username = username

                if not domain_nm:
                    self.conn = winrm.Session(str(self.hostname), auth=(str(self.username), str(self.password)))
                else:
                    self.conn = winrm.Session(self.hostname, auth=(self.username, self.password), transport='ntlm')

            elif operating_system.upper() == 'LINUX':
                self.ssh = paramiko.SSHClient()
                self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                if self.auth_type == 'password':
                    self.ssh.connect(str(self.hostname), username=self.username, password=str(self.password))
                if self.auth_type == 'ppk':
                    self.ssh.connect(str(self.hostname), username=self.username, key_filename=pemfile_path)
                if self.auth_type == 'passwordandppk':
                    self.ssh.connect(str(self.hostname), username=self.username, key_filename=pemfile_path)
                if issudouser == 'TRUE':
                    self.auth_type = 'ppk'
            self.output_data['success']=True
            return
        except Exception as err:
            output_dict={'Output':'Error','ErrorMessage':err}
            print("ERROR IN Authentication",err)
            self.output_data['output']=output_dict
            return
