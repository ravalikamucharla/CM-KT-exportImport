#!/usr/bin/python3
import datetime
import json
from ansible.module_utils.basic import AnsibleModule
import re
import sys
import copy
from pyrfc import Connection
import traceback
import logging
from ansible.module_utils.SAP_general_login import SAPLogin
from ansible.module_utils.get_abap_version import AbapVersion
def modify_abap_output(module,logging,abap_output,column_map,script_name):
    try:
        scrval=column_map.get(script_name,"")
        logging.info("script name :%s" %scrval)
        colvals=[]
        logging.info("Type :%s" %type(scrval))
        if len(scrval) == 1:
            logging.info("in check")
            scrkeys = scrval.keys()
            tabnostr = list(scrkeys)[0]
            colvals = scrval[tabnostr]
            tabno=int(tabnostr)
            logging.info("Table to check :%s" %tabno)
            logging.info("Columns expected :%s" %colvals)
        new_output=[]
        count = 1
        new_head=[]
        new_val=[]
        start_ind = 1
        logging.info("Abap output is:%s" %abap_output)
        cp_abap_op=copy.deepcopy(abap_output)
        proc_ind = 0
        for proc_ind,eachitem in enumerate(abap_output):
            if tabno > 1:
                new_output.append(eachitem)
                if eachitem['WA'] == '':
                    count = count + 1
                    if count == tabno:
                        start_ind = proc_ind+2
                        break
        if tabno > 1:
            new_output.append({'WA':''})
            proc_ind += 2
        #Append title
        new_output.append(abap_output[start_ind-1])

        logging.info("start ind is :%s" %start_ind)
        #Get the header
        headentry = abap_output[start_ind]       
        logging.info("head entry :%s" %headentry)
        lstsub = []
        if "|" in headentry:
            lsthead=headentry.split("|")
            lstsub=list(set(colvals)-set(lsthead))
        logging.info("Missing columns :%s" %lstsub)
        proc_start = 0
        if lstsub:
            for proc_ind1,eachitem in abap_output[proc_ind:]:
                new_val = []
                new_head = []
                logging.info("Each row to process :%s" %eachitem)
                #Start with columns
                colentry = eachitem['WA']
                if  colentry != '' and "|" in colentry:
                    colsplt = colentry.split("|")
                    for newind,eachmatch in enumerate(colvals):
                        if eachmatch in lstsub: #column missing
                            new_val.append('NULL')
                        else:
                            new_val.append(colsplt[newind])
                        new_head.append(eachmatch)
                    if proc_start == 0:
                        proc_start = 1
                        heading = "|".join(new_head)
                        new_output.append({'WA':heading})
                    columns_append="|".join(new_val)
                    new_output.append({'WA':columns_append})
                         
                    
        else:
            return abap_output

        if proc_ind1 < len(abap_output) -1:            
            for ind,eachitem in enumerate(abap_output)[proc_ind1:]:
                new_output.append(eachitem)
        if new_output:
            return new_output
        else:
            return abap_output

    except Exception as err:
        OUTPUT_DICT = {'OUTPUT':{'STATUS':'STARTED','STEPS':[],'ERROR':'','RESULT':''}}
        OUTPUT_DICT['OUTPUT']['STATUS'] = 'FAILED'
        OUTPUT_DICT['OUTPUT']['ERROR'] = err
        data = OUTPUT_DICT
        # Returning the error in Ansible standard returned format.
        module.fail_json(msg=data)
                            


def read_title_column_jsons(json_path):
    try:
        with open(json_path+"//"+"title_json.json", "r") as json_title_file:
                title_list = json.load(json_title_file)
        with open(json_path+"//"+"column_mapping.json", "r") as json_col_file:
                column_list = json.load(json_col_file)
                return title_list,column_list
                    
    except FileNotFoundError as err:
        empty_json={}
        return empty_json,empty_json

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
                password = dict(required=False, type='str', default='', no_log=True),
                instance = dict(required=True, type='str'),
                client = dict(required=False, type='str', default=''),
                group = dict(required=False, type='str', default=''),
                abappath = dict(required=True, type='str'),
                abapscript = dict(required=True, type='str'),
                outputspath = dict(required=True, type='str'),
                inputparams = dict(required=True, type='str'),
                message=dict(required=False, type='str',default='No data'),
                sncpartnername = dict(required=False, type='str', default='')
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
        outputspath = module.params['outputspath']
        inputparams = module.params['inputparams']
        message = module.params['message']
        sncpartnername = module.params['sncpartnername']

        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(levelname)s -%(message)s'
                            , datefmt='%d-%b-%y %H:%M:%S'
                            , filename="/tmp/sap_pyrfc.log", filemode='a')

        data_dict = {}
        data_list = []  
        start_time = datetime.datetime.now()
        start_date_time = start_time.strftime("%m/%d/%Y %H:%M:%S")
        data_list.insert(0, start_date_time)
        logging.info("Abap script : %s" %abapscript)
        # Establishing Connection with RFC module using above created required parameter objects
        if sncpartnername:
            LoginObj = SAPLogin(hostip, instance,username,group, password,client,sncpartnername)
        else:
            LoginObj = SAPLogin(hostip, instance,username,group, password,client)
        conn = LoginObj.Connect_SAP()
        logging.info("Successfully established connection to host - %s " %hostname)
        logging.info("SAP pyrfc execution log")
        logging.info("Abap path is :%s" %abappath)
        title_mapping,column_mapping = read_title_column_jsons(abappath)
        logging.info("Title mapping :%s" %title_mapping)
        logging.info("Column mapping :%s" %column_mapping)
        abap_obj = AbapVersion(conn, abappath,logging)
        abap_file_ver = abap_obj.get_abap_file(abapscript)
        logging.info("SCRIPT TO RUN : %s" %abap_file_ver)
        if not abap_file_ver and 'ZBASIS_R_BASIS_COMPONENT' not in abapscript.upper():
            try:
                OUTPUT_DICT={'OUTPUT':{}}
                # Exiting execution, unable to fetch supporting version script.
                tmp=[{"TITLE":"Blocked Transactions","DATA":[{"RESULT":"This Tcode is not applicable for version - %s -" %abap_obj.abapver}]}]
                OUTPUT_DICT['OUTPUT']['OUTPUT'] = tmp
                
                data = OUTPUT_DICT
                conn.close()
                end_time = datetime.datetime.now()
                end_date_time = end_time.strftime("%m/%d/%Y %H:%M:%S")
                data_list.insert(1, end_date_time)
                data_dict.update({abapscript: data_list})
                logging.info("Data dict is :%s" %data_dict)
                # insert time in json file
                file = open("/cm_sap_migration/" + abapscript.split(".")[0] + "_timing.json", "w")
                file.write(json.dumps(data_dict, ensure_ascii=False))
                file.close()
                logging.info("Wrote timestamp")
                logging.info("Message : %s written to output path: %s" %(OUTPUT_DICT['OUTPUT'],outputspath))
                fo = open(outputspath + abapscript.split(".")[0]+".json", "w")
                fo.write(json.dumps(OUTPUT_DICT['OUTPUT'], ensure_ascii=False))
                fo.close()
                logging.info("Finished writing to file")
                module.exit_json(changed=True, success='True', msg=data)
            except Exception as err:
                logging.info("Exception :%s" %err)
        data = inputparams
        abap_code = []
        abap_input = []

        # Reading Abap Code       
        with open(abappath+"//"+abap_file_ver, "r") as abap_code_file:
            my_list = abap_code_file.read().splitlines()
            for line in my_list:
                abap_line = {'LINE': line}
                abap_code.append(abap_line)
        
        # This code is build for single abap script's input (Example 'EXPORT'), but can handle multiple parameters separated by ","
        inputparams = inputparams.split(',')
        data = inputparams

        final_parameters = ''
        if len(inputparams) < 1:
            pass
        else:
            for i in range(len(inputparams)):
                element_list = re.split('[:]+', inputparams[i])
                if len(element_list) > 1:
                    multi_var = element_list[0]
                    for j in range(len(element_list)-1):
                        multi_var = multi_var + ',' + element_list[j+1]
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
        logging.info("abap input is %s" % abap_input)

        # return item from next line of code will be in dictionary format
        RESULT = conn.call('ZBASIS_RFC_ACCWRAPPER', IS_PROGRAM_LINES=abap_code, IS_INPUT=abap_input)

        # Started parsing the return data
        data = RESULT['ES_OUTPUT']
        logging.info("check message")
        logging.info("output data is %s" % data)
        if RESULT['ES_OUTPUT'] == []:
            raise Exception('No output received from SAP. Likely cause, can be of not passing correct parameters.')
        else:
  
            abap_op = RESULT['ES_OUTPUT']
            if len(abap_op) == 3 and "|" not in abap_op[1].get('WA',''):
                title=abap_op[0].get('WA','')
                dataop = abap_op[2].get('WA','')
                OUTPUT_DICT={"OUTPUT":{'OUTPUT':[]}}
                OUTPUT_DICT['OUTPUT']['OUTPUT'] = [{"TITLE":title,"DATA":[{"Message":dataop}]}]
                conn.close()
                end_time = datetime.datetime.now()
                end_date_time = end_time.strftime("%m/%d/%Y %H:%M:%S")
                data_list.insert(1, end_date_time)
                data_dict.update({abapscript: data_list})
                logging.info("Data dict is :%s" %data_dict)
                # insert time in json file
                file = open("/cm_sap_migration/" + abapscript.split(".")[0] + "_timing.json", "w")
                file.write(json.dumps(data_dict, ensure_ascii=False))
                file.close()
                logging.info("Wrote timestamp")
                logging.info("Message : %s written to output path: %s" %(OUTPUT_DICT['OUTPUT'],outputspath))
                fo = open(outputspath + abapscript.split(".")[0]+".json", "w")
                fo.write(json.dumps(OUTPUT_DICT['OUTPUT'], ensure_ascii=False))
                fo.close()
                logging.info("Finished writing to file")
                module.exit_json(changed=True, success='True', msg=data)
            chkflag=0
            if abap_op:
                lenop = len(abap_op)
                for each in abap_op:
                    chkoutput=each.get('WA',"")
                    if 'application error' in chkoutput.lower() or 'compilation issue' in chkoutput.lower():
                        chkflag = 1
                        break
                if  lenop <= 1:
                    chkflag = 1
            
            logging.info("OP check flag :%s" %chkflag)
            chkabap_script= abapscript.strip()
            if chkflag:
                construct_op =[]
                OUTPUT_DICT={"OUTPUT":{'OUTPUT':[]}}
                if abapscript in list(title_mapping.keys()):
                    lst_titles = title_mapping.get(chkabap_script,"")
                    if lst_titles:
                        for each_title in lst_titles:
                            construct_op.append({"TITLE":each_title,"DATA":[{"RESULT":"Lower version compilation issue with script"}]})
                        
                        OUTPUT_DICT['OUTPUT']['OUTPUT'] = construct_op
                        logging.info("Set new output for compilation error :%s" %OUTPUT_DICT)
                else:
                    OUTPUT_DICT={"OUTPUT":{'OUTPUT':[]}}
                    tmp=[{"TITLE":"Lower version error","DATA":[{"RESULT":"Lower version compilation issue with script"}]}]
                    OUTPUT_DICT['OUTPUT']['OUTPUT'] = tmp
                    logging.info("Set new output for compilation error, Title not mapped :%s" %OUTPUT_DICT)
                #SAFE EXIT
                data = OUTPUT_DICT
                conn.close()
                end_time = datetime.datetime.now()
                end_date_time = end_time.strftime("%m/%d/%Y %H:%M:%S")
                data_list.insert(1, end_date_time)
                data_dict.update({abapscript: data_list})
                logging.info("Data dict is :%s" %data_dict)
                # insert time in json file
                file = open("/cm_sap_migration/" + abapscript.split(".")[0] + "_timing.json", "w")
                file.write(json.dumps(data_dict, ensure_ascii=False))
                file.close()
                logging.info("Wrote timestamp")
                logging.info("Message : %s written to output path: %s" %(OUTPUT_DICT['OUTPUT'],outputspath))
                fo = open(outputspath + abapscript.split(".")[0]+".json", "w")
                fo.write(json.dumps(OUTPUT_DICT['OUTPUT'], ensure_ascii=False))
                fo.close()
                logging.info("Finished writing to file")
                module.exit_json(changed=True, success='True', msg=data)
            if abapscript in list(column_mapping.keys()):
                    logging.info("Check for missing column headers in output")
                    #Change output
                    RESULT['ES_OUTPUT'] = modify_abap_output(module,logging,RESULT['ES_OUTPUT'],column_mapping,abapscript)
                    logging.info("Modified output after checking for missing columns :%s" %RESULT['ES_OUTPUT'])
            STATEMENT_TAKEN = False
            OUTPUT_DICT_INNER = {}
            DATA_DICT = {}
            ABAP_RECORDS_LIST = []
            OUTPUT_LIST = []
            COLUMN_TAKEN = False
            DATA_TAKEN = False
            IS_TREE = False
            IS_TABLE = False
            is_certificate = False
            last_level = 0
            level = 0
            first_level_list = []
            first_level_count = -1
            second_level_count = -1
            third_level_count = -1
            fourth_level_count = -1
            certificate_count = 0
            certificate = ''


            for i in range(len(RESULT['ES_OUTPUT'])):
                row = list(RESULT['ES_OUTPUT'][i].values())[0]
                tree_statement = row.split('|')
                if (len(tree_statement) > 1) and (IS_TREE == False) and (IS_TABLE == False):
                    try:
                        temp = int(tree_statement[1])
                        IS_TREE = True
                    except Exception as ex:
                        logging.info("Exception occured, Error:%s" %ex)
                pass


                if IS_TREE:
                    last_level = level
                    row = list(RESULT['ES_OUTPUT'][i].values())[0]
                    row_split = row.split('|')
                    row = row_split[0]
                    level = int(row_split[1])
                    if level == 1:
                        same_level_dict = {}
                        same_level_dict.update({row:[]})
                        first_level_list.append(same_level_dict) #[{row:[]}]
                        first_level_count += 1

                    elif level == 2:
                        same_level_dict = {}
                        same_level_dict.update({row:[]})
                        key_one = list(first_level_list[first_level_count].keys())[0]
                        if last_level <= level:
                            first_level_list[first_level_count][key_one].append(same_level_dict)  #[{level1:[{level2:[]}]}]
                        else:
                            first_level_list[first_level_count][key_one].append(same_level_dict)  #[{level1:[{level2:[]}]}]
                            third_level_count = -1
                        second_level_count += 1

                    elif level == 3:
                        same_level_dict = {}
                        same_level_dict.update({row:[]})
                        key_one = list(first_level_list[first_level_count].keys())[0]
                        key_two = list(first_level_list[first_level_count][key_one][second_level_count].keys())[0]
                        if last_level <= level:
                            first_level_list[first_level_count][key_one][second_level_count][key_two].append(same_level_dict)#third_level_list  #[{level1:[{level2:[{level3:[]}]}]}]
                        elif last_level > level:
                            first_level_list[first_level_count][key_one][second_level_count][key_two].append(same_level_dict)#third_level_list
                            fourth_level_count = -1
                        third_level_count += 1

                    elif level == 4:
                        same_level_dict = {}
                        same_level_dict.update({row:[]})
                        if last_level <= level:
                            key_one = list(first_level_list[first_level_count].keys())[0]
                            key_two = list(first_level_list[first_level_count][key_one][second_level_count].keys())[0]
                            key_tre = list(first_level_list[first_level_count][key_one][second_level_count][key_two][third_level_count].keys())[0]
                            first_level_list[first_level_count][key_one][second_level_count][key_two][third_level_count][key_tre].append(same_level_dict)
                        elif last_level > level:
                            first_level_list[first_level_count][key_one][second_level_count][key_two][third_level_count][key_tre].append(same_level_dict)
                        fourth_level_count += 1
                    pass
                    
                    
                else:
                    IS_TABLE = True
                    if row == '':
                        STATEMENT_TAKEN = False
                        certificate_count = 0
                        if DATA_TAKEN == True:
                            DATA_DICT.update({'TITLE':STATEMENT})
                            if ABAP_RECORDS_LIST != []:
                                DATA_DICT.update({'DATA':ABAP_RECORDS_LIST})
                            OUTPUT_LIST.append(DATA_DICT)
                            DATA_DICT = {}
                            DATA_TAKEN = False
                    elif row == '-----BEGIN CERTIFICATE-----':
                        certificate = ''
                        is_certificate = True
                    elif row == '-----END CERTIFICATE-----':
                        certificate = '-----BEGIN CERTIFICATE-----\n' + certificate + '\n-----END CERTIFICATE-----'
                        ABAP_RECORDS_LIST[certificate_count-1].update({'CERTIFICATE':certificate})
                        is_certificate = False
                    elif is_certificate:
                        certificate = certificate + row

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
                                certificate_count += 1
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
            elif IS_TREE:
                OUTPUT_LIST = first_level_list


            OUTPUT_DICT_INNER.update({'OUTPUT':OUTPUT_LIST})

        OUTPUT_DICT['OUTPUT']['STATUS'] = 'SUCCESS'
        OUTPUT_DICT['OUTPUT']['RESULT'] = OUTPUT_DICT_INNER
        
        if re.search('TU02', abap_file_ver):
            output_data = DATA_DICT['DATA']
            for each_dict in output_data:
                for message in each_dict.values():
                    if "parameters not deleted" in message:
                        OUTPUT_DICT['OUTPUT']['STATUS'] = 'FAILURE'
                        if OUTPUT_DICT['OUTPUT']['ERROR'] != "":
                            OUTPUT_DICT['OUTPUT']['ERROR'] = OUTPUT_DICT['OUTPUT']['ERROR'] + ', '
                        OUTPUT_DICT['OUTPUT']['ERROR'] = OUTPUT_DICT['OUTPUT']['ERROR'] + message

        data = OUTPUT_DICT
        conn.close()

        end_time = datetime.datetime.now()
        end_date_time = end_time.strftime("%m/%d/%Y %H:%M:%S")
        data_list.insert(1, end_date_time)
        data_dict.update({abap_file_ver: data_list})

        # insert time in json file
        file = open("/cm_sap_migration/" + abapscript.split(".")[0] + "_timing.json", "w")
        file.write(json.dumps(data_dict, ensure_ascii=False))
        file.close()

        fo = open(outputspath + abapscript.split(".")[0]+".json", "w")
        fo.write(json.dumps(OUTPUT_DICT['OUTPUT']['RESULT'], ensure_ascii=False))
        fo.close()

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