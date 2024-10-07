#!/usr/bin/python3
import json
import logging
import sys
import traceback
from general_login import Login
from mssql_action_execution import MsSqlActions


def main():
    try:
        # Structure of Output dictionary
        output_dict = {'OUTPUT': {'STATUS': 'STARTED', 'STEPS': [], 'ERROR': '', 'RESULT': ''}}
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s',
                            datefmt='%d-%b-%y %H:%M:%S', filename="/tmp/mssql_db_log.txt", filemode='a')

        hostname = (sys.argv[1].split('='))[1]
        username = (sys.argv[2].split('='))[1]
        password = (sys.argv[3].split('='))[1]
        login_mechanism = (sys.argv[4].split('='))[1]
        pem_file = (sys.argv[5].split('='))[1]
        is_sudo_user = (sys.argv[6].split('='))[1]
        db_sid = (sys.argv[7].split('='))[1]
        db_instance = (sys.argv[8].split('='))[1]
        action = (sys.argv[9].split('='))[1]
        os_type = (sys.argv[10].split('='))[1]
        ascs_instance = (sys.argv[11].split('='))[1]

        dict_status_final = {}
        if os_type.upper() == "WINDOWS":
            if action == 'STOP':
                login_obj = Login(hostname, username, password, os_type, login_mechanism, pem_file, is_sudo_user)
                exec_obj = MsSqlActions(login_obj)
                exec_obj.action_db(action, db_sid, db_instance, ascs_instance)
            elif action == 'START':
                hostname_dict = {}
                login_obj = Login(hostname, username, password, os_type, login_mechanism, pem_file, is_sudo_user)
                exec_obj = MsSqlActions(login_obj)
                dict_status, service_mismatch = exec_obj.action_db(action, db_sid, db_instance, ascs_instance)
                #print(dict_status)
                hostname_dict.update({'Hostname': hostname})
                hostname_dict.update({'state': dict_status})

                dict_status_final.update({'output': [hostname_dict]})
                json_status_final = json.dumps(dict_status_final)
                output_dict['OUTPUT']['RESULT'] = json_status_final

            output_dict['OUTPUT']['STATUS'] = 'SUCCESS'

        else:
            logging.info("Incorrect operating system passed, Please try Windows.")
            output_dict['OUTPUT']['STATUS'] = 'FAILURE'

        data = output_dict
        print(data)

    except Exception as exceptn:
        output_dict['OUTPUT']['STATUS'] = 'FAILED'
        output_dict['OUTPUT']['ERROR'] = str(traceback.format_exc())
        data = output_dict
        print(data)


if __name__ == '__main__':
    main()
