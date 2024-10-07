#!/usr/bin/python3
import ast
import copy
import json
import re
import sys
import traceback
from ansible.module_utils.get_abap_version import AbapVersion
from ansible.module_utils.basic import AnsibleModule
import logging
from pyrfc import Connection

def main():
    try:
        # Structure of Output dictionary
        OUTPUT_DICT = {'OUTPUT': {'STATUS': 'STARTED', 'STEPS': [],'ERROR': '', 'RESULT': ''}}
        # Ansible object with parameters
        module = AnsibleModule(
            argument_spec = dict(
                hostname = dict(required=True, type='str'),
                hostip = dict(required=True, type='str'),
                username = dict(required=True, type='str'),
                password = dict(required=True, type='str', no_log=True),
                instance = dict(required=True, type='str'),
                client = dict(required=True, type='str'),
                group = dict(required=True, type='str'),
                abappath = dict(required=True, type='str'),
                abapscript = dict(required=True, type='str'),
                sourcevalues = dict(required=True, type='str'),
                targetvalues = dict(required=True, type='str'),
                source_info=dict(required=True, type='str'),
                target_info=dict(required=True, type='str'),
                source_aas_info=dict(required=False, type='str', default=''),
                target_aas_info=dict(required=False, type='str', default=''),
                message=dict(required=False, type='str',default='No data in source json')
            )
        )

        hostname = module.params['hostname']
        hostip = module.params['hostip']
        username = module.params['username']
        password = module.params['password']
        instance = module.params['instance']
        client = module.params['client']
        group = module.params['group']
        abappath = module.params['abappath']
        abapscript = module.params['abapscript']
        sourcevalues_list = module.params['sourcevalues']
        targetvalues_list = module.params['targetvalues']
        source_info_input = module.params['source_info']
        target_info_input = module.params['target_info']
        source_aas_info_input = module.params['source_aas_info']
        target_aas_info_input = module.params['target_aas_info']
        message = module.params['message']

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s -%(message)s'
                            , datefmt='%d-%b-%y %H:%M:%S'
                            , filename="/tmp/rz12.log", filemode='w')
        logging.info("Ansible input: %s" %module.params)
        source_map_str = source_info_input + "," + source_aas_info_input
        source_info = source_map_str.split(",")
        target_map_str = target_info_input + "," + target_aas_info_input
        target_info= target_map_str.split(",")
        instancename_list = target_info
        map_info={}
        for ind,each in enumerate(source_info):
            if "NULL" in each:
                target = target_info[ind]
                map_info.update({"%s_%s"%(each,target):target_info[ind]})
            elif 'NULL' not in target_info[ind]: #Get all keys of non NULL target values
                map_info.update({each:target_info[ind]})
        logging.info("Mapping dict :%s" %map_info)
        source_json_file = open(sourcevalues_list, "r")
        source_json = json.loads(source_json_file.read())
        source_json_file.close()

        target_json_file = open(targetvalues_list, "r")
        target_json = json.loads(target_json_file.read())
        target_json_file.close()

        abap_input = []

        source_empty = False
        target_empty = False

        sourcevalues_list = source_json["OUTPUT"][0]["DATA"]
        targetvalues_list = target_json["OUTPUT"][0]["DATA"]
        logging.info("sourcevalues_list :%s" %sourcevalues_list)
        logging.info("targetvalues_list :%s" %targetvalues_list)
        # if Source is empty
        if len(list(sourcevalues_list[0].keys())) < 2:
            source_empty = True

        # if Target is empty
        if len(list(targetvalues_list[0].keys())) < 2:
            target_empty = True

        # Comparison Started
        if (source_empty == True) and (target_empty == True):
            targetvalues_list2 = []

        elif (source_empty == False) and (target_empty == True):
            targetvalues_list2 = copy.deepcopy(sourcevalues_list)
            for i, _ in enumerate(targetvalues_list2):
                targetvalues_list2[i].update({"ACTION": "I"})

        elif (source_empty == True) and (target_empty == False):
            targetvalues_list2 = copy.deepcopy(targetvalues_list)
            for i, _ in enumerate(targetvalues_list2):
                targetvalues_list2[i].update({"ACTION": "D"})

        else:
            targetvalues_list2 = copy.deepcopy(targetvalues_list)
            for i, _ in enumerate(targetvalues_list2):
                targetvalues_list2[i].update({"ACTION": "D"})

            for i, temp_dict_s in enumerate(sourcevalues_list):
                temp_dict = copy.deepcopy(temp_dict_s)
                temp_dict.update({"ACTION": "I"})
                targetvalues_list2.append(temp_dict)

        final_target_vals = []
        target_vals=copy.deepcopy(targetvalues_list2)
        for i, temp_dict_t in enumerate(target_vals):
            app_server = targetvalues_list2[i]["ApplServer"]
            if temp_dict_t["ACTION"] not in ("D", ""):
                mapped_target = map_info.get(app_server,"")
                if mapped_target:
                    index_val = source_info.index(app_server)
                    targetvalues_list2[i]["ApplServer"] = mapped_target
                    targetvalues_list2[i]["ApplicationServer"] = instancename_list[index_val]
                    final_target_vals.append(targetvalues_list2[i])
            elif temp_dict_t["ACTION"] in ("D"):
                get_target = [source for source, target in map_info.items() if target == app_server]
                chk = [each for each in get_target if each.startswith('NULL')]
                if targetvalues_list2[i]["Classname"] == "NULL" or chk:
                    pass
                else:
                    final_target_vals.append(target_vals[i])
            else:
                final_target_vals.append(target_vals[i])

        temp_string = ""
        for key, _ in targetvalues_list2[0].items():
            temp_string = temp_string + "|" + key
        abap_input.append(temp_string[1:])

        for i, dict_ in enumerate(final_target_vals):
            temp_string = ""
            for _, value in dict_.items():
                temp_string = temp_string + "|" + value
            abap_input.append(temp_string[1:])


        data = abap_input

        # Establishing Connection with RFC module using above created required parameter objects
        if group == '_NULL':
            conn = Connection(user=username, passwd=password, ashost=hostip, sysnr=instance, client=client)
        else:
            instance = '36'+str(instance)
            conn = Connection(user=username, passwd=password, mshost=hostip, msserv=instance, client=client, group=group )

        abap_code = []
        logging.info("abappath : %s" %abappath)
        abap_obj = AbapVersion(conn, abappath, logging)
        abap_file_ver = abap_obj.get_abap_file(abapscript)
        logging.info("Abap script : %s" %abap_file_ver)
        with open(abappath + "//" + abap_file_ver, "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)
        logging.info("Abap input is :%s" %abap_input)
        # return item from next line of code will be in dictionary format
        RESULT = conn.call('ZBASIS_RFC_ACCWRAPPER', IS_PROGRAM_LINES=abap_code, IS_INPUT=abap_input)

        # Started parsing the return data
        data = RESULT['ES_OUTPUT']
        logging.info("Abap output is :%s" %data)
        if RESULT['ES_OUTPUT'] == []:
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
                    if DATA_TAKEN == True:
                        DATA_DICT.update({'TITLE': STATEMENT})
                        if ABAP_RECORDS_LIST != []:
                            DATA_DICT.update({'DATA':ABAP_RECORDS_LIST})
                        OUTPUT_LIST.append(DATA_DICT)
                        DATA_DICT = {}
                        DATA_TAKEN = False
                else:
                    if STATEMENT_TAKEN == False:
                        DATA_TAKEN = True
                        ABAP_RECORDS_LIST = []
                        STATEMENT = row
                        STATEMENT_TAKEN = True
                        COLUMN_TAKEN = False
                    else:
                        if COLUMN_TAKEN == False:
                            SEPARATED_COLUMNS = row.split('|')
                            COLUMN_TAKEN = True
                            if len(SEPARATED_COLUMNS) == 1:
                                ABAP_RECORDS_DICT = {}
                                ABAP_RECORDS_DICT.update({'RESULT':SEPARATED_COLUMNS[0]})
                                ABAP_RECORDS_LIST.append(ABAP_RECORDS_DICT)
                        elif len(SEPARATED_COLUMNS) > 1:
                            ABAP_RECORDS_DICT = {}
                            SEPARATED_RECORDS = row.split('|')
                            for j in range(len(SEPARATED_COLUMNS)):
                                ABAP_RECORDS_DICT.update({SEPARATED_COLUMNS[j]:SEPARATED_RECORDS[j]})
                            ABAP_RECORDS_LIST.append(ABAP_RECORDS_DICT)
                        elif len(SEPARATED_COLUMNS) == 1:
                            element_to_remove = {'RESULT':SEPARATED_COLUMNS[0]}
                            if element_to_remove in ABAP_RECORDS_LIST:
                                ABAP_RECORDS_LIST.remove(element_to_remove)
                            ABAP_RECORDS_DICT = {}
                            ABAP_RECORDS_DICT.update({SEPARATED_COLUMNS[0]:row})
                            ABAP_RECORDS_LIST.append(ABAP_RECORDS_DICT)

            if DATA_TAKEN == True:
                DATA_DICT.update({'TITLE':STATEMENT})
                if ABAP_RECORDS_LIST != []:
                    DATA_DICT.update({'DATA':ABAP_RECORDS_LIST})
                OUTPUT_LIST.append(DATA_DICT)


            OUTPUT_DICT_INNER.update({'OUTPUT':OUTPUT_LIST})

        OUTPUT_DICT['OUTPUT']['STATUS'] = 'SUCCESS'
        OUTPUT_DICT['OUTPUT']['RESULT'] = OUTPUT_DICT_INNER

        data = OUTPUT_DICT

        # Closing the connection
        conn.close()

        # Returning the output in Ansible standard returned format if everything run successfully.
        module.exit_json(changed=True, success='True', msg=data)
    except Exception as exceptn:
        OUTPUT_DICT['OUTPUT']['STATUS'] = 'FAILED'
        OUTPUT_DICT['OUTPUT']['ERROR'] = str(traceback.format_exc())
        data = OUTPUT_DICT
        # Returning the error in Ansible standard returned format.
        module.fail_json(msg=data)

if __name__ == '__main__':
    main()
