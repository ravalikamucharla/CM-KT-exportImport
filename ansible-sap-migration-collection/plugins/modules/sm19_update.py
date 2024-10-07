#!/usr/bin/python3
import ast
import copy
import json
import sys
import logging
from ansible.module_utils.basic import AnsibleModule
from pyrfc import Connection


def main():
    try:
        # Structure of Output dictionary
        output_dict = {'OUTPUT':{'STATUS': 'STARTED', 'STEPS': [], 'ERROR': '', 'RESULT': ''}}

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s',
                            datefmt='%d-%b-%y %H:%M:%S', filename="/tmp/SM19.log", filemode='a')

        # Ansible object with parameters
        module = AnsibleModule(
            argument_spec = dict(
                hostip = dict(required=True, type='str'),
                username = dict(required=True, type='str'),
                password = dict(required=True, type='str', no_log=True),
                instance = dict(required=True, type='str'),
                client = dict(required=True, type='str'),
                group = dict(required=True, type='str'),
                abappath = dict(required=True, type='str'),
                abapscript = dict(required=True, type='str'),
                sourcevalues_list = dict(required=True, type='str'),
                targetvalues_list = dict(required=True, type='str'),
                uniquecols_list = dict(required=True, type='str'),
                message=dict(required=False, type='str',default='No data')
            )
        )

        logging.info("args done")

        hostip = module.params['hostip']
        username = module.params['username']
        password = module.params['password']
        instance = module.params['instance']
        client = module.params['client']
        group = module.params['group']
        abappath = module.params['abappath']
        abapscript = module.params['abapscript']
        sourcevalues_list = module.params['sourcevalues_list']
        targetvalues_list = module.params['targetvalues_list']
        uniquecols_list = ast.literal_eval(module.params['uniquecols_list'])
        message = module.params['message']

        logging.info("data taken")

        source_json_file = open(sourcevalues_list, "r")
        source_json = json.loads(source_json_file.read())
        source_json_file.close()

        target_json_file = open(targetvalues_list, "r")
        target_json = json.loads(target_json_file.read())
        target_json_file.close()

        sourcevalues_list = source_json["OUTPUT"][2]["DATA"]
        if len(sourcevalues_list) <= 1:
            data = {"Message": message}
            for each in sourcevalues_list:
                for key, val in each.items():
                    if 'no data' in val.lower():
                        data={"Message":message} 
                        module.exit_json(changed=True, success='True', msg=data)
        targetvalues_list = target_json["OUTPUT"][2]["DATA"]

        targetvalues_list_copy = copy.deepcopy(targetvalues_list)

        for i, temp_dict_t in enumerate(targetvalues_list_copy):
            targetvalues_list_copy[i].update({"ACTION": ""})

        logging.info("Target value copy list is %s" % targetvalues_list_copy)
        logging.info("unique list is %s" % uniquecols_list)

        # Getting Unique Source columns
        source_unique_val = []
        for i, element in enumerate(sourcevalues_list):
            temp_list = []
            for key, value in element.items():
                if key in uniquecols_list:
                    temp_list.append(value)
            source_unique_val.append(temp_list)

        # Getting Unique Target columns
        target_unique_val = []
        for i, element in enumerate(targetvalues_list):
            temp_list = []
            for key, value in element.items():
                if key in uniquecols_list:
                    temp_list.append(value)
            target_unique_val.append(temp_list)

        logging.info("source unique values is %s" % source_unique_val)
        logging.info("target unique values is %s" % target_unique_val)

        # COLUMNS THAT ARE TO BE DELETED
        for i, element in enumerate(targetvalues_list):
            temp_list = []
            for key, value in element.items():
                if key in uniquecols_list:
                    temp_list.append(value)
            logging.info("target temp list is %s" % temp_list)
            if temp_list not in source_unique_val:
                targetvalues_list_copy[i].update({"ACTION": "D"})
            else:
                logging.info("target element is %s" % targetvalues_list[i])
                for j, temp_dict_s in enumerate(sourcevalues_list):
                    logging.info("source element is %s" % temp_dict_s)
                    source_unique_val_list = []
                    for key_s, value_s in temp_dict_s.items():
                        if key_s in uniquecols_list:
                            source_unique_val_list.append(value_s)
                    logging.info("source uniq val list is %s" % source_unique_val_list)
                    if temp_list == source_unique_val_list:
                        logging.info("inside equals")
                        if targetvalues_list[i] == temp_dict_s:
                            targetvalues_list_copy[i].update({"ACTION": ""})
                            logging.info("target copy now is %s" % targetvalues_list_copy[i])
                        else:
                            logging.info("inside else")
                            targetvalues_list_copy[i] = temp_dict_s
                            targetvalues_list_copy[i].update({"ACTION": "U"})
                            logging.info("target copy now is %s" % targetvalues_list_copy[i])
                        break

        logging.info("target value list 2 again is %s" % targetvalues_list_copy)

        # COLUMNS THAT ARE TO BE INSERTED
        for i, element in enumerate(sourcevalues_list):
            temp_list = []
            for key, value in element.items():
                if key in uniquecols_list:
                    temp_list.append(value)
            if temp_list not in target_unique_val:
                temp_dict = {}
                for key, value in element.items():
                    temp_dict.update({key: value})
                temp_dict.update({"ACTION": "I"})
                targetvalues_list_copy.append(temp_dict)

        logging.info("target value list 2 again 1 is %s" % targetvalues_list_copy)

        abap_code = []
        data = targetvalues_list_copy
        abap_input = []

        with open(abappath+"//"+abapscript, "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)

        temp_string = ""
        for key, _ in targetvalues_list_copy[0].items():
            temp_string = temp_string + "|" + key
        abap_input.append(temp_string[1:])

        for i, dict_ in enumerate(targetvalues_list_copy):
            temp_string = ""
            for _, value in dict_.items():
                temp_string = temp_string + "|" + value
            abap_input.append(temp_string[1:])

        logging.info("data is %s" % abap_input)

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

        output_dict['OUTPUT']['STATUS'] = 'SUCCESS'
        output_dict['OUTPUT']['RESULT'] = OUTPUT_DICT_INNER
        data = output_dict

        # Closing the connection
        conn.close()

        # Returning the output in Ansible standard returned format if everything run successfully.
        module.exit_json(changed=True, success='True', msg=data)

    except Exception as error:
        output_dict['OUTPUT']['STATUS'] = 'FAILED'
        output_dict['OUTPUT']['ERROR'] = error
        data = output_dict
        module.fail_json(msg=data)


if __name__ == '__main__':
    main()
