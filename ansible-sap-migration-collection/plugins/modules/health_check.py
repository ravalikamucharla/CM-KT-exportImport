#!/usr/bin/python3
import sys
import json
from hdbcli import dbapi
from pathlib import Path
from general_login import Login
from datetime import datetime


try:
    out_dict={"Output":[],"Status":"Failed","StatusCode":"500","ERROR":""}
    DATA = json.loads(sys.argv[1])
    HNAME, UNAME, UPWD, SID = ([] for _ in range(4))
    AUTHTYPE, PEMFILE = [], []
    ISSUDOUSER = []
    USERSTOREKEY = []
    BATCH_FILE = []
    OUTPUT_FILE = []
    for i in DATA:
        HNAME.append(i.get('hostName','').strip())
        UNAME.append(i.get('userName','').strip())
        UPWD.append(i.get('password','').strip())
        SID.append(i.get('sid','').upper().strip())
        ISSUDOUSER.append(i.get('isSudoUser', 'FALSE').upper().strip())
        AUTHTYPE.append(i.get('loginMechanism','ppk').lower().strip())
        PEMFILE.append(i.get('pemFile', '').strip())
        USERSTOREKEY.append(i.get('userStoreKey', ''))
        BATCH_FILE.append(i.get('batchFile', ''))
        OUTPUT_FILE.append(i.get('outputFile', ''))

    lstlen=len(HNAME)
    fin_result=[]
    for lstcount in range(lstlen):
        LOGIN_OBJ = Login(HNAME[lstcount], UNAME[lstcount], UPWD[lstcount],"Linux" , AUTHTYPE[lstcount], PEMFILE[lstcount], ISSUDOUSER[lstcount])
        sshobj=LOGIN_OBJ.ssh
        sidadm = SID[lstcount].lower() + 'adm'
        user_store_key = USERSTOREKEY[lstcount]
        batch_file =BATCH_FILE[lstcount]
        batch_file = batch_file.replace("\\","//")
        output_file=OUTPUT_FILE[lstcount]
        output_file = output_file.replace("\\","//")
        command = r'hdbsql -U %s -m -A -I %s -o %s' %(user_store_key,batch_file,output_file)
        if AUTHTYPE[lstcount] in ('password','ppk', 'passwordandppk'):
            _, stdout, stderr = sshobj.exec_command('sudo su - %s -c "'"%s"'" '%(sidadm,command))
        else:
            out_dict['ERROR']="Incorrect authentication type"
            print(json.dumps(out_dict, default=str))
            sys.exit(1)
        result = str(stdout.read(), 'utf-8')
        err=str(stderr.read(),'utf-8')
        if err:
            out_dict['ERROR']="Error occured while executing the hdbsql command - %s" %(err)
            print(json.dumps(out_dict, default=str))
            sys.exit(1)
        _, stdout, stderr = sshobj.exec_command('cat %s' %(output_file))
        result = str(stdout.read(), 'utf-8')
        error=str(stderr.read(),'utf-8')
        if error:
            out_dict['ERROR']="Error occured while reading output file '%s', Error :%s" %(output_file,error)
            print(json.dumps(out_dict, default=str))
            sys.exit(1)
        if result:
            lst_lines=result.split('\n')
            sep_cols = [line.split("|") for line in lst_lines if "|" in line]
            cols=[eachcol.strip() for eachcol in sep_cols[0] if eachcol.strip() not in ['',','] ]
            cols.insert(0,"Title")
            fl=0
            final_output=[]
            for each in sep_cols[2:]:
                if (not 'END OF CHECK' in each[1]) and each[1]:
                    if "****" in each[1]:
                        head=each[2].strip()
                    elif each[1].strip() != '':
                        each_vals =[vals.strip() for vals in each[1:-1]]
                        all_vals=each_vals
                        all_vals.insert(0,head)
                        fin_each = dict(zip(cols,all_vals))
                        final_output.append(fin_each)
            fin_result.append({"SID":SID[lstcount],"Value":final_output})

    out_dict['Output']=fin_result
    out_dict['StatusCode']="200"
    out_dict['Status']="Success"
    print(json.dumps(out_dict, default=str))

except Exception as err:
    out_dict={"Output":[],"Status":"Failed","StatusCode":"500","ERROR":"Exception occured, Error : %s" %(err)}
    print(json.dumps(out_dict, default=str))
    sys.exit(1)
