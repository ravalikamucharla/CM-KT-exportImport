#!/usr/bin/python3
import ast
import copy
import json
import re
import sys
import traceback
import logging
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.get_abap_version import AbapVersion
from pyrfc import Connection

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
                updatecols = dict(required=True, type='str'),
                uniquecols = dict(required=True, type='str'),
                sourcevalues = dict(required=True, type='str'),
                targetvalues = dict(required=True, type='str'),
                message=dict(required=False, type='str',default='No data in source json'),
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
        updatecols_list0 = ast.literal_eval(module.params['updatecols'])
        uniquecols_list0 = ast.literal_eval(module.params['uniquecols'])
        sourcevalues_list = module.params['sourcevalues']
        targetvalues_list = module.params['targetvalues']
        message = module.params['message']

        source_json_file = open(sourcevalues_list, "r")
        source_json = json.loads(source_json_file.read())
        source_json_file.close()

        target_json_file = open(targetvalues_list, "r")
        target_json = json.loads(target_json_file.read())
        target_json_file.close()

        logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s -%(message)s'
                    , datefmt='%d-%b-%y %H:%M:%S'
                    , filename="/tmp/sap_align_config.log", filemode='a')

        loops_length = len(source_json["OUTPUT"])
        source_file =  sourcevalues_list
        
        is_sm61 = 0
        if re.search('SM61', source_file):
            is_sm61 = 1

        if loops_length <= 1:
            sourcevalues_list = source_json["OUTPUT"][0]["DATA"]
            if len(sourcevalues_list) <= 1:
                for each_val in sourcevalues_list:
                    for ekey,eval in each_val.items():
                        if 'no data' in eval.lower() or 'no group data' in eval.lower():
                            data={"Message":message} 
                            module.exit_json(changed=True, success='True', msg=data)

        abap_input = []

        len_unique_cols = len(uniquecols_list0)
        if len_unique_cols <= 0:
            len_cols=loops_length
        else:
            len_cols = len_unique_cols
        
        # Establishing Connection with RFC module using above created required parameter objects
        if group == '_NULL':
            conn = Connection(user=username, passwd=password, ashost=hostip, sysnr=instance, client=client)
        else:
            instance = '36'+str(instance)
            conn = Connection(user=username, passwd=password, mshost=hostip, msserv=instance, client=client, group=group )
        #
        for loop in range(len_cols):
            if source_json.get("OUTPUT","") != "" and target_json.get("OUTPUT","") != "":
                if source_json["OUTPUT"][loop].get("DATA","") != "" and  target_json["OUTPUT"][loop].get("DATA","")!="":
                    data_found = True
                    sourcevalues_list = source_json["OUTPUT"][loop]["DATA"]
                    targetvalues_list = target_json["OUTPUT"][loop]["DATA"]
                    uniquecols_list = list(uniquecols_list0[loop].values())

                    targetvalues_list2 = copy.deepcopy(targetvalues_list)

                    for i, temp_dict_t in enumerate(targetvalues_list2):
                        targetvalues_list2[i].update({"ACTION":""})

                    # No data is present in source data
                    if len(list(sourcevalues_list[0].values())) < 2:
                        if len(list(targetvalues_list[0].values())) < 2:
                            for i, _ in enumerate(targetvalues_list2):
                                targetvalues_list2[i].update({"ACTION":""})
                                data_found = False
                        else:
                            for i, _ in enumerate(targetvalues_list2):
                                targetvalues_list2[i].update({"ACTION":"D"})


                    else:
                        # Getting Unique Source columns
                        source_unique_keys = []
                        for i, element in enumerate(sourcevalues_list):
                            temp_list = []
                            for key, value in element.items():
                                if key in uniquecols_list:
                                    temp_list.append(value)
                            source_unique_keys.append(temp_list)

                        # Getting Unique Target columns
                        target_unique_keys = []
                        for i, element in enumerate(targetvalues_list):
                            temp_list = []
                            for key, value in element.items():
                                if key in uniquecols_list:
                                    temp_list.append(value)
                            target_unique_keys.append(temp_list)


                        # COLUMNS THAT ARE TO BE DELETED
                        for i, element in enumerate(targetvalues_list):
                            temp_list = []
                            for key, value in element.items():
                                if key in uniquecols_list:
                                    temp_list.append(value)
                            if temp_list not in source_unique_keys:
                                targetvalues_list2[i].update({"ACTION":"D"})
                            else:
                                targetvalues_list2[i].update({"ACTION":""})


                        # COLUMNS THAT ARE TO BE INSERTED
                        for i, element in enumerate(sourcevalues_list):
                            temp_list = []
                            for key, value in element.items():
                                if key in uniquecols_list:
                                    temp_list.append(value)
                            if temp_list not in target_unique_keys:
                                temp_dict = {}
                                for key, value in element.items():
                                    temp_dict.update({key:value})
                                temp_dict.update({"ACTION":"I"})
                                targetvalues_list2.append(temp_dict)

                        # All Source Keys 
                        all_source_keys = list(sourcevalues_list[0].keys())
                        all_target_keys = list(targetvalues_list[0].keys())


                        # REPLACING KEYS WITH UPDATED COLUMNS
                        for i, element in enumerate(targetvalues_list2):
                            if is_sm61 == 1:
                                check_condition = element['ACTION'] not in ['D']
                            else:
                                check_condition = element['ACTION'] not in ['D', 'I']
                            
                            if check_condition and (uniquecols_list != []):
                                if len(updatecols_list0) > 0:
                                    for key, value in element.items():
                                        for u_key, u_value in updatecols_list0[loop].items():
                                            if key == u_key:
                                                targetvalues_list2[i].update({key:u_value})
                                                if element['ACTION'] not in ['I'] and is_sm61 == 1:
                                                    targetvalues_list2[i].update({"ACTION":"U"})
                                                elif is_sm61 == 0:
                                                    targetvalues_list2[i].update({"ACTION": "U"})
                                else:
                                    for key_t, value_t in element.items():
                                        temp_unique_t = []
                                        for uniquecol in uniquecols_list:
                                            if uniquecol in all_target_keys:
                                                temp_unique_t.append(element[uniquecol])

                                    for j, temp_dict_s in enumerate(sourcevalues_list):
                                        for key_s, value_s in temp_dict_s.items():
                                            temp_unique_s = []
                                            for uniquecol in uniquecols_list:
                                                if uniquecol in all_source_keys:
                                                    temp_unique_s.append(temp_dict_s[uniquecol])

                                        if temp_unique_s == temp_unique_t:
                                            if targetvalues_list[i] == temp_dict_s:
                                                targetvalues_list[i].update({"ACTION":""})
                                            else:
                                                if re.search('SE06', source_file):
                                                    if 'Modifiable' in targetvalues_list2[i]:  # Changed
                                                        if targetvalues_list2[i]['Modifiable'] != temp_dict_s['Modifiable']:
                                                            targetvalues_list2[i]['Modifiable'] = temp_dict_s['Modifiable']
                                                            logging.info("inside else with source temp as %s" % temp_dict_s)
                                                            targetvalues_list2[i].update({"ACTION":"U"})
                                                else:
                                                    targetvalues_list2[i] = temp_dict_s
                                                    targetvalues_list2[i].update({"ACTION": "U"})
                                            break   # Changed

                        logging.info("target value list 2 is %s" % targetvalues_list2)                            

                        if uniquecols_list == []:
                            for i, temp_dict_s in enumerate(sourcevalues_list):
                                if temp_dict_s not in targetvalues_list:
                                    temp_dict = copy.deepcopy(temp_dict_s)
                                    temp_dict.update({"ACTION":"I"})
                                    targetvalues_list2.append(temp_dict)


                        if uniquecols_list == []:
                            for i, temp_dict_t in enumerate(targetvalues_list):
                                if temp_dict_t not in sourcevalues_list:
                                    targetvalues_list2[i].update({"ACTION":"D"})


                    abap_code = []
                    data = targetvalues_list2

                    abap_obj = AbapVersion(conn, abappath,logging)
                    abap_file_ver = abap_obj.get_abap_file(abapscript)
                    logging.info("SCRIPT TO RUN : %s" %abap_file_ver)
                    with open(abappath+"//"+abap_file_ver, "r") as abap_code_file:
                        my_list = abap_code_file.read().splitlines()
                        for line in my_list:
                            abap_line = {'LINE': line}
                            abap_code.append(abap_line)

                    if data_found == True:
                        temp_string = ""
                        for key, _ in targetvalues_list2[0].items():
                            temp_string = temp_string + "|" + key
                        abap_input.append(temp_string[1:])

                        for i, dict_ in enumerate(targetvalues_list2):
                            temp_string = ""
                            for _, value in dict_.items():
                                temp_string = temp_string + "|" + value
                            abap_input.append(temp_string[1:])
                    
                    else:
                        abap_input.append("THERE IS NO DATA")
                        
                    abap_input.append("")
            

        data = abap_input[:-1]

        logging.info("data is %s" % abap_input)

        # return item from next line of code will be in dictionary format
        RESULT = conn.call('ZBASIS_RFC_ACCWRAPPER', IS_PROGRAM_LINES=abap_code, IS_INPUT=abap_input)

        # Started parsing the return data
        data = RESULT['ES_OUTPUT']
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
