#!/usr/bin/python3
import ast
import copy
import json
import re
import sys
import traceback
from ansible.module_utils.basic import AnsibleModule
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
                sourcevalues = dict(required=True, type='str'),
                targetvalues = dict(required=True, type='str'),
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
        message = module.params['message']

        source_json_file = open(sourcevalues_list, "r")
        source_json = json.loads(source_json_file.read())
        source_json_file.close()

        target_json_file = open(targetvalues_list, "r")
        target_json = json.loads(target_json_file.read())
        target_json_file.close()

        abap_input = []


        # SECOND TABLE
        sourcevalues_list = source_json["OUTPUT"][1]["DATA"]
        targetvalues_list = target_json["OUTPUT"][1]["DATA"]
        if len(sourcevalues_list) <= 1:
            data={"Message":message} 
            for each in sourcevalues_list:
                for key,val in each.items():
                    if 'no data' in val.lower():
                        module.exit_json(changed=True, success='True', msg=data) 
                        
        data = sourcevalues_list

        targetvalues_list2 = copy.deepcopy(targetvalues_list)
        new_target_list2 = []
        for i, temp_dict_t in enumerate(targetvalues_list2):
            for j, temp_dict_s in enumerate(sourcevalues_list):
                if temp_dict_t["Operation mode"] == temp_dict_s["Operation mode"]:
                    if temp_dict_t["Total work pro"] == temp_dict_s["Total work pro"]:
                        temp_dict_t["Dialog work pro"] = temp_dict_s["Dialog work pro"]
                        temp_dict_t["Background work pro"] = temp_dict_s["Background work pro"]
                        new_target_list2.append(temp_dict_t)

                    else:
                        remaining_cpus = int(temp_dict_t["Total work pro"]) - (int(temp_dict_t["Dialog work pro"]) + int(temp_dict_t["Background work pro"]))

                        temp_dict_t["Dialog work pro"] = round(int(temp_dict_t["Total work pro"])*(int(temp_dict_s["Dialog work pro"])/int(temp_dict_s["Total work pro"])))
                        temp_dict_t["Background work pro"] = round(int(temp_dict_t["Total work pro"])*(int(temp_dict_s["Background work pro"])/int(temp_dict_s["Total work pro"])))

                        while True:
                            if (remaining_cpus + int(temp_dict_t["Dialog work pro"]) + int(temp_dict_t["Background work pro"])) == int(temp_dict_t["Total work pro"]):
                                break
                            elif (remaining_cpus + int(temp_dict_t["Dialog work pro"]) + int(temp_dict_t["Background work pro"])) < int(temp_dict_t["Total work pro"]):
                                temp_dict_t["Dialog work pro"] = int(temp_dict_t["Dialog work pro"]) + 1
                            else:
                                temp_dict_t["Background work pro"] = int(temp_dict_t["Background work pro"]) - 1
                        new_target_list2.append(temp_dict_t)

        abap_code = []
        targetvalues_list2 = new_target_list2
        data = targetvalues_list2

        with open(abappath+"//"+abapscript, "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)


        temp_string = ""
        for key, _ in targetvalues_list2[0].items():
            temp_string = temp_string + "|" + key
        abap_input.append(temp_string[1:])

        for i, dict_ in enumerate(targetvalues_list2):
            temp_string = ""
            for _, value in dict_.items():
                if value == "NULL":
                    temp_string = temp_string + "|"
                else:
                    temp_string = temp_string + "|" + str(value)
            temp_string = temp_string + "|U" 
            abap_input.append(temp_string[1:])
        
            
        abap_input.append("")
        abap_input.insert(0, "")
            

        data = abap_input[:-1]


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
