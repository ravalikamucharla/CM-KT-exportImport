#!/usr/bin/python3
import ast
import copy
import json
from ansible.module_utils.basic import AnsibleModule
from pyrfc import Connection


def main():
    # Structure of Output dictionary
    output_dict = {'OUTPUT': {'STATUS': 'STARTED', 'STEPS': [], 'ERROR': '', 'RESULT': ''}}

    try:
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
                targetvalues=dict(required=True, type='str'),
                input_params_source=dict(required=True, type='str'),
                input_params_target=dict(required=True, type='str'),
                server_list_source=dict(required=True, type='str'),
                server_list_target=dict(required=True, type='str'),
                message=dict(required=False, type='str', default='No data in source json'),
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
        targetvalues_list = module.params['targetvalues']
        input_params_source = ast.literal_eval(module.params['input_params_source'])
        input_params_target = ast.literal_eval(module.params['input_params_target'])
        server_list_source = ast.literal_eval(module.params['server_list_source'])
        server_list_target = ast.literal_eval(module.params['server_list_target'])
        message = module.params['message']

        user_target_data_list = []

        target_json_file = open(targetvalues_list, "r")
        target_json = json.loads(target_json_file.read())
        target_json_file.close()

        loops_length = len(target_json["OUTPUT"])
        target_data_list = target_json["OUTPUT"][0]["DATA"]

        if loops_length <= 1:
            if len(target_data_list) <= 1:
                data = {"Message": message}
                for each in target_data_list:
                    for key, val in each.items():
                        if 'no data' in val.lower():
                            module.exit_json(changed=True, success='True', msg=data)

        for data_dict in target_data_list:
            user_defined = data_dict.get("UserDefined")
            if user_defined == "X":
                user_target_data_list.append(data_dict)

        for i, target_dict in enumerate(user_target_data_list):
            user_target_data_list[i].update({"ACTION": ""})

        # If type is list then look for the list value in all the entries of json
        for list_val in input_params_source:
            for data_dict in user_target_data_list:
                cp_data_dict = copy.deepcopy(data_dict)
                directory = data_dict.get("Directory")
                if list_val in directory:
                    # fetch index
                    index = input_params_source.index(list_val)
                    new_val = input_params_target[index]
                    new_directory = directory.replace(list_val, new_val)
                    data_dict["Directory"] = new_directory
                    data_dict.update({"ACTION": "I"})
                    cp_data_dict.update({"ACTION": "D"})
                    user_target_data_list.append(cp_data_dict)
                    break

        # Update servers in target
        if server_list_source:
            for server_name in server_list_source:
                for data_dict in user_target_data_list:
                    if data_dict["ACTION"] != "D":
                        server = data_dict.get("Server")
                        if server == server_name:
                            index = server_list_source.index(server_name)
                            target_server = server_list_target[index]
                            data_dict["Server"] = target_server
                            if data_dict["ACTION"] != "I":
                                data_dict.update({"ACTION": "I"})

        # Read code file
        abap_code = []
        with open(abappath + "//" + abapscript, "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)

        abap_input = []
        temp_string = ""
        for key, _ in user_target_data_list[0].items():
            temp_string = temp_string + "|" + key
        abap_input.append(temp_string[1:])

        for i, dict_ in enumerate(user_target_data_list):
            temp_string = ""
            for _, value in dict_.items():
                temp_string = temp_string + "|" + value
            abap_input.append(temp_string[1:])

        abap_input.append("")

        # Establishing Connection with RFC module using above created required parameter objects
        if group == '_NULL':
            conn = Connection(user=username, passwd=password, ashost=hostip, sysnr=instance, client=client)
        else:
            instance = '36' + str(instance)
            conn = Connection(user=username, passwd=password, mshost=hostip, msserv=instance, client=client,
                              group=group)

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
                    if DATA_TAKEN == True:
                        DATA_DICT.update({'TITLE': STATEMENT})
                        if ABAP_RECORDS_LIST:
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

        output_dict['OUTPUT']['STATUS'] = 'SUCCESS'
        output_dict['OUTPUT']['RESULT'] = OUTPUT_DICT_INNER

        data = output_dict

        # Closing the connection
        conn.close()

        # Returning the output in Ansible standard returned format if everything run successfully.
        module.exit_json(changed=True, success='True', msg=data)

    except Exception as error:
        output_dict['OUTPUT']['STATUS'] = 'FAILED'
        output_dict['OUTPUT']['ERROR'] = str(error)
        data = output_dict
        # Returning the error in Ansible standard returned format.
        module.fail_json(msg=data)


if __name__ == '__main__':
    main()
