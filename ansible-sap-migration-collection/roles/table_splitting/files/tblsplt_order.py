#!/usr/bin/python3
import sys
import json
import traceback
import argparse
from os import path
import warnings
import os
import glob
import math
import re

warnings.filterwarnings("ignore")

class TABLESPLIT():
    """
    STMS / STAPI class
    """
    def __init__(self):
        #establishing connection with SAP
        self.final_output = {
            "Output": "",
            "ERROR": "",
            "StatusCode": "500"
        }
        self.inpath=""
        self.outpath=""
        self.split_size=1
        self.spltwrite = []
        self.orderbywrite=[]

    def parse_arguments(self, argvars):
        try:
            arg_len = len(argvars)
            if arg_len > 0:
                # arg[1] is input
                in_path  = argvars[0]
                if not os.path.isabs(in_path ):
                    in_path = os.path.join(os.getcwd(), in_path )
                self.inpath = in_path
                self.outpath = argvars[1]
            else:
                self.final_output["ERROR"]="Please supply 'Input path' as argument"
                print(json.dumps(self.final_output, default=str))
                sys.exit()
        except Exception as err:
            print("ERROR :", err)
    def read_input(self):
        rootdir = self.inpath
        lstdirs=[]
        files_flag=0
        curdirfile = [x for x in os.listdir(rootdir) if x.endswith(".json")]
        #print("LIST ",curdirfile)
        all_dirs = [x[0] for x in os.walk(rootdir)]
        #print("all dirs ",all_dirs)
        for file in all_dirs:
            if not file == '.':
                d = os.path.join(rootdir, file)
                if os.path.isdir(d):
                    lstdirs.append(d)

        if curdirfile:
            files_flag =self.inpath
        #print("lst dirs :",lstdirs)
        return lstdirs,files_flag


    def read_files(self,each):
        try:
            lsttab=[]
            lstodr=[]
            #self.lst_jsons = glob.glob(os.path.join(self.inpath, eachdir, "*.json"))
            #for index, each in enumerate(self.lst_jsons):
            filename = os.path.basename(each).split(".json")[0]
            try:
                with open(each,encoding='utf-8') as json_file:
                    data = json.load(json_file,strict=False)
            except Exception as err:
                print(json.dumps({"Error": "Error reading json file %s, Error:%s" % (filename, err)}))
            proc_data = data['OUTPUT']
            for eachproc in proc_data:
                process_data = eachproc['DATA']
                #splt=self.split_size * 1000000      #convert GB to KB
                splt = self.split_size * 100000  # convert GB to KB
                for eachdata in process_data:
                    for key,val in eachdata.items():
                        if 'table' in key.lower():
                            t_name=val
                            tab_name=val
                            if r'\\' in val:
                                tab_name=val.replace("\\","_")
                            if r"/" in val:
                                tab_name = val.replace("/", "_")
                        if 'size' in key.lower():
                            tabval=float(val)
                            tabv=math.ceil(tabval)
                            tabsize=math.ceil(int(tabv)/splt)
                            if tabsize > 1:
                                lsttab.append("%s%%%s" %(t_name,tabsize))
                                lstodr.append("[%s]" %tab_name)
                                lstodr.append("jobNum=1")
                                for num in range(tabsize):
                                    lstodr.append("%s-%s" %(tab_name,num+1))
            return lsttab,lstodr
        except Exception as err:
            print("ERROR :", err)

try:
    obj_table_split=TABLESPLIT()
    parser = argparse.ArgumentParser("tblsplt_order")
    cur_path = os.path.join(os.getcwd(), "Output")

    parser.add_argument('--input', '-i', help='Input File path')
    parser.add_argument('--size_in_GB', '-s', help='Table size in GB')
    parser.add_argument('--output', '-o', default=cur_path, help='Optional output path')
    args = parser.parse_args()
    if not path.exists(args.output):
        os.makedirs(args.output)
        obj_table_split.outpath = args.output

    argvars=[args.input,args.output]
    obj_table_split.split_size=int(args.size_in_GB)
    obj_table_split.parse_arguments(argvars)
    #lst_ips, has_files = obj_table_split.read_input()
    tblsplt=os.path.join(obj_table_split.outpath,"table_splitting.txt")
    wr_table = open(tblsplt,"w")
    orderby=os.path.join(obj_table_split.outpath,"order_by.txt")
    wr_order = open(orderby,"w")
    if not args.input:
        print("Please supply input file")
    else:
        lsttable, lstorder = obj_table_split.read_files(args.input)
        for eachdata in lsttable:
            wr_table.write(eachdata)
            wr_table.write("\n")
        for eachodr in lstorder:
            wr_order.write(eachodr)
            wr_order.write("\n")
    wr_table.close()
    wr_order.close()
    # for eachdir in lst_ips[1:]:
    #     lsttable,lstorder =obj_table_split.read_files(eachdir)
    #     for eachdata in lsttable:
    #         wr_table.write(eachdata)
    #         wr_table.write("\n")
    #     for eachodr in lstorder:
    #         wr_order.write(eachodr)
    #         wr_order.write("\n")
    # if has_files:
    #     lsttable,lstorder = obj_table_split.read_files(has_files)
    #     for eachdata in lsttable:
    #         wr_table.write(eachdata)
    #         wr_table.write("\n")
    #     for eachodr in lstorder:
    #         wr_order.write(eachodr)
    #         wr_order.write("\n")


except Exception as err:
    obj_table_split.final_output["ERROR"] ="Exception - %s " %err
    print(json.dumps(obj_table_split.final_output, default=str))
    sys.exit()







