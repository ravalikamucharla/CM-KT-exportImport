#!/usr/bin/python3
import re
import six
import sys
import warnings
import logging

warnings.filterwarnings("ignore")


class MsSqlActions:
    """Main class which include all the execution of actions
    """

    def __init__(self, login_obj):
        self.conn = login_obj.conn

    def action_db(self, action, database_sid, db_instance, ascs_instance):
        """Method for performing actions like
        START, STOP or STATUS on DB
        """

        try:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s',
                                datefmt='%d-%b-%y %H:%M:%S', filename="/tmp/mssql_db_log.txt", filemode='a')
            status = ''
            if action == 'START':
                status = self.start_mssql_db(database_sid, db_instance, ascs_instance)

            elif action == 'STOP':
                self.stop_mssql_db(database_sid, db_instance)

            else:
                print('Incorrect action given.')
                sys.exit(1)

            return status
        except Exception as err:
            print('Error occurred while passing', err)
            sys.exit()

    def start_mssql_db(self, database_sid, db_instance, ascs_instance):
        """
        For starting the DB only
        """
        logging.info("inside start db action")
        logging.info(database_sid)
        if db_instance != '_NULL':
            logging.info("inside not null")
            host_out = self.conn.run_ps('hostname')
            retcode, stdout, stderr = host_out.status_code, six.ensure_str(host_out.std_out),\
                six.ensure_str(host_out.std_err)
            hostname = stdout.strip()
            start_db_cmd = 'sqlcmd -S ' + hostname + ' -d master -Q "use master;' + \
                           'ALTER  DATABASE ' + database_sid + ' SET ONLINE"'
            logging.info(start_db_cmd)
            start_out = self.conn.run_cmd(start_db_cmd)
            retcode, stdout, stderr = start_out.status_code, six.ensure_str(start_out.std_out),\
                six.ensure_str(start_out.std_err)
            logging.info(stdout)
            if stdout:
                print("Starting MSSQL DB")
                status = self.check_status(db_instance, '1', '', ascs_instance, hostname, database_sid)
            else:
                print("Error encountered while starting DB")
        else:
            print('Please provide the instance of DB which needs to be started.')
        return status

    def stop_mssql_db(self, database_sid, db_instance):
        """
        For stopping the DB only
        """
        if db_instance != '_NULL':
            hostname = self.login_obj.run_cmd('hostname')
            stop_db_cmd = 'sqlcmd -S ' + hostname + ' -d master -Q "use master;' + \
                          'ALTER  DATABASE ' + database_sid + ' SET OFFLINE"'
            output = self.login_obj.run_cmd(stop_db_cmd)
            logging.info(stop_db_cmd)
            if output:
                print("Stopping MSSQL DB")
            else:
                print("Error encountered while stopping tenant DB with error:")
        else:
            print('Please provide the instance of DB which needs to be stopped.')

    def check_status(self, db_instance, app_update, color_allowed, ascs_instance, hostname, database_sid):
        """
        For checking the status of DB
        """
        all_db_status = []
        all_db_dict = []
        service_stop = 0
        logging.info("inside check status")
        if db_instance == '':
            db_instance = ascs_instance
        if db_instance != '_NULL':
            logging.info("db instance is not null")
            status_db_cmd = 'sqlcmd -S ' + hostname + ' -d master -Q "use master;' + \
                            'SELECT name FROM master.sys.databases WHERE name = \'' + \
                            database_sid + '\' AND state_desc = \'ONLINE\'"'
            if app_update == '1':
                status_out = self.conn.run_cmd(status_db_cmd)
                retcode, stdout, stderr = status_out.status_code, six.ensure_str(status_out.std_out), \
                    six.ensure_str(status_out.std_err)
                logging.info(stdout)
                if stdout:
                    output = stdout.strip()
                    instance = re.search(database_sid, output)
                    if instance:
                        print("DB started successfully")
                        all_db_status.append(db_instance)
                    else:
                        print("DB not started")
                        sys.exit()
            elif app_update == '0':
                status_system_cmd = "C:/\"Program Files\"/SAP/hostctrl/exe/sapcontrol.exe"\
                                    " -prot PIPE sapcontrol.exe -nr "\
                                    + ascs_instance + " -function GetProcessList"
                sys_out = self.conn.run_cmd(status_system_cmd)
                retcode, stdout, stderr = sys_out.status_code, six.ensure_str(sys_out.std_out), \
                    six.ensure_str(sys_out.std_err)
                logging.info(stdout)
                if stdout:
                    output = stdout.strip()
                    output_list = output.split('\n')
                    number_of_dbs = len(output_list) - 1
                    column_list = output_list[3].split(',')
                    for i in range(3, number_of_dbs):
                        db_dict = {}
                        db_dict.update({'instance': db_instance})
                        db_row = output_list[i + 1].split(',')
                        if db_row:
                            db_dict.update({column_list[0]: db_row[0]})
                            db_dict.update({column_list[1]: db_row[1]})
                            if db_row[2].strip() == color_allowed:
                                db_dict.update({column_list[2]: db_row[2]})
                            else:
                                service_stop = 1
                                # if status color does not matches with color_allowed, run the command again
                                status_output, _ = self.check_status(db_instance, app_update, color_allowed,
                                                                     ascs_instance, hostname, database_sid)
                                break
                            all_db_dict.append(db_dict)

                    if service_stop == 0:
                        all_db_status = all_db_dict
                    else:
                        all_db_status = status_output

            if app_update == '1' and service_stop == 0:
                logging.info("inside app update")
                stop_systems_cmd = "C:/\"Program Files\"/SAP/hostctrl/exe/sapcontrol.exe -prot PIPE -nr "\
                                   + ascs_instance + " -function StopSystem ALL"
                logging.info(stop_systems_cmd)
                stop_sys_out = self.conn.run_cmd(stop_systems_cmd)
                retcode, stdout, stderr = stop_sys_out.status_code, six.ensure_str(stop_sys_out.std_out), \
                    six.ensure_str(stop_sys_out.std_err)
                logging.info("stopped all system")
                logging.info(stdout)
                if stdout:
                    logging.info("going to check the status")
                    status_dict, not_match = self.check_status('', '0', 'GRAY', ascs_instance, hostname,
                                                               database_sid)
                    logging.info(status_dict)
                    if status_dict:
                        logging.info("going to start ascs")
                        systems_start = "C:/\"Program Files\"/SAP/hostctrl/exe/sapcontrol.exe"\
                                        " -prot PIPE -nr " + ascs_instance + " -function Start"
                        output_system_start = self.conn.run_cmd(systems_start)
                        retcode, stdout, stderr = output_system_start.status_code, \
                            six.ensure_str(output_system_start.std_out), \
                            six.ensure_str(output_system_start.std_err)
                        logging.info(stdout)
                        if stdout:
                            output, _ = self.check_status('', '0', 'GREEN', ascs_instance, hostname, database_sid)
                            all_db_status.append(output)
                            print(all_db_status)
        else:
            print('Please provide the correct instance of DB.')
            sys.exit()

        return all_db_status, service_stop
