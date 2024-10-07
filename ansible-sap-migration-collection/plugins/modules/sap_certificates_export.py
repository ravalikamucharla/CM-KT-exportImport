#!/usr/bin/python3
import ast
import copy
import json
import re
import sys
import traceback
import logging
from ansible.module_utils.basic import AnsibleModule
from pyrfc import Connection
from ansible.module_utils.get_abap_version import AbapVersion

def main():
    try:
        # Structure of Output dictionary
        OUTPUT_DICT = {'OUTPUT':{'STATUS':'STARTED','STEPS':[],'ERROR':'','RESULT':''}}
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
                message = dict(required=False, type='str',default='No data in source json'),
                source_info=dict(required=False, type='str',default=''),
                target_info=dict(required=False, type='str',default=''),
                source_aas_info=dict(required=False, type='str', default=''),
                target_aas_info=dict(required=False, type='str', default=''),
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
        message = module.params['message']
        source_info_input = module.params['source_info'] #opt
        if source_info_input is None:
            source_info_input = ""
        target_info_input = module.params['target_info'] #opt
        if target_info_input is None:
            target_info_input =""    
        source_aas_info_input = module.params['source_aas_info']
        if source_aas_info_input is None:
            source_aas_info_input = ""
        target_aas_info_input = module.params['target_aas_info']
        if target_aas_info_input is None:
            target_aas_info_input = ""
        source_map_str = source_info_input + "," + source_aas_info_input
        source_hostnames = source_map_str.split(",")
        target_map_str = target_info_input + "," + target_aas_info_input
        target_hostnames = target_map_str.split(",")

        source_json_file = open(sourcevalues_list, "r")
        source_json = json.loads(source_json_file.read())
        source_json_file.close()

        target_json_file = open(targetvalues_list, "r")
        target_json = json.loads(target_json_file.read())
        target_json_file.close()
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s -%(message)s'
                            , datefmt='%d-%b-%y %H:%M:%S'
                            , filename="/tmp/STRUST.log", filemode='a')
        update_cert = 0
        logging.info("Input data :%s" %module.params)

        loops_length = len(source_json["OUTPUT"])
        abap_input = []
        if loops_length <= 1:
            source_val_check=source_json["OUTPUT"][0]["DATA"]
            if len(source_val_check) <= 1:
                data = {"Message":message}
                for each in source_val_check:
                    for key,val in each.items():
                        if 'no data' in val.lower():
                            module.exit_json(changed=True, success='True', msg=data) 

        logging.info("Source json :%s" %source_json)
        logging.info("Target json :%s" %target_json)
        for s_host in source_hostnames:
            for t_host in target_hostnames:
                if s_host == t_host:
                    update_cert = 1
                    break

        if update_cert == 0:
            data = {"Message": "Source and Target hosts are different so certificates will not be added"}
            module.exit_json(changed=True, success='True', msg=data)
        else:
            for loop in range(1):
                source_empty = False
                target_empty = False

                sourcevalues_list = source_json["OUTPUT"][loop+1]["DATA"]
                targetvalues_list = target_json["OUTPUT"][loop+1]["DATA"]


                #if Source is emplty
                if len(list(sourcevalues_list[0].keys())) == 0:
                    source_empty = True
                elif len(list(sourcevalues_list[0].keys())) == 1:
                    if list(sourcevalues_list[0].keys())[0].lower() == "result":
                        source_empty = True
                    else:
                        source_empty = False
                else:
                    source_empty = False
                    

                #if Target is emplty
                if len(list(targetvalues_list[0].keys())) == 0:
                    target_empty = True
                elif len(list(targetvalues_list[0].keys())) == 1:
                    if list(targetvalues_list[0].keys())[0].lower() == "result":
                        target_empty = True
                    else:
                        target_empty = False
                else:
                    target_empty = False


                if (source_empty == True) and (target_empty == True):
                    targetvalues_list2 = []
                    
                elif (source_empty == False) and (target_empty == True):
                    targetvalues_list2 = copy.deepcopy(sourcevalues_list)

                elif (source_empty == True) and (target_empty == False):
                    targetvalues_list2 = []

                else:
                    # Apply D action for all
                    targetvalues_list2 = []

                    # this for loop is for adding adding certificate record
                    for i, temp_dict_s in enumerate(sourcevalues_list):
                        non_found = True
                        comb_unique_values_s = []
                        comb_unique_values_s.append(temp_dict_s["PSE name"])
                        comb_unique_values_s.append(temp_dict_s["Certificate name"])
                        for j, temp_dict_t in enumerate(targetvalues_list):
                            comb_unique_values_t = []
                            comb_unique_values_t.append(temp_dict_t["PSE name"])
                            comb_unique_values_t.append(temp_dict_t["Certificate name"])
                            if comb_unique_values_t == comb_unique_values_s:
                                non_found = False
                                break
                        if non_found == True:
                            targetvalues_list2.append(temp_dict_s)

                abap_code = []
                data = targetvalues_list2
                logging.info("abappath : %s" %abappath)
                abap_obj = AbapVersion(conn, abappath, logging)
                abap_file_ver = abap_obj.get_abap_file(abapscript)
                logging.info("Abap script : %s" %abap_file_ver)

                with open(abappath+"//"+abap_file_ver, "r") as abap_code_file:
                    my_list = abap_code_file.read().splitlines()
                    for line in my_list:
                        abap_line = {'LINE': line}
                        abap_code.append(abap_line)


                temp_string = ""
                if len(targetvalues_list2) > 0:
                    for key, _ in targetvalues_list2[0].items():
                        temp_string = temp_string + "|" + key
                    abap_input.append(temp_string[1:])

                    for i, dict_ in enumerate(targetvalues_list2):
                        temp_string = ""
                        for _, value in dict_.items():
                            temp_string = temp_string + "|" + value
                        abap_input.append(temp_string[1:])
                    
                    abap_input.append("")

        abap_input2 = copy.deepcopy(abap_input)
        abap_input = []
        for i, row in enumerate(abap_input2[:-1]):
            split_row = row.split("|")
            certificate = split_row[-1]
            split_row.pop()
            if i != 0:
                split_row.insert(0, "IMPORT")
                abap_input.append("|".join(split_row))
                split_certificate = certificate.split("\n")
                for ele in split_certificate:
                    limit = 0
                    combined = ""
                    for char in ele:
                        combined = combined + char
                        if limit < 254:
                            limit = limit + 1
                        else:
                            abap_input.append(combined)
                            combined = ""
                            limit = 0
                    abap_input.append(combined)
            else:
                split_row.insert(0, "ACTION")
                abap_input.append("|".join(split_row))

        data = abap_input[:]

        # Return if abap_input is empty
        if not abap_input:
            data = {"Message": "Systems are in sync. No changes required"}
            module.exit_json(changed=True, success='True', msg=data)
        logging.info("Abap input :%s" %abap_input)
        # Establishing Connection with RFC module using above created required parameter objects
        if group == '_NULL':
            conn = Connection(user=username, passwd=password, ashost=hostip, sysnr=instance, client=client)
        else:
            instance = '36'+str(instance)
            conn = Connection(user=username, passwd=password, mshost=hostip, msserv=instance, client=client, group=group )

        # return item from next line of code will be in dictionary format
        RESULT = conn.call('ZBASIS_RFC_ACCWRAPPER', IS_PROGRAM_LINES=abap_code, IS_INPUT=abap_input)

        # Started parsing the return data
        data = RESULT['ES_OUTPUT']
        logging.info("Abap output : %s" %data)
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
                        DATA_DICT.update({'TITLE':STATEMENT})
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
