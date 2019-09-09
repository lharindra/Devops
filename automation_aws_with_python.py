#!/usr/local/bin/python3
import boto3
import subprocess
import textwrap

class main_class():
    def __init__(self):
        self.ec2_conn_list = boto3.client('ec2')
        self.ec2_conn_create = boto3.resource('ec2')
        self.total_inst_list = {}
        self.inst_running = []
        self.inst_term = []
        self.inst_stop = []
        self.all_inst_dict_tolist = []

    def ec2_list_of_instances(self):
        ec2_responce = self.ec2_conn_list.describe_instances()  
        for reservation in ec2_responce["Reservations"]:
            for instance in reservation["Instances"]:
                each_inst_dict = {}
                each_inst_dict["Sate"] = instance["State"]["Name"]
                each_inst_dict["InstanceId"] = instance["InstanceId"]
                self.all_inst_dict_tolist.append(each_inst_dict)
        columns = list(self.all_inst_dict_tolist[0].keys()) 
        columns.insert(0, "No.")   
        tb = SimpleTable(columns)
        row_number = 0
        for i in self.all_inst_dict_tolist:
            row_data = []
            row_number += 1
            row_data.append(str(row_number))
            for k, v in i.items():
                row_data.append(v)
            tb.add_row(row_data)
        tb.print_table()

    def creat_new_ec2_instances(self):
        instances = self.ec2_conn_create.create_instances(
            ImageId = 'ami-00fc224d9834053d6',
            InstanceType = 't2.micro',
            KeyName = 'sshpair',
            MinCount = 1,
            MaxCount = 2
        )

    def stop_instance(self):
        ec2_stop = self.ec2_conn_list.stop_instances(InstanceIds = ['i-01e4a3f4999b0ca13'])

    def start_instance(self):
        ec2_start = self.ec2_conn_list.start_instances(InstanceIds = ['i-01e4a3f4999b0ca13'])

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
    Mainobj = main_class()
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+ Here are the list of instance's which are build in you account +")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    Mainobj.ec2_list_of_instances()
    #Mainobj.creat_new_ec2_instances()
    Mainobj.stop_instance()
    #Mainobj.start_instance()
    #Mainobj.ec2_list_of_instances()
