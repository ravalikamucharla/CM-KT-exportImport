#!/usr/bin/python3
import json
import sys
import winrm
import logging

class EnvComp:
    def __init__(self):
        self.final_output = {
            "Output": "Success",
            "ERROR": "No errors found",
        }
        try:
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

            if self.auth_type:
                self.auth_type = self.auth_type.lower()

            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s - %(levelname)s -%(message)s'
                                , datefmt='%d-%b-%y %H:%M:%S'
                                , filename="/tmp/win_env.log", filemode='a')

            self.source_sid_adm = self.source_sid.lower() + 'adm'
            self.target_sid_adm = self.target_sid.lower() + 'adm'

            # Read exclude vars file
            with open(self.exclude_vars_file, "r") as f:
                self.exclude_vars = f.read().splitlines()

            # Login to source system and collect env vars
            source_env_vars = self.login_sys(self.source_hostname, self.source_username, self.source_password, self.source_sid_adm)

            # Login to target system and collect env vars
            target_env_vars = self.login_sys(self.target_hostname, self.target_username, self.target_password, self.target_sid_adm)

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
            domain_nm = ''
            if '\\' in username:
                names = username.split('\\')
                self.username = names[1]
                domain_nm = names[0]
                self.username = '{}@{}'.format(self.username, domain_nm)
            else:
                self.username = username
            if not domain_nm:
                self.conn = winrm.Session(str(hostname), auth=(str(username), str(password)))
            else:
                self.conn = winrm.Session(hostname, auth=(username, password), transport='ntlm')

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
        result = self.run_cmd('SET', sid_adm)
        logging.info("env vars for sid %s are %s" % (sid_adm, result))
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
        self.actual_vars_dict = {}

        for env_vars in source_data.keys():
            if env_vars in target_data:
                is_equal = source_data.get(env_vars) == target_data.get(env_vars)
                if not is_equal:
                    self.update_vars_dict[env_vars] = source_data[env_vars]
                    self.actual_vars_dict[env_vars] = target_data[env_vars]
            else:
                self.add_vars_dict[env_vars] = source_data[env_vars]

        if self.add_vars_dict:
            self.add_env_vars()

        if self.update_vars_dict:
            self.update_env_vars()

    def add_env_vars(self):
        logging.info("add vars is %s" % self.add_vars_dict)
        for var in self.add_vars_dict:
            value = self.add_vars_dict[var]
            if len(self.exclude_vars) > 0 and var not in self.exclude_vars:
                logging.info("add var is %s" % var)
                # self.run_cmd('REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v '+ var+' /t REG_EXPAND_SZ /d '+ value+' /f', self.target_sid_adm)
                self.run_cmd('REG ADD "HKCU\Environment" /v '+ var+' /t REG_EXPAND_SZ /d '+ value+' /f',
                             self.target_sid_adm)

    def update_env_vars(self):
        logging.info("update vars is %s" % self.update_vars_dict)
        for var in self.update_vars_dict:
            value = self.update_vars_dict[var]
            actual_val = self.actual_vars_dict[var]
            if len(self.exclude_vars) > 0 and var not in self.exclude_vars:
                logging.info("update var is %s" % var)
                # self.run_cmd('REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v '+ var+' /t REG_EXPAND_SZ /d ' + var+'%;' + value+' /f', self.target_sid_adm)
                self.run_cmd('REG ADD "HKCU\Environment" /v '+var+' /t REG_EXPAND_SZ /d ' +actual_val+';' + value+' /f',
                             self.target_sid_adm)

    def run_cmd(self,command, sid_adm):

        try:
            output = self.conn.run_cmd(command)

            result = str(output.std_out, 'UTF-8')
            error = str(output.std_err, 'UTF-8')

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
