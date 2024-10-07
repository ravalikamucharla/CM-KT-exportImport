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

def main():
    try:
        # Structure of Output dictionary
        OUTPUT_DICT = {'OUTPUT':{'STATUS':'STARTED','STEPS':[],'ERROR':'','RESULT':''}}

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s -%(message)s'
                            , datefmt='%d-%b-%y %H:%M:%S'
                            , filename="/tmp/spad.log", filemode='a')

        logging.info("Inside sap_spad file")

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
                instancename = dict(required=True, type='str'),
                message=dict(required=False, type='str',default='No data in source json'),
                updateval=dict(required=False, type='str',default=''),
                source_info = dict(required=True, type='str'),
                target_info = dict(required=True, type='str'),
                source_aas_info = dict(required=False, type='str',default=""),
                target_aas_info = dict(required=False, type='str',default=""),

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
        instancename_list = ast.literal_eval(module.params['instancename'])
        message = module.params['message']
        updateval=module.params['updateval']
        source_info_input = module.params['source_info']
        target_info_input = module.params['target_info']
        source_aas_info_input = module.params['source_aas_info']
        target_aas_info_input = module.params['target_aas_info']
        if source_aas_info_input is None:
            source_aas_info_input = ""
        if target_aas_info_input is None:
            target_aas_info_input = ""
        if source_aas_info_input:
            source_map_str = source_info_input + "," + source_aas_info_input
        else:
            source_map_str = source_info_input
        source_info = source_map_str.split(",")
        if target_aas_info_input:
            target_map_str = target_info_input + "," + target_aas_info_input
        else:
            target_map_str = target_info_input
        target_info = target_map_str.split(",")
        source_json_file = open(sourcevalues_list, "r")
        source_json = json.loads(source_json_file.read())
        source_json_file.close()
        #Expect "NULL" in target info for those source info which are to be ignored, Filter NULL target values
        new_source_list=[]
        new_target_list=[]
        for ind,each in enumerate(target_info):
            if each.upper() != "NULL":
                new_source_list.append(source_info[ind])
                new_target_list.append(target_info[ind])
        source_info = new_source_list
        target_info = new_target_list
        target_json_file = open(targetvalues_list, "r")
        target_json = json.loads(target_json_file.read())
        target_json_file.close()

        logging.info("source info is %s" % source_info)
        logging.info("target info is %s" % target_info)

        logging.info("source json data is %s" % source_json)
        logging.info("target json data is %s" % target_json)

        loops_length = len(source_json["OUTPUT"])
        abap_input = []
        if loops_length <= 1:
            sourcevalues_list = source_json["OUTPUT"][0]["DATA"]
            if len(sourcevalues_list) <= 1:
                data={"Message":message}
                for each in sourcevalues_list:
                    for key,val in each.items():
                        if 'no data' in val.lower():
                            module.exit_json(changed=True, success='True', msg=data)
        for loop in range(loops_length):
            source_empty = False
            target_empty = False

            sourcevalues_list = source_json["OUTPUT"][loop]["DATA"]
            targetvalues_list = target_json["OUTPUT"][loop]["DATA"]

            #if Source is empty
            if len(list(sourcevalues_list[0].keys())) < 2:
                source_empty = True

            #if Target is empty
            if len(list(targetvalues_list[0].keys())) < 2:
                target_empty = True


            if loop == 0:
                if (source_empty == True) and (target_empty == True):
                    targetvalues_list2 = []

                elif (source_empty == False) and (target_empty == True):
                    targetvalues_list2 = copy.deepcopy(sourcevalues_list)
                    for i, _ in enumerate(targetvalues_list2):
                        targetvalues_list2[i].update({"ACTION":"I"})

                elif (source_empty == True) and (target_empty == False):
                    targetvalues_list2 = copy.deepcopy(targetvalues_list)
                    for i, _ in enumerate(targetvalues_list2):
                        targetvalues_list2[i].update({"ACTION":"D"})

                else:
                    instance_count = 0
                    targetvalues_list2 = copy.deepcopy(targetvalues_list)
                    for i, _ in enumerate(targetvalues_list2):
                        targetvalues_list2[i].update({"ACTION":"D"})
                        logging.info("target value list 2 is %s " % targetvalues_list2)
                    for i, temp_dict_s in enumerate(sourcevalues_list):
                        for j, temp_dict_t in enumerate(targetvalues_list):
                            if (temp_dict_s["Outputdevicename"] == temp_dict_t["Outputdevicename"]):
                                if sourcevalues_list[i]["Spoolservers"] == "NULL":
                                    targetvalues_list2[j]["Spoolservers"] = "NULL"
                                    targetvalues_list2[j].update({"ACTION":"U"})
                                else:
                                    source_spoolserver = sourcevalues_list[j]["Spoolservers"]
                                    split_data = source_spoolserver.rsplit('_', 2)
                                    source_inst_number = split_data[2]
                                    logging.info("source inst number is %s" % source_inst_number)
                                    logging.info("source info passed is %s" % source_info)
                                    target_server = get_target_info(source_inst_number, source_info, target_info)
                                    targetvalues_list2[j]["Spoolservers"] = target_server
                                    if (temp_dict_t["Spoolservers"] == "__AUTOSPOOLSERVER"):    
                                        targetvalues_list2[j].update({"ACTION": ""})
                                    else:
                                        targetvalues_list2[j].update({"ACTION": "U"})
                            elif (temp_dict_t["Spoolservers"] == "__AUTOSPOOLSERVER"):
                                targetvalues_list2[j].update({"ACTION":""})

                logging.info("target value list 2 is %s" % targetvalues_list2)
                abap_code = []

                with open(abappath+"//"+abapscript, "r") as abap_code_file:
                    my_list = abap_code_file.read().splitlines()
                    for line in my_list:
                        abap_line = {'LINE': line}
                        abap_code.append(abap_line)

                temp_string = ""
                for key, _ in targetvalues_list2[0].items():
                    temp_string = temp_string + "|" + key
                abap_input.append(temp_string[1:])
                logging.info("abap input part 1 is %s" % abap_input)

                for i, dict_ in enumerate(targetvalues_list2):
                    temp_string = ""
                    logging.info("dict is %s" % dict_)
                    for _, value in dict_.items():
                        temp_string = temp_string + "|" + value
                    abap_input.append(temp_string[1:])
                    logging.info("abap input made is %s" % abap_input)
                logging.info("abap input part 2 is %s" % abap_input)

                abap_input.append("")
                logging.info("abap input part 3 is %s" % abap_input)

        data = abap_input[:-1]
        logging.info("abap input final is %s" % data)

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
        logging.info("final result is %s" % data)
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
        logging.info("output dict is %s" % data)

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


def get_target_info(source_inst_number, source_info, target_info):
    """
    Fethcing corresponding target info for the instance number
    """
    spool_server=source_inst_number
    for count,server_info in enumerate(source_info):
        server_data = server_info.rsplit('_', 3)
        inst_num = server_data[3]
        if source_inst_number == inst_num:
            inst_name = server_data[2]
            fl = 1
            for servers_info_target in target_info:
                if re.search(inst_name, servers_info_target):
                    fl = 0
                    logging.info("inside regex match")
                    server_data_target = servers_info_target.rsplit('_', 3)
                    spool_server = server_data_target[0] + '_' + server_data_target[1] + '_' \
                        + server_data_target[3]
                    break
            if fl:
                tmp = target_info[count]
                server_data_target = tmp.rsplit('_', 3)
                spool_server = server_data_target[0] + '_' + server_data_target[1] + '_' \
                               + server_data_target[3]
                logging.info("spoolserver is %s" % spool_server)
                break
    return spool_server


if __name__ == '__main__':
    main()
