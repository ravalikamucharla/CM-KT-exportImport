#!/usr/bin/python3
import json
import logging
import paramiko
import re
import sys

class EnvComp:
    def __init__(self):
        self.final_output = {
            "Output": "Success",
            "ERROR": "No errors found",
        }
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            #arguments_dict = json.loads(sys.argv[1])  # , object_pairs_hook=OrderedDic

            self.source_sid = (sys.argv[1].split("="))[1]
            self.source_hostname = (sys.argv[2].split("="))[1]
            self.source_username = (sys.argv[3].split("="))[1]
            self.source_password = (sys.argv[4].split("="))[1]
            self.target_sid = (sys.argv[5].split("="))[1]
            self.target_hostname = (sys.argv[6].split("="))[1]
            self.target_username = (sys.argv[7].split("="))[1]
            self.target_password = (sys.argv[8].split("="))[1]
            self.auth_type = (sys.argv[9].split("="))[1]
            self.pem_file = (sys.argv[10].split("="))[1]
            self.is_sudo_user = (sys.argv[11].split("="))[1]
            self.exclude_vars_file = (sys.argv[12].split("="))[1]

            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s',
                            datefmt='%d-%b-%y %H:%M:%S', filename="/tmp/linux_env_log.txt", filemode='a')

            if self.auth_type:
                self.auth_type = self.auth_type.lower()

            self.source_sid_adm = self.source_sid.lower() + 'adm'
            self.target_sid_adm = self.target_sid.lower() + 'adm'

            # Read exclude vars file
            with open(self.exclude_vars_file, "r") as f:
                self.exclude_vars = f.read().splitlines()
            
            # Login to source system and collect env vars
            source_env_vars = self.login_sys(self.source_hostname, self.source_username,
                                             self.source_password, self.source_sid_adm)

            # Login to target system and collect env vars
            target_env_vars = self.login_sys(self.target_hostname, self.target_username,
                                             self.target_password, self.target_sid_adm)

            if source_env_vars != target_env_vars:
                self.compare_env_vars(source_env_vars, target_env_vars)

        except Exception as exc:
            self.final_output["Output"] = "Failure"
            self.final_output['ERROR'] = "General exception occurred, Error :%s" % exc
            print(json.dumps(self.final_output, default=str))
            sys.exit(1)

    def login_sys(self, hostname, username, password, sid_adm):
        """"
        Logging into the system using provided credentials
        """
        try:
            if self.auth_type == 'password':
                logging.info("Inside password")
                self.ssh.connect(str(hostname), username=username, password=str(password))
            if self.auth_type == 'ppk':
                logging.info("inside ppk file with pem file %s" % self.pem_file)
                conn = self.ssh.connect(str(hostname), username=username, key_filename=self.pem_file)
                logging.info("connection completed %s" % conn)
            if self.auth_type == 'passwordandppk':
                self.ssh.connect(str(hostname), username=username, key_filename=self.pem_file)
            if self.is_sudo_user.upper() == 'TRUE':
                logging.info("inside sudo user")
                self.auth_type = 'ppk'

            output = self.get_env_details(sid_adm)
            return output

        except Exception as ex:
            self.final_output["Output"] = "Failure"
            self.final_output["ERROR"] = "error is :%s" % ex
            print(json.dumps(self.final_output, default=str))
            sys.exit(1)

    def get_env_details(self, sid_adm):
        """"
        Fetching environment vars
        """
        # Get env vars
        result = self.execute_command('env', sid_adm)
        if result:
            result_row = result.splitlines()
            env_vars_dict = {}
            for data in result_row:
                row_split = data.split("=")
                env_vars_dict[row_split[0]] = row_split[1]
            return env_vars_dict

    def compare_env_vars(self, source_data, target_data):
        """"
        Comparing the environment vars of source and target
        """
        self.add_vars_dict = {}
        self.update_vars_dict = {}

        for env_vars in source_data.keys():
            if env_vars in target_data:
                is_equal = source_data.get(env_vars) == target_data.get(env_vars)
                if not is_equal:
                    target_value = target_data.get(env_vars)
                    source_value = source_data.get(env_vars)
                    val_list = target_value.split(':')
                    if source_value not in val_list:
                        self.update_vars_dict[env_vars] = source_data[env_vars]
            else:
                self.add_vars_dict[env_vars] = source_data[env_vars]

        # Check the shell
        shell = self.execute_command('echo $SHELL', self.target_sid_adm)
        logging.info("shell is %s" % shell)

        self.bash_sh_ksh_shell = re.search(r'/bin/bash|/bin/sh|/bin/ksh', shell, re.IGNORECASE)
        self.csh = re.search(r'/bin/csh', shell, re.IGNORECASE)

        if self.add_vars_dict:
            self.add_env_vars()

        if self.update_vars_dict:
            self.update_env_vars()

    def add_env_vars(self):
        if self.bash_sh_ksh_shell:
            for var in self.add_vars_dict:
                value = self.add_vars_dict[var]
                if len(self.exclude_vars) > 0 and var not in self.exclude_vars:
                    self.execute_command('echo "' + var + '=' + value + '" >> $HOME/.profile', self.target_sid_adm)
                    self.execute_command('echo "export ' + var + '" >> $HOME/.profile', self.target_sid_adm)

        elif self.csh:
            logging.info("inside csh")
            for var in self.add_vars_dict:
                value = self.add_vars_dict[var]
                if len(self.exclude_vars) > 0 and var not in self.exclude_vars:
                    logging.info("inside exclude vars")
                    self.execute_command('echo "setenv ' + var + ' ' + value + '" >> $HOME/.cshrc',
                                         self.target_sid_adm)

    def update_env_vars(self):
        if self.bash_sh_ksh_shell:
            for var in self.update_vars_dict:
                value = self.update_vars_dict[var]
                if len(self.exclude_vars) > 0 and var not in self.exclude_vars:
                    self.execute_command('echo "' + var + '=$' + var + ':' + value + '" >> $HOME/.profile',
                                         self.target_sid_adm)
                    self.execute_command('echo "export ' + var + '" >> $HOME/.profile', self.target_sid_adm)
        elif self.csh:
            logging.info("inside csh for update vars")
            for var in self.update_vars_dict:
                value = self.update_vars_dict[var]
                if len(self.exclude_vars) > 0 and var not in self.exclude_vars:
                    logging.info("inside exclude vars for update")
                    self.execute_command('echo "setenv ' + var + ' ' + value + ':$' + var + '" >> $HOME/'
                                          '.cshrc', self.target_sid_adm)

    def execute_command(self, command, sid_adm):
        try:
            if self.auth_type == 'password':
                logging.info("inside password for command: %s" % command)
                _, stdout, stderr = self.ssh.exec_command(command)
                logging.info(command)
            elif self.auth_type in ('ppk', 'passwordandppk'):
                _, stdout, stderr = self.ssh.exec_command(r"sudo su - %s -c '%s'" % (sid_adm, command))
                logging.info(r"sudo su - %s -c '%s'" % (sid_adm, command))
            
            result = str(stdout.read(), 'UTF-8')
            error = str(stderr.read(), 'UTF-8')

            logging.info(result)
            logging.info(error)
            if result:
                return result
            elif error:
                self.final_output["Output"] = "Failure"
                self.final_output["ERROR"] = error
                return self.final_output
        except Exception as ex:
            self.final_output["Output"] = "Failure"
            self.final_output["ERROR"] = "Exception occurred: %s" % ex
            return self.final_output


try:
    # Creating object of class
    obj_env_comp = EnvComp()
    print(json.dumps(obj_env_comp.final_output, default=str))
    sys.exit()
except Exception as err:
    print(err)
