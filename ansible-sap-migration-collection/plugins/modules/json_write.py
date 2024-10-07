#!/usr/bin/python3
import glob
import json
import logging
import os
import sys
from ansible.module_utils.basic import AnsibleModule

class JsonCreation:
    def __init__(self):
        self.final_output = {'OUTPUT': {'STATUS': 'SUCCESS', 'ERROR': ''}}
        try:
            module = AnsibleModule(
                argument_spec = dict(
                    stage = dict(required=True, type='str')
                )
            )
            stage = module.params['stage']
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s',
                                datefmt='%d-%b-%y %H:%M:%S', filename="/tmp/json_write.log", filemode='a')

            output_path = "/cm_sap_migration/"
            logging.info(output_path + "*_timing.json")
            files = glob.glob(output_path + "*_timing.json", recursive=True)
            logging.info("Files captured are: %s" % files)

            final_dict = {}
            for file in files:
                with open(file, 'r') as openfile:
                    # Reading from json file
                    dictionary = json.load(openfile)
                    final_dict.update(dictionary)
                if os.path.exists(file):
                    logging.info("inside if %s exists" % file)
                    os.remove(file)

            logging.info("final dictionary is %s" % final_dict)

            json_object = json.dumps(final_dict, ensure_ascii=False)
            with open(output_path + "ExecutionTiming_" + stage + ".json", "w") as outfile:
                outfile.write(json_object)

        except Exception as exc:
            self.final_output["OUTPUT"]['STATUS'] = "FAILURE"
            self.final_output['ERROR'] = "General exception occurred, Error :%s" % exc
            print(json.dumps(self.final_output, default=str))
            sys.exit(1)


try:
    # Creating object of class
    obj_json_creation = JsonCreation()
    print(json.dumps(obj_json_creation.final_output, default=str))
    sys.exit()
except Exception as err:
    print(err)




