#!/usr/bin/python3
import os
import re
import glob


class AbapVersion:
    """Main class
    """
    def __init__(self, connection_obj, path,logging):
        """
        Constructor
        """
        try:
            self.logger=logging
            self.conn_abap = connection_obj
            self.path = path
            self.abapver=""
            self.abap_file_name = ""
            self.output_data = {'success': False, 'output': '', 'err_type': ''}
            self.pattern = re.compile('^[\\d]+\\|[\\d]+$')
        except Exception as err:
            if self.logger:
                self.logger.info("Exception occuerd, Error :%s" %err)
            return

    def get_cur_abap_version(self):
        """SAP code is passed to the RFC module(ZBASIS_RFC_WRAPPER) which returns non parsed data.
           Uses files I/O to fetch ABAP code.
        """
        try:
            abap_code = []
            # Getting 'abap_code' and passing to wrapper
            with open(os.path.join(self.path, "ZBASIS_R_BASIS_COMPONENT.txt"), "r") as abap_code_file:
                my_list = abap_code_file.read().splitlines()
                for line in my_list:
                    abap_line = {'LINE': line}
                    abap_code.append(abap_line)

            result = self.conn_abap.call('ZBASIS_RFC_ACCWRAPPER', IS_PROGRAM_LINES=abap_code)
            respop = result['ES_OUTPUT']
            self.logger.info("version result :%s" %result['ES_OUTPUT'])
            for each in respop:
                lstmatch = self.pattern.match(each['WA'])
                if lstmatch:
                    finresult = str(lstmatch.group())
                    if finresult:
                        tmp = finresult.split("|", 1)
                        return tmp[0]
            return ""
        except Exception as err:
            self.logger.info("Exception :%s" %err)
            return

    def get_abap_file(self, abap_filename):
        self.logger.info("Start getting all version files")
        self.abap_file_name = abap_filename
        if not self.abap_file_name:
            return ""
        file_extn = self.abap_file_name.rsplit(".",1)[1]
        if file_extn:
            file_extn = file_extn.lower()
        self.logger.info("Filename : %s" %abap_filename)
        abap_vers = self.get_cur_abap_version()
        self.abapver=abap_vers
        self.logger.info("Abap version : %s" %abap_vers)
        if not abap_vers:
            return ""
        else:
            abap_version = int(abap_vers)
        loc = self.path
        self.logger.info("self path :%s" %self.path)
        filename = abap_filename.rsplit('.', 1)[0]
        self.logger.info("Filename is :%s" %filename)
        npath = os.path.join(loc,"%s*.*" %filename)
        file_list = [os.path.basename(files) for files in glob.glob(loc + "//" + "%s*.*" % filename)]

        lstextns = re.compile(r'^%s_?([0-9]{1,3}S|[a-zA-Z]{1,4})?.%s$|^%s_[a-zA-Z]{1,4}_[0-9]{1,3}.%s$|^%s_[0-9]{1,3}_[a-zA-Z]{1,4}.%s$|^%s_[0-9]{1,3}_[0-9]{1,3}.%s$' % (filename,file_extn,filename,file_extn,filename,file_extn,filename,file_extn))
        matched_files = []
        self.logger.info("File list :%s" %file_list)
        for each_file in file_list:
            res_pattern = lstextns.match(each_file)
            if res_pattern:
                file_found = res_pattern.group()
                if file_found not in matched_files:
                    matched_files.append(file_found)
        filename_with_cur_version = '%s_%sS.%s' % (filename, abap_version,file_extn)
        final_file = ""

        if filename_with_cur_version in matched_files:
            final_file = filename_with_cur_version
        elif abap_version < 740:
            scrpt_range = [each for each in matched_files if
                           re.findall(r"%s_[1-9][0-9][0-9]_[1-9][0-9][0-9].%s" %(filename,file_extn), each)]
            for eachrange in scrpt_range:
                search_dgts = re.findall(r"\d{3}", eachrange)
                if abap_version >= int(search_dgts[0]) and abap_version <= int(search_dgts[1]):
                    final_file = eachrange
                    return final_file
            scrpt_no_hver = [each for each in matched_files if
                             re.findall(r"%s_LVER_[1-9][0-9][0-9].%s" % (filename,file_extn),each)]
            for eachrange in scrpt_no_hver:
                search_dgts = re.findall(r"\d{3}", eachrange)
                if abap_version <= int(search_dgts[0]):
                    final_file = eachrange
                    return final_file
            if '%s_LVER.%s' % (filename,file_extn) in matched_files:
                final_file = '%s_LVER.%s' % (filename,file_extn)
                return final_file
            if abap_filename in matched_files:
                final_file = abap_filename
                return final_file
        elif abap_version >= 740:
            self.logger.info(" >=740")
            scrpt_range= [each for each in matched_files if re.findall(r"%s_[1-9][0-9][0-9]_[1-9][0-9][0-9].%s"%(filename,file_extn),each)]
            self.logger.info("Script range : %s" %scrpt_range)
            for eachrange in scrpt_range:

                search_dgts = re.findall(r"\d{3}",eachrange)
                if abap_version >=int(search_dgts[0]) and abap_version <=int(search_dgts[1]):
                    final_file = eachrange
                    return final_file
            self.logger.info("test")
            scrpt_no_hver = [each for each in matched_files if
                           re.findall(r"%s_[1-9][0-9][0-9]_HVER.%s" %(filename,file_extn), each)]

            for eachrange in scrpt_no_hver:
                search_dgts = re.findall(r"\d{3}",eachrange)
                if abap_version >=int(search_dgts[0]):
                    final_file = eachrange
                    return final_file
            if '%s_HVER.%s' % (filename,file_extn) in matched_files:
                final_file = '%s_HVER.%s' % (filename,file_extn)
                return final_file
            if abap_filename in matched_files:
                final_file = abap_filename
                return final_file
        elif abap_filename in matched_files:
            final_file = abap_filename
        return final_file
