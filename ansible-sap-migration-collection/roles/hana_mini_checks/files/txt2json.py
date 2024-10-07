#!/usr/bin/python3
import sys
import json
import os
import argparse

try:

    parser = argparse.ArgumentParser("txt_json")
    parser.add_argument('--input', '-i', help='Input path')
    args = parser.parse_args()
    with open(args.input,"r") as txt_file:
        result =txt_file.read()
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
        print(json.dumps(final_output,default=str))

except Exception as err:
    print(json.dumps("Error:err", default=str))
    sys.exit(1)