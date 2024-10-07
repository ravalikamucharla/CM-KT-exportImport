#!/usr/bin/python3
import json
import logging
import os
import sys
import traceback
from general_login import Login
#from ansible.module_utils.basic import AnsibleModule
from hana_start_stop_lin import HanaTenantDBLinux


def main():
    try:
        # Structure of Output dictionary
        output_dict = {'OUTPUT':{'STATUS':'STARTED','STEPS':[],'ERROR':'','RESULT':''}}
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s',
                            datefmt='%d-%b-%y %H:%M:%S', filename="/tmp/hana_db_log1.txt", filemode='a')

        sid = (sys.argv[1].split('='))[1]
        hostname = (sys.argv[2].split('='))[1]
        username = (sys.argv[3].split('='))[1]
        password = (sys.argv[4].split('='))[1]
        instance = (sys.argv[5].split('='))[1]
        loginMechanism = (sys.argv[6].split('='))[1]
        pemFile = (sys.argv[7].split('='))[1]
        isSudoUser = (sys.argv[8].split('='))[1]
        dbSid = (sys.argv[9].split('='))[1]
        dbInstance = (sys.argv[10].split('='))[1]
        action = (sys.argv[11].split('='))[1]
        osType = (sys.argv[12].split('='))[1]
        tenantUname = (sys.argv[13].split('='))[1]
        tenantPwd = (sys.argv[14].split('='))[1]
        dbTenantId = (sys.argv[15].split('='))[1]
        ascsInstance = (sys.argv[16].split('='))[1]

        dict_status_final = {}
        if osType.upper() == 'LINUX' or osType.upper() == "WINDOWS":
            if action == 'STOP':
                login_obj = Login(hostname, username, password, osType, loginMechanism, pemFile, isSudoUser)
                lin_obj = HanaTenantDBLinux(login_obj, sid)
                lin_obj.action_db(sid, action, tenantUname, tenantPwd, dbTenantId,
                                  dbSid, dbInstance, ascsInstance)
            elif action == 'START':
                hostname_dict = {} 
                login_obj = Login(hostname, username, password, osType, loginMechanism, pemFile, isSudoUser)
                lin_obj = HanaTenantDBLinux(login_obj, sid)
                dict_status, service_mismatch = lin_obj.action_db(sid, action, tenantUname, tenantPwd, dbTenantId,
                                  dbSid, dbInstance, ascsInstance)
                hostname_dict.update({'Hostname': hostname})
                hostname_dict.update({'state': dict_status})

                dict_status_final.update({'output': [hostname_dict]})
                json_status_final = json.dumps(dict_status_final)
                logging.info(json_status_final)
                output_dict['OUTPUT']['RESULT'] = json_status_final

            elif action == 'STATUS':
                hostname_dict = {}
                login_obj = Login(hostname, username, password, osType, loginMechanism, pemFile, isSudoUser)
                lin_obj = HanaTenantDBLinux(login_obj, sid)
                dict_status, green_yellow_gray = lin_obj.action_db(sid, action, tenantUname,
                                                                   tenantPwd, dbTenantId, dbSid, dbInstance, ascsInstance)
                logging.info(dict_status)
                hostname_dict.update({'Hostname': hostname})
                hostname_dict.update({'state': dict_status})

                dict_status_final.update({'output': [hostname_dict]})
                json_status_final = json.dumps(dict_status_final)
                logging.info(json_status_final)
                for i in hostname_dict['state']:
                    if i['name'] == dbTenantId:
                        if i['dispstatus'] == 'YES':
                            logging.info('Tenant DB is up and running. Yeay !')
                        else:
                            logging.info('Tenant DB is not running.')
                #json_status_final = json.dumps(DICT_STATUS_FINAL)
                #print(json_status_final)
                output_dict['OUTPUT']['RESULT'] = json_status_final

            output_dict['OUTPUT']['STATUS'] = 'SUCCESS'

        elif osType.upper() == "WINDOWS":
            logging.info('Windows test environment not available. Try Linux for a change ?')
            output_dict['OUTPUT']['STATUS'] = 'FAILURE'

        else:
            logging.info("Incorrect operating system passed, Please for the love of God try windows or Linux.")
            output_dict['OUTPUT']['STATUS'] = 'FAILURE'

        data = output_dict
        logging.info(data)
        print(data)

    except Exception as exceptn:
        output_dict['OUTPUT']['STATUS'] = 'FAILED'
        output_dict['OUTPUT']['ERROR'] = str(traceback.format_exc())
        data = output_dict
        print(data)


if __name__ == '__main__':
    main()

