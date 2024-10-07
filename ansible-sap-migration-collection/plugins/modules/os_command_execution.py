#!/usr/bin/python3
import logging
from ansible.module_utils.basic import AnsibleModule
from pyrfc import Connection


def main():

    try:
        # Ansible object with parameters
        module = AnsibleModule(
            argument_spec=dict(
                hostip=dict(required=True, type='str'),
                username=dict(required=True, type='str'),
                password=dict(required=True, type='str', no_log=True),
                instance=dict(required=True, type='str'),
                client=dict(required=True, type='str'),
                group=dict(required=True, type='str'),
                abappath=dict(required=True, type='str'),
                abapscript=dict(required=True, type='str'),
                input_params=dict(required=True, type='str'),
                command=dict(required=True, type='str'),
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
        command = module.params['command']
        input_params = module.params['input_params']

        # Structure of Output dictionary
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s -%(message)s', datefmt='%d-%b-%y %H:%M:%S',
                            filename="./os_command_execution.log", filemode='a')

        abap_code = []
        abap_input = []

        with open(abappath+"//"+abapscript, "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)

        input_params = input_params.split(',')

        final_parameters = ''
        if len(input_params) < 1:
            pass
        else:
            final_parameters = input_params[0] + '|' + command
        abap_line = {'WA': final_parameters}
        abap_input.append(abap_line)
        logging.info("abap input is %s" % abap_input)

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
            output_str = ""
            for i in range(len(RESULT['ES_OUTPUT'])):
                row = list(RESULT['ES_OUTPUT'][i].values())[0]
                if output_str != "":
                    output_str = output_str + "\n"
                output_str = output_str + row

        data = output_str

        # Closing the connection
        conn.close()

        # Returning the output in Ansible standard returned format if everything run successfully.
        module.exit_json(changed=True, success='True', msg=data)
    except Exception as error:
        data = str(error)
        # Returning the error in Ansible standard returned format.
        module.fail_json(msg=data)


if __name__ == '__main__':
    main()
