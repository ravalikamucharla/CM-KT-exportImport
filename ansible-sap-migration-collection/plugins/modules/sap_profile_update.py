#!/usr/bin/python3
import ast
import copy
import json
import re
import logging
from ansible.module_utils.basic import AnsibleModule
from pyrfc import Connection


def main():

    OUTPUT_DICT = {'OUTPUT': {'STATUS': 'STARTED', 'STEPS': [], 'ERROR': '', 'RESULT': ''}}
    try:

        logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename="/tmp/sap_profile_new.log", filemode='a')

        # Ansible object with parameters
        module = AnsibleModule(
            argument_spec=dict(
                hostname=dict(required=True, type='str'),
                hostip=dict(required=True, type='str'),
                username=dict(required=True, type='str'),
                password=dict(required=True, type='str', no_log=True),
                instance=dict(required=True, type='str'),
                client=dict(required=True, type='str'),
                group=dict(required=True, type='str'),
                abappath=dict(required=True, type='str'),
                abapscript=dict(required=True, type='str'),
                inclusion_param=dict(required=True, type='str'),
                sourcevalues=dict(required=True, type='str'),
                targetvalues=dict(required=True, type='str'),
                exclude_vars_file=dict(required=True, type='str'),
                message=dict(required=False, type='str', default='No data in source json'),
            )
        )

        hostip = module.params['hostip']
        username = module.params['username']
        password = module.params['password']
        instance = module.params['instance']
        client = module.params['client']
        group = module.params['group']
        abappath = module.params['abappath']
        abapscript = module.params['abapscript']
        source_values_list = module.params['sourcevalues']
        target_values_list = module.params['targetvalues']
        inclusion_param = ast.literal_eval(module.params['inclusion_param'])
        exclude_vars_file = module.params['exclude_vars_file']
        message = module.params['message']


        source_json_file = open(source_values_list, "r")
        source_json = json.loads(source_json_file.read())
        source_json_file.close()

        target_json_file = open(target_values_list, "r")
        target_json = json.loads(target_json_file.read())
        target_json_file.close()

        # Read exclude vars file
        with open(exclude_vars_file, "r") as f:
            exclude_vars = f.read().splitlines()
        logging.info("exclude vars is %s" % exclude_vars)

        loops_length = len(source_json["OUTPUT"])
        t_loops_length = len(target_json["OUTPUT"])
        logging.info("loops length is %s" % loops_length)

        source_table_list = []
        full_source_list = []
        target_table_list = []
        full_target_list = []
        abap_input = []

        if loops_length <= 1:
            logging.info("Inside loop less size")
            source_values_list = source_json["OUTPUT"][0]["DATA"]
            if len(source_values_list) <= 1:
                for each_val in source_values_list:
                    for e_key, e_val in each_val.items():
                        if 'no data' in e_val.lower() or 'no group data' in e_val.lower():
                            data = {"Message": message}
                            module.exit_json(changed=True, success='True', msg=data)

        for loop in range(loops_length):
            source_table = source_json["OUTPUT"][loop].get("TITLE", "")
            full_source_list.append(source_table)
            if loop == 0:
                continue
            source_table_list.append(source_table)
        logging.info("source table list is %s" % source_table_list)

        for loop in range(t_loops_length):
            target_table = target_json["OUTPUT"][loop].get("TITLE", "")
            full_target_list.append(target_table)
            if loop == 0:
                continue
            target_table_list.append(target_table)
        logging.info("target file list is %s" % target_table_list)
        lst_new = [full_target_list[0]]

        source_target_dict = {}
        for table_t in target_table_list:
            for table_s in source_table_list:
                if re.findall("ASCS", table_t):
                    source_target_dict.update({table_t: "NA"})
                    if re.findall("ASCS", table_s):
                        source_target_dict.update({table_t: table_s})
                        break
                elif re.findall("ERS", table_t):
                    source_target_dict.update({table_t: "NA"})
                    if re.findall("ERS", table_s):
                        source_target_dict.update({table_t: table_s})
                        break
                elif re.findall("DEFAULT",  table_t):
                    source_target_dict.update({table_t: "NA"})
                    if re.findall("DEFAULT", table_s):
                        source_target_dict.update({table_t: table_s})
                        break
        logging.info("source target file is %s" % source_target_dict)

        for table_t in list(source_target_dict.keys()):
            if table_t in target_table_list:
                target_table_list.remove(table_t)

        for table_s in list(source_target_dict.values()):
            if table_s in source_table_list:
                source_table_list.remove(table_s)

        logging.info("source file again is %s" % source_table_list)
        logging.info("target file again is %s" % target_table_list)

        if len(target_table_list) <= len(source_table_list):
            for i, table_t in enumerate(target_table_list):
                source_target_dict.update({table_t: source_table_list[i]})
        else:
            for i, table_s in enumerate(source_table_list):
                source_target_dict.update({target_table_list[i]: table_s})

        logging.info("source target again is %s" % source_target_dict)

        for table, table_s in source_target_dict.items():
            logging.info("inside for loop with %s and %s" % (table, table_s))
            inclusion_list = copy.deepcopy(inclusion_param)
            if table_s == "NA":
                continue

            target_title_index = full_target_list.index(table)
            logging.info("target table index is %s" % target_title_index)
            target_data = target_json["OUTPUT"][target_title_index]["DATA"]

            source_title_index = full_source_list.index(table_s)
            logging.info("source table index is %s" % source_title_index)
            source_data = source_json["OUTPUT"][source_title_index]["DATA"]

            data_to_write = []
            for i, t_dict in enumerate(target_data):
                if t_dict["Parameter Name"] in inclusion_list and len(exclude_vars) > 0 \
                        and t_dict["Parameter Name"] not in exclude_vars:
                    logging.info("param %s present in inclusion list" % t_dict["Parameter Name"])
                    for j, s_dict in enumerate(source_data):
                        if s_dict["Parameter Name"] == t_dict["Parameter Name"]:
                            logging.info("key matches")
                            inclusion_list.remove(t_dict["Parameter Name"])
                            if t_dict["Parameter Value"] != s_dict["Parameter Value"]:
                                target_data[i].update({"ACTION": "U"})
                                t_dict["Parameter Value"] = s_dict["Parameter Value"]
                                data_to_write.append(t_dict)
                                lst_new.append(table)
            logging.info("remaining inclusion list %s" % inclusion_list)

            for each in inclusion_list:
                logging.info("inclusion param is %s" % each)
                for j, s_dict in enumerate(source_data):
                    if s_dict["Parameter Name"] == each and len(exclude_vars) > 0 and s_dict["Parameter Name"] \
                            not in exclude_vars:
                        logging.info("key matches in source")
                        s_dict.update({"ACTION": "I"})
                        data_to_write.append(s_dict)
                        lst_new.append(table)

            if data_to_write:
                abap_input.append("")
                abap_input.append(table)
                temp_string = ""
                for key, _ in target_data[0].items():
                    temp_string = temp_string + "|" + key
                abap_input.append(temp_string[1:])

                for i, dict_ in enumerate(data_to_write):
                    temp_string = ""
                    for _, value in dict_.items():
                        temp_string = temp_string + "|" + value
                abap_input.append(temp_string[1:])

        index = 0
        for tables in lst_new:
            abap_input.insert(index, tables)
            index = index + 1

        logging.info("abap input is %s" % abap_input)
        abap_code = []
        with open(abappath+"//"+abapscript, "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)

        # Establishing Connection with RFC module using above created required parameter objects
        if group == '_NULL':
            conn = Connection(user=username, passwd=password, ashost=hostip, sysnr=instance, client=client)
        else:
            instance = '36' + str(instance)
            conn = Connection(user=username, passwd=password, mshost=hostip, msserv=instance, client=client,
                              group=group)

        # return item from next line of code will be in dictionary format
        RESULT = conn.call('ZBASIS_RFC_ACCWRAPPER', IS_PROGRAM_LINES=abap_code, IS_INPUT=abap_input)

        # Started parsing the return data
        if not RESULT['ES_OUTPUT']:
            raise Exception('No output received from SAP. Likely cause, can be of not passing correct parameters.')
        else:
            STATEMENT_TAKEN = False
            OUTPUT_DICT_INNER = {}
            DATA_DICT = {}
            ABAP_RECORDS_LIST = []
            OUTPUT_LIST = []
            COLUMN_TAKEN = False
            DATA_TAKEN = False
            for i in range(len(RESULT['ES_OUTPUT'])):
                row = list(RESULT['ES_OUTPUT'][i].values())[0]
                if row == '':
                    STATEMENT_TAKEN = False
                    if DATA_TAKEN:
                        DATA_DICT.update({'TITLE': STATEMENT})
                        if ABAP_RECORDS_LIST:
                            DATA_DICT.update({'DATA': ABAP_RECORDS_LIST})
                        OUTPUT_LIST.append(DATA_DICT)
                        DATA_DICT = {}
                        DATA_TAKEN = False
                else:
                    if not STATEMENT_TAKEN:
                        DATA_TAKEN = True
                        ABAP_RECORDS_LIST = []
                        STATEMENT = row
                        STATEMENT_TAKEN = True
                        COLUMN_TAKEN = False
                    else:
                        if not COLUMN_TAKEN:
                            SEPARATED_COLUMNS = row.split('|')
                            COLUMN_TAKEN = True
                            if len(SEPARATED_COLUMNS) == 1:
                                ABAP_RECORDS_DICT = {}
                                ABAP_RECORDS_DICT.update({'RESULT': SEPARATED_COLUMNS[0]})
                                ABAP_RECORDS_LIST.append(ABAP_RECORDS_DICT)
                        elif len(SEPARATED_COLUMNS) > 1:
                            ABAP_RECORDS_DICT = {}
                            SEPARATED_RECORDS = row.split('|')
                            for j in range(len(SEPARATED_COLUMNS)):
                                ABAP_RECORDS_DICT.update({SEPARATED_COLUMNS[j]: SEPARATED_RECORDS[j]})
                            ABAP_RECORDS_LIST.append(ABAP_RECORDS_DICT)
                        elif len(SEPARATED_COLUMNS) == 1:
                            element_to_remove = {'RESULT': SEPARATED_COLUMNS[0]}
                            if element_to_remove in ABAP_RECORDS_LIST:
                                ABAP_RECORDS_LIST.remove(element_to_remove)
                            ABAP_RECORDS_DICT = {}
                            ABAP_RECORDS_DICT.update({SEPARATED_COLUMNS[0]: row})
                            ABAP_RECORDS_LIST.append(ABAP_RECORDS_DICT)

            if DATA_TAKEN:
                DATA_DICT.update({'TITLE': STATEMENT})
                if ABAP_RECORDS_LIST:
                    DATA_DICT.update({'DATA': ABAP_RECORDS_LIST})
                OUTPUT_LIST.append(DATA_DICT)

            OUTPUT_DICT_INNER.update({'OUTPUT': OUTPUT_LIST})

        OUTPUT_DICT['OUTPUT']['STATUS'] = 'SUCCESS'
        OUTPUT_DICT['OUTPUT']['RESULT'] = OUTPUT_DICT_INNER
        data = OUTPUT_DICT

        # Closing the connection
        conn.close()

        # Returning the output in Ansible standard returned format if everything run successfully.
        module.exit_json(changed=True, success='True', msg=data)
    except Exception as error:
        OUTPUT_DICT['OUTPUT']['STATUS'] = 'FAILED'
        OUTPUT_DICT['OUTPUT']['ERROR'] = str(error)
        data = OUTPUT_DICT
        # Returning the error in Ansible standard returned format.
        module.fail_json(msg=data)


if __name__ == '__main__':
    main()
