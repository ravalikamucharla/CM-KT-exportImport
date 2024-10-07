#!/usr/bin/python3
import sys
import time
import warnings
import logging

warnings.filterwarnings("ignore")


class HanaTenantDBLinux:
    """Main class which include all the connections, methods
    and updating router file, restarting, stopping System
    """

    def __init__(self, login_obj, sid):
        self.ssh = login_obj.ssh
        self.auth_type = login_obj.auth_type
        self.sid = sid
        self.sid_adm = sid.lower() + 'adm'
        self.hostname = login_obj.hostname

    def action_db(self, sid, action, tenant_username, tenant_password, tenant_db_id,
                  database_sid, db_instance_number, ascsInstance):
        """Method for performing actions like
        START, STOP or STATUS on DB
        """

        try:
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s',
                                datefmt='%d-%b-%y %H:%M:%S', filename="/tmp/hana_db_log1.txt", filemode='a')
            status = ''
            if action == 'STATUS':
                status = self.check_tenant_db(db_instance_number, '0', 'GREEN', ascsInstance)

            elif action == 'START':
                status = self.start_tenant_db(database_sid, db_instance_number, ascsInstance)

            elif action == 'STOP':
                self.stop_tenant_db(database_sid, db_instance_number)

            else:
                print('Incorrect action given.')
                sys.exit(1)

            return status
        except Exception as err:
            print('Error occurred while passing', err)
            sys.exit()

    def start_tenant_db(self, database_sid, db_instance_number, ascsInstance):
        """
        For starting the Tenant DB only
        """
        logging.info("inside start db action")
        db_sid_adm = database_sid.lower() + 'adm'
        logging.info(db_sid_adm)
        if db_instance_number != '_NULL':
            start_db_cmd = '/usr/sap/hostctrl/exe/sapcontrol -nr ' + db_instance_number + ' -function StartSystem HDB'
            if self.auth_type == 'password':
                _, stdout, stderr = self.ssh.exec_command(start_db_cmd)
            elif self.auth_type in ('ppk', 'passwordandppk'):
                _, stdout, stderr = self.ssh.exec_command('sudo su - %s -c "%s"' % (db_sid_adm, start_db_cmd))
            logging.info('sudo su - %s -c "%s"' % (db_sid_adm, start_db_cmd))
            time.sleep(120)
            output = str(stdout.read(), 'utf-8')
            error = str(stderr.read(), 'utf-8')
            logging.info(output)
            if output:
                print("Starting TENANT DB process if not already running.")
                status = self.check_tenant_db(db_instance_number, '1', 'GREEN', ascsInstance)
            else:
                print("Error encountered while starting tenant DB with error:", error)
        else:
            print('Please provide the instance of tenant DB which needs to be started.')
        return status

    def stop_tenant_db(self, database_sid, db_instance_number):
        """
        For stopping the Tenant DB only
        """
        db_sid_adm = database_sid.lower() + 'adm'
        if db_instance_number != '_NULL':
            stop_db_cmd = '/usr/sap/hostctrl/exe/sapcontrol -nr ' + db_instance_number + ' -function Stop'
            if self.auth_type == 'password':
                _, stdout, stderr = self.ssh.exec_command(stop_db_cmd)
            elif self.auth_type in ('ppk', 'passwordandppk'):
                _, stdout, stderr = self.ssh.exec_command('sudo su - %s -c "%s"' % (db_sid_adm, stop_db_cmd))
            output = str(stdout.read(), 'utf-8')
            error = str(stderr.read(), 'utf-8')
            if output:
                print("Stopping HANA DB process if not already running.")
            else:
                print("Error encountered while stopping tenant DB with error:", error)
        else:
            print('Please provide the instance of tenant DB which needs to be stopped.')

    def check_tenant_db(self, db_instance_number, app_update, color_allowed, ascsInstance):
        """
        For checking the status of Tenant DB only
        """
        all_db_status = []
        service_stop = 0
        logging.info("inside check status")
        if db_instance_number == '':
           db_instance_number = ascsInstance
        if db_instance_number != '_NULL':
            status_db_cmd = '/usr/sap/hostctrl/exe/sapcontrol -nr ' + db_instance_number + ' -function GetProcessList'
            if self.auth_type == 'password':
                _, stdout, stderr = self.ssh.exec_command(status_db_cmd)
            elif self.auth_type in ('ppk', 'passwordandppk'):
                _, stdout, stderr = self.ssh.exec_command('sudo su - %s -c "%s"' % (self.sid_adm, status_db_cmd))
            #time.sleep(120)
            output = str(stdout.read(), 'utf-8')
            error = str(stderr.read(), 'utf-8')
            logging.info(output)
            if output:
                output = output.strip()
                output_list = output.split('\n')
                number_of_dbs = len(output_list) - 1
                column_list = output_list[3].split(',')
                for i in range(3, number_of_dbs):
                    db_dict = {}
                    db_dict.update({'instance': db_instance_number})
                    db_row = output_list[i + 1].split(',')
                    if db_row:
                        if db_row[2].strip() == color_allowed:
                            db_dict.update({column_list[2]: db_row[2]})
                        else:
                            service_stop = 1
                            db_dict.update({column_list[2]: db_row[2]})
                        all_db_status.append(db_dict)

                if app_update == '1' and service_stop == 0:
                    logging.info("inside app update")
                    stop_systems_cmd = '/usr/sap/hostctrl/exe/sapcontrol -nr ' + ascsInstance + ' -function StopSystem ALL'
                    if self.auth_type == 'password':
                        _, stdout, stderr = self.ssh.exec_command(stop_systems_cmd)
                    elif self.auth_type in ('ppk', 'passwordandppk'):
                        _, stdout, stderr = self.ssh.exec_command('sudo su - %s -c "%s"' % (self.sid_adm, stop_systems_cmd))
                    time.sleep(120)
                    logging.info('sudo su - %s -c "%s"' % (self.sid_adm, stop_systems_cmd))
                    output_systems = str(stdout.read(), 'utf-8')
                    logging.info("stopped all system")
                    logging.info(output_systems)
                    error = str(stderr.read(), 'utf-8')
                    if output_systems:
                        logging.info("going to check the status")
                        status_dict, not_match = self.check_tenant_db('', '0', 'GRAY', ascsInstance)
                        logging.info(service_stop)
                        if not_match == 0:
                            logging.info("going to start ascs")
                            systems_start = '/usr/sap/hostctrl/exe/sapcontrol -nr ' + ascsInstance + ' -function Start'
                            if self.auth_type == 'password':
                                _, stdout, stderr = self.ssh.exec_command(systems_start)
                            elif self.auth_type in ('ppk', 'passwordandppk'):
                                _, stdout, stderr = self.ssh.exec_command('sudo su - %s -c "%s"' % (self.sid_adm, systems_start))
                            time.sleep(120)
                            logging.info('sudo su - %s -c "%s"' % (self.sid_adm, systems_start))
                            output_system_start = str(stdout.read(), 'utf-8')
                            logging.info(output_system_start)
                            error = str(stderr.read(), 'utf-8')
                            if output_system_start:
                                self.check_tenant_db('', '0', 'GREEN', ascsInstance)
            else:
                print("Error encountered while checking status with error:", error)
        else:
            print('Please provide the correct instance of tenant DB.')
            sys.exit()
        logging.info(all_db_status)
        return all_db_status, service_stop
