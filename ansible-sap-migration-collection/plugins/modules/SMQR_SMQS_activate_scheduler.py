#!/usr/bin/python3
import json
from ansible.module_utils.basic import AnsibleModule
import re
import os
from pyrfc import Connection



# import q

def main():
    try:
        # Structure of Output dictionary
        OUTPUT_DICT = {'OUTPUT': '','ERROR':''}
        # Ansible object with parameters
        module = AnsibleModule(
            argument_spec=dict(
                hostname=dict(required=True, type='str'),
                username=dict(required=True, type='str'),
                password=dict(required=True, type='str', no_log=True),
                instance=dict(required=True, type='str'),
                client=dict(required=True, type='str'),
                group=dict(required=True, type='str'),
                abappath=dict(required=True, type='str'),
                abapscript=dict(required=True, type='str'),
                inputparam=dict(required=True, type='str'),
                message=dict(required=False, type='str', default='No data')
            )
        )

        hostname = module.params['hostname']
        username = module.params['username']
        password = module.params['password']
        instance = module.params['instance']
        client = module.params['client']
        group = module.params['group']
        abappath = module.params['abappath']
        abapscript = module.params['abapscript']
        inputparam = module.params['inputparam']
        message = module.params['message']


        # Establishing Connection with RFC module using above created required parameter objects
        if group == '_NULL':
            conn = Connection(user=username, passwd=password, ashost=hostname, sysnr=instance, client=client)
        else:
            instance = '36' + str(instance)
            conn = Connection(user=username, passwd=password, mshost=hostname, msserv=instance, client=client,
                              group=group)


        abap_code = []
        abap_input = []

        # Reading Abap Code
        # q("Abap script :%s" %(abapscript))
        with open(os.path.join(abappath,abapscript), "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)

        # This code is build for single abap script's input (Example 'EXPORT'), but can handle multiple parameters separated by ","
        inputparams = inputparam.split(',')
        data = inputparams

        final_parameters = ''
        if len(inputparams) < 1:
            pass
        else:
            for i in range(len(inputparams)):
                element_list = re.split('[:]+', inputparams[i])
                if len(element_list) > 1:
                    multi_var = element_list[0]
                    for j in range(len(element_list) - 1):
                        multi_var = multi_var + ',' + element_list[j + 1]
                    final_parameters = final_parameters + multi_var + '|'
                else:
                    if element_list[0] == '_NULL':
                        null_element = ''
                        final_parameters = final_parameters + null_element + '|'
                    else:
                        final_parameters = final_parameters + element_list[0] + '|'
            final_parameters = final_parameters[0:-1]
        abap_line = {'WA': final_parameters}
        abap_input.append(abap_line)
        data = abap_input

        # return item from next line of code will be in dictionary format
        RESULT = conn.call('ZBASIS_RFC_ACCWRAPPER', IS_PROGRAM_LINES=abap_code, IS_INPUT=abap_input)

        # Started parsing the return data
        data = RESULT['ES_OUTPUT']
        fin_output=RESULT['ES_OUTPUT']
        if RESULT['ES_OUTPUT'] == []:
            # data={"Message":message}
            # module.exit_json(changed=True, success='True', msg=data)
            raise Exception('No output received from SAP. Likely cause, can be of not passing correct parameters.')
        else:
            if fin_output[1]:
                finalop = fin_output[0]['WA'] + ' - ' +fin_output[1]['WA']
            else:
                finalop = fin_output[0]['WA']
            OUTPUT_DICT['OUTPUT']=finalop

            data = OUTPUT_DICT
        # Closing the connection
        conn.close()


        # Returning the output in Ansible standard returned format if everything run successfully.
        module.exit_json(changed=True, success='True', msg=data)
    except Exception as exceptn:
        OUTPUT_DICT['ERROR'] = exceptn
        data = OUTPUT_DICT
        # # Returning the error in Ansible standard returned format.
        module.fail_json(msg=data)

if __name__ == '__main__':
    main()
