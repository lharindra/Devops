#!/usr/local/bin/python3
import boto3
import subprocess
import textwrap
from argparse import ArgumentParser
import sys

class main_class():
    def __init__(self):
        self.ec2_conn_list = boto3.client('ec2')
        self.ec2_conn_create = boto3.resource('ec2')
        self.total_list_assign = []
        self.all_inst_dict_tolist = []

    def ec2_list_of_instances(self):
        ec2_responce = self.ec2_conn_list.describe_instances()  
        for reservation in ec2_responce["Reservations"]:
            for instance in reservation["Instances"]:
                each_inst_dict = {}
                each_inst_dict["Sate"] = instance["State"]["Name"]
                each_inst_dict["InstanceId"] = instance["InstanceId"]
                self.all_inst_dict_tolist.append(each_inst_dict)

    def table_format(self):
        self.columns = list(self.all_inst_dict_tolist[0].keys()) 
        self.columns.insert(0, "No.")   
        tb = SimpleTable(self.columns)
        row_number = 0
        for i in self.all_inst_dict_tolist:
            row_data = []
            row_number += 1
            row_data.append(str(row_number))
            for k, v in i.items():
                row_data.append(v)
            tb.add_row(row_data)
        tb.print_table()

    def creat_new_ec2_instances(self, count):
        count = int(count)
        instances = self.ec2_conn_create.create_instances(
            ImageId = 'ami-00fc224d9834053d6',
            InstanceType = 't2.micro',
            KeyName = 'sshpair',
            MinCount = 1,
            MaxCount = count
        )
        print("Successfully created " + str(count) + " Instances")

    def stop_instance(self, list_filter):
        try:
            for i in list_filter:
                ec2_stop = self.ec2_conn_list.stop_instances(InstanceIds = [i])
        except AttributeError:
            print("unable to stop the instances")

    def start_instance(self, list_filter):
        for i in list_filter:
            ec2_start = self.ec2_conn_list.start_instances(InstanceIds = [i])

    def term_instance(self, list_filter):
        for i in list_filter:
            ec2_start = self.ec2_conn_list.terminate_instances(InstanceIds = [i])

    def filter_list(self, list_option):
        print("These are the Instances which will be affected:- ")
        for k in list_option:
            i = int(k)
            print(self.all_inst_dict_tolist[i-1]["InstanceId"])
            self.total_list_assign.append(self.all_inst_dict_tolist[i-1]["InstanceId"])

    def confirmation(self):
        try:        
            yn = input("If you want to continue with confirm(Y/N):- ")
            if yn in ["Y","y"]:
                return "y"
            elif yn in ["N","n"]:
                exit
            else:
                raise Exception
        except Exception:
            print("Given a incorrect character")
        
    def range_mapper(self, range_vales):
        range_list = []
        case_range = range_vales.split(",")
        try:
            for r in case_range:
                range_dict = {}
                range_start_end = r.split("-")
                if "" in range_start_end:
                    raise Exception  # this can occur if unncessary hypens/commas present in range values
                if len(range_start_end) == 1:
                    range_dict["start"] = range_start_end[0]
                    range_dict["end"] = range_start_end[0]
                    range_list.append(range_dict)
                elif len(range_start_end) == 2:
                    range_dict["start"] = range_start_end[0]
                    range_dict["end"] = range_start_end[1]
                    range_list.append(range_dict)         
            InstanceIds = [self.all_inst_dict_tolist[rownumber]["InstanceId"]
                                    for r in range_list for rownumber in range(int(r["start"]) - 1, int(r["end"]))]
            print("These are the Instances which are effected with above action")
            for i in InstanceIds:
                print(i)
            return InstanceIds
        except Exception as e:
            return False


    def range_listing(self, list_option):
        range_list = []
        case_range = list_option.split(",")
        for r in case_range:
            range_start_end = r.split("-")

                

class SimpleTable():

    def __init__(self, columns=[], wrap_length=20, coldelim=" | ", rowdelim="-"):
        self.table_heading = columns
        self.table_rows = []
        self.rowdelim = rowdelim
        self.coldelim = coldelim
        self.wrap_length = wrap_length
        # self.column_limit = 185
        # computes terminal width
        self.column_limit = int(subprocess.Popen(
            ["tput", "cols"], stdout=subprocess.PIPE).communicate()[0].decode("utf-8").strip("\n"))

    def add_row(self, row_data):
        self.table_rows.append(row_data)

    def print_table(self):
        self.set_table_attributes()
        string = self.rowdelim
        self.table_rows.insert(0, self.table_heading)
        # restructure to get textwrap.wrap output for each cell
        l = [[textwrap.wrap(col, self.wrap_length) for col in row]
             for row in self.table_rows]
        for row in l:
            for n in range(max([len(i) for i in row])):
                string += self.coldelim
                for col in row:
                    if n < len(col):
                        string += col[n].ljust(self.wrap_length)
                    else:
                        string += " " * self.wrap_length
                    string += self.coldelim
                string += "\n"
            string += self.rowdelim
        print(string)

    def set_table_attributes(self):
        # considering column delims that come in between table contents
        p = len(self.coldelim) * (len(self.table_rows[0]) - 1)
        self.wrap_length = self.check_wrap_length(self.wrap_length, p)
        self.rowdelim = self.coldelim + self.rowdelim * \
            (self.wrap_length *
             max([len(i) for i in self.table_rows]) + p) + self.coldelim + "\n"

    def check_wrap_length(self, wrap_length, p):
        # if wrap_length * len(self.table_heading) <= self.column_limit - 2 *
        # len(self.coldelim) - p:
        if wrap_length * len(self.table_heading) <= self.column_limit * 3 // 4:
            return wrap_length
        else:
            return self.check_wrap_length(wrap_length - 1, p)

if __name__ == "__main__":
    parser = ArgumentParser(description="""To check the Instances details of AWS account""",
                            usage='%(prog)s --list(list of instances) --stop(to stop instances) --term(to terminate instances) --start(to start instances)',
                            epilog='python verify_hosts.py --list(or) --start')
    parser.add_argument("--list", dest="list", help="List instances")
    parser.add_argument("--stop", help="Stop instances")
    parser.add_argument("--start",help="Start instances")
    parser.add_argument("--term", help="Terminate Instances")
    parser.add_argument("--create", help="Creating imstances")
    args = parser.parse_args()
    Mainobj = main_class()
    if len(sys.argv)<2 or args.list in ("all",""):
        Mainobj.ec2_list_of_instances()
        Mainobj.table_format()

    if args.stop:
        Mainobj.ec2_list_of_instances()
        list_option_filter = Mainobj.range_mapper(args.stop)
        confirm = Mainobj.confirmation()
        if confirm in ["Y","y"]:
            Mainobj.stop_instance(list_option_filter)

    if args.start:
        Mainobj.ec2_list_of_instances()
        list_option_filter = Mainobj.range_mapper(args.start)
        confirm = Mainobj.confirmation()
        if confirm in ["Y","y"]:
            Mainobj.start_instance(list_option_filter)

    if args.term:
        Mainobj.ec2_list_of_instances()
        list_option_filter = Mainobj.range_mapper(args.term)
        confirm = Mainobj.confirmation()
        if confirm in ["Y","y"]:
            Mainobj.term_instance(list_option_filter)

    if args.create:
        Mainobj.creat_new_ec2_instances(args.create)
