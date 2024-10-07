#!/usr/bin/python3
import ast
import copy
import json
import re
import sys
import logging
import traceback
from ansible.module_utils.basic import AnsibleModule
from pyrfc import Connection


def main():
    try:
        # Structure of Output dictionary
        OUTPUT_DICT = {'OUTPUT': {'STATUS': 'STARTED', 'STEPS': [], 'ERROR': '', 'RESULT': ''}}
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
                sourcevalues=dict(required=True, type='str'),
                targetvalues=dict(required=False, type='str',default=''),
                instancename=dict(required=True, type='str'),
                message=dict(required=False, type='str', default='No data in source json'),
                source_info=dict(required=False, type='str',default=''),
                target_info=dict(required=False, type='str',default=''),
                source_aas_info=dict(required=False, type='str', default=''),
                target_aas_info=dict(required=False, type='str', default=''),
                target_sid = dict(required=False, type='str',default=""),
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
        target_sid = module.params['target_sid'] 
        if targetvalues_list is None:
            targetvalues_list = ""    
        if target_sid is None:
            target_sid = ""
        if not targetvalues_list:
            target_instance = hostname + "_" + target_sid + "_" + instance
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
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s -%(message)s'
                            , datefmt='%d-%b-%y %H:%M:%S'
                            , filename="/tmp/sap_logon_group_smlg.log", filemode='a')

        source_map_str = source_info_input + "," + source_aas_info_input
        source_info = source_map_str.split(",")
        target_map_str = target_info_input + "," + target_aas_info_input
        target_info = target_map_str.split(",")
        instancename_list = target_info
        map_info={}
        for ind,each in enumerate(source_info):
            if "NULL" in each:
                target = target_info[ind]
                map_info.update({"%s_%s"%(each,target):target_info[ind]})
            elif 'NULL' not in target_info[ind]: #Get all keys of non NULL target values
                map_info.update({each:target_info[ind]})

        logging.info("Source info :%s" %source_info)
        logging.info("Target info :%s" %target_info)
        logging.info("Mapping dict :%s" %map_info)
        source_json_file = open(sourcevalues_list, "r")
        source_json = json.loads(source_json_file.read())
        source_json_file.close()
        logging.info("sourcce data :%s" %source_json)
        if targetvalues_list:
            target_json_file = open(targetvalues_list, "r")
            target_json = json.loads(target_json_file.read())
            target_json_file.close()
            logging.info("target data :%s" %target_json)
        else:
            target_json = {}

        sourcevalues_list = source_json["OUTPUT"][0]["DATA"]
        if target_json:
            targetvalues_list = target_json["OUTPUT"][0]["DATA"]
        else:
            targetvalues_list = []

        if len(sourcevalues_list) <= 1:
            data = {"Message": message}
            for each in sourcevalues_list:
                for key, val in each.items():
                    if 'no data' in val.lower():
                        module.exit_json(changed=True, success='True', msg=data)

        targetvalues_list2 = copy.deepcopy(targetvalues_list)
        data = targetvalues_list2

        for i, _ in enumerate(targetvalues_list):
            targetvalues_list2[i].update({"ACTION": "D"})

        source_inst_name = []
        for i, temp_dict_s in enumerate(sourcevalues_list):
            if temp_dict_s["Instance name"] not in source_inst_name:
                source_inst_name.append(temp_dict_s["Instance name"])

        instance_change_req = False
        check_if_same_data = True
        if source_inst_name != instancename_list:
            instance_change_req = True

        target_inst_name = []
        for i, temp_dict_t in enumerate(targetvalues_list):
            if temp_dict_t["Instance name"] not in target_inst_name:
                target_inst_name.append(temp_dict_t["Instance name"])

        change_required = False
        instance_count = 0
        if len(sourcevalues_list) == len(targetvalues_list):
            for i, temp_dict_s in enumerate(sourcevalues_list):
                if (temp_dict_s == targetvalues_list[i]) and (instance_change_req == False):
                    targetvalues_list2[i].update({"ACTION": ""})

                else:
                    change_required = True
                    targetvalues_list2 = copy.deepcopy(targetvalues_list)
                    break

            # REORDERING LOGON GROUP
            if change_required == True:
                for i, _ in enumerate(targetvalues_list):
                    targetvalues_list2[i].update({"ACTION": "D"})
                temp_list = []
                temp_dict = {}
                temp_source_list = sorted(sourcevalues_list, key=lambda x: x['Logon group name'].lower())
                temp_target_list = sorted(targetvalues_list2, key=lambda x: x['Logon group name'].lower())
                target_cmp = []
                for each in temp_target_list:
                    target_cmp.append({k: v.lower() if (k!= 'ACTION' and k!= 'Instance name') else v for k, v in each.items()})
                source_cmp = []
                for each in temp_source_list:
                    source_cmp.append({k: v.lower() if (k!= 'ACTION' and k!= 'Instance name') else v for k, v in each.items()})
                for ind,each in enumerate(source_cmp):
                    tmp_changed=each
                    mapped_target = map_info.get(each['Instance name'],"")
                    tmp_changed.update({'Instance name':mapped_target,'ACTION': 'D'})
                    if tmp_changed != target_cmp[ind]:
                        check_if_same_data = False
                        break
                if check_if_same_data:
                    for each in targetvalues_list2:
                        each.update({"ACTION": ""})
                else:
                    for i, temp_dict_s in enumerate(sourcevalues_list):
                        if temp_dict_s not in temp_list:
                            temp_list.append(temp_dict_s)
                            temp_dict = copy.deepcopy(temp_dict_s)
                            temp_dict.update({"ACTION": "I"})
                            targetvalues_list2.append(temp_dict)
                            for j, temp_dict_s2 in enumerate(sourcevalues_list):
                                if temp_dict_s != temp_dict_s2:
                                    if temp_dict_s["Logon group name"] == temp_dict_s2["Logon group name"]:
                                        temp_list.append(temp_dict_s2)
                                        temp_dict = copy.deepcopy(temp_dict_s2)
                                        temp_dict.update({"ACTION": "I"})
                                        targetvalues_list2.append(temp_dict)

        else:
            check_if_same_data = False
            temp_list = []
            temp_dict = {}
            for i, temp_dict_s in enumerate(sourcevalues_list):
                if temp_dict_s not in temp_list:
                    temp_dict = copy.deepcopy(temp_dict_s)
                    temp_dict.update({"ACTION": "I"})
                    if not targetvalues_list:
                        temp_dict.update({"Instance name": target_instance})
                    targetvalues_list2.append(temp_dict)
                    for j, temp_dict_s2 in enumerate(sourcevalues_list):
                        if temp_dict_s != temp_dict_s2:
                            if temp_dict_s["Logon group name"] == temp_dict_s2["Logon group name"]:
                                temp_list.append(temp_dict_s2)
                                temp_dict = copy.deepcopy(temp_dict_s2)
                                temp_dict.update({"ACTION": "I"})
                                if not targetvalues_list:
                                    temp_dict.update({"Instance name": target_instance})
                                targetvalues_list2.append(temp_dict)

        data = targetvalues_list2
        logging.info("check_if_same_data -%s" %check_if_same_data)
        # Changing the instance name
        instance_count = 0
        final_target_vals = []
        logging.info("Target values :%s" %targetvalues_list2)
        target_vals=copy.deepcopy(targetvalues_list2)
        if not check_if_same_data:
            for i, temp_dict_t in enumerate(target_vals):
                inst_name = targetvalues_list2[i]["Instance name"]
                mapped_target = map_info.get(inst_name,"")
                if temp_dict_t["ACTION"] not in ("D", ""):    
                    if mapped_target:
                        targetvalues_list2[i]["Instance name"] = mapped_target
                        targetvalues_list2[i]["ACTION"] = "I"
                        final_target_vals.append(targetvalues_list2[i])
                elif temp_dict_t["ACTION"] in ("D"):
                    logging.info("instance name :%s" %inst_name)
                    get_target = [source for source, target in map_info.items() if target == inst_name]
                    logging.info("GET TARGET :%s" %get_target)
                    chk = [each for each in get_target if each.startswith('NULL')]
                    logging.info("chk :%s" %chk)
                    if targetvalues_list2[i]["Logon group name"] == "NULL" or chk:
                        pass
                    else:
                        final_target_vals.append(target_vals[i])
                else:
                    final_target_vals.append(target_vals[i])
        else:
            final_target_vals = targetvalues_list2

        data = final_target_vals

        logging.info("final target:%s " %final_target_vals)
        abap_code = []
        abap_input = []

      
        with open(abappath + "//" + abapscript, "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)

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
        logging.info("Abap input : %s" %abap_input)
        # Establishing Connection with RFC module using above created required parameter objects
        if group == '_NULL':
            conn = Connection(user=username, passwd=password, ashost=hostname, sysnr=instance, client=client)
        else:
            instance = '36' + str(instance)
            conn = Connection(user=username, passwd=password, mshost=hostname, msserv=instance, client=client,
                              group=group)

        # return item from next line of code will be in dictionary format
        RESULT = conn.call('ZBASIS_RFC_ACCWRAPPER', IS_PROGRAM_LINES=abap_code, IS_INPUT=abap_input)

        # Started parsing the return data
        data = RESULT['ES_OUTPUT']
        logging.info("Abap Output : %s" %data)
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
                            DATA_DICT.update({'DATA': ABAP_RECORDS_LIST})
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

            if DATA_TAKEN == True:
                DATA_DICT.update({'TITLE': STATEMENT})
                if ABAP_RECORDS_LIST != []:
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
    except Exception as exceptn:
        OUTPUT_DICT['OUTPUT']['STATUS'] = 'FAILED'
        OUTPUT_DICT['OUTPUT']['ERROR'] = str(traceback.format_exc())
        data = OUTPUT_DICT
        # Returning the error in Ansible standard returned format.
        module.fail_json(msg=data)


if __name__ == '__main__':
    main()