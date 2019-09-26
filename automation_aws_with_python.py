#!/usr/local/bin/python3
import boto3
import subprocess
import textwrap
from argparse import ArgumentParser
import sys
import re
from webbrowser import open_new
import botocore
import os

class ec2_class():
    def __init__(self):
        self.ec2_conn_list = boto3.client('ec2')
        self.ec2_conn_create = boto3.resource('ec2')
        self.total_list_assign = []
        self.all_inst_dict_tolist = []
        self.running_state = []
        self.stoppped_state = []
        self.terminated_state = []

    def ec2_list_of_instances(self, sate_check=''):
        try:
            self.ec2_responce = self.ec2_conn_list.describe_instances()
        except  botocore.exceptions.EndpointConnectionError as err:
            print("Error:- Couldn't connect to the internet Please check the network setting")
            sys.exit(1)
        state = []  
        for reservation in self.ec2_responce["Reservations"]:
            for instance in reservation["Instances"]:
                each_inst_dict = {}
                each_inst_dict["Region"] = instance["Placement"]["AvailabilityZone"]
                each_inst_dict["State"] = instance["State"]["Name"]
                each_inst_dict["InstanceId"] = instance["InstanceId"] 
                self.all_inst_dict_tolist.append(each_inst_dict)                
        newlist=sorted(self.all_inst_dict_tolist, key = lambda k:k['State'])
        self.all_inst_dict_tolist=newlist
        #print(self.all_inst_dict_tolist)
        if sate_check == "stopped":
            for i in self.all_inst_dict_tolist:
                if i["State"] == "stopped":
                    self.running_state.append(i)
            self.all_inst_dict_tolist = self.running_state
            exit
        if sate_check == "terminated":
            for i in self.all_inst_dict_tolist:
                if i["State"] == "terminated":
                    self.stoppped_state.append(i)
            self.all_inst_dict_tolist = self.stoppped_state
            exit
        if sate_check == "running":
            for i in self.all_inst_dict_tolist:
                if i["State"] == "running":
                    self.terminated_state.append(i)
            self.all_inst_dict_tolist = self.terminated_state
            exit

    def table_format(self):
        try:
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
        except IndexError:
            print("Instances are not available. Please use --create to lauch")

    def creat_new_ec2_instances(self, count, sec_id, subnet_id):
        count = int(count)
        tags = [
                    {'Key':'Name','Value': 'WithAutomation'}
                ]
        user_data = '''#!/bin/bash -xe
        exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
        sudo su -
        useradd hari
        echo "linux" | passwd --stdin hari
        sed -i "/^[^#]*PasswordAuthentication[[:space:]]no/c\PasswordAuthentication yes" /etc/ssh/sshd_config
        service sshd restart
        echo "hari            ALL=(ALL)       NOPASSWD: ALL" >> /etc/sudoers'''
        tag_Specifications = [{'ResourceType': 'instance', 'Tags': tags}]
        instances = self.ec2_conn_create.create_instances(
            ImageId = 'ami-00fc224d9834053d6',
            TagSpecifications = tag_Specifications, 
            InstanceType = 't2.micro',
            KeyName = 'sshpair',
            MinCount = 1,
            MaxCount = count,
            NetworkInterfaces=[{'DeviceIndex': 0,'Groups': [sec_id], 'SubnetId': str(subnet_id), 'DeleteOnTermination': True, 'AssociatePublicIpAddress': True}],
            UserData=user_data
        )
        print("Successfully created " + str(count) + " Instances")

    def check_sec_grp(self):
        try:
            check_sec_group = self.ec2_conn_list.describe_security_groups()
        except  botocore.exceptions.EndpointConnectionError as err:
            print("Error:- Couldn't connect to the internet Please check the network setting")
            sys.exit(1)
        try:
            for groups in check_sec_group["SecurityGroups"]:
                if groups["GroupName"] == "Instance launch":
                    sec_id = groups["GroupId"]
                    #print("The security group **" +  groups["GroupName"] + "** which you are trying to create is already there with ID:- "+ groups["GroupId"])
                    return "Found",sec_id
            return "NotFound", "NotFound"
        except ValueError:
            print("VPC or the Security group issue")

    def get_subnetid(self):
        check_sec_group = self.ec2_conn_list.describe_security_groups()
        for groups in check_sec_group["SecurityGroups"]:
            if groups["GroupName"] == "default":
                vpc_id = groups["VpcId"]
                response = self.ec2_conn_create.Vpc(id=vpc_id)
                subnets = []
                for subnet in response.subnets.all():
                    subnets.append(subnet.id)
                return subnets[0]
        
    def create_sec_grp(self, count):
        check_status, sec_id = self.check_sec_grp()
        subnet_id = self.get_subnetid()
        if check_status == "Found":
            self.creat_new_ec2_instances(count, sec_id, subnet_id)
        elif check_status == "NotFound":
            self.sec_group = self.ec2_conn_create.create_security_group(
                GroupName='Instance launch', Description='Instance launch sec group')
            self.sec_group.authorize_ingress(
                IpPermissions=[
                {'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                ]  
            )
            print("Security group not found, so created one:-" + self.sec_group.group_id)
            self.creat_new_ec2_instances(count, self.sec_group.id, subnet_id)

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
            ec2_term = self.ec2_conn_list.terminate_instances(InstanceIds = [i])

    def confirmation(self, item=[]):
        try:
            if item:
                yn =  input("do you want to continue with operation on "+item+" (Y/N):- ")
            else:
                yn = input("If you want to continue with confirm(Y/N):- ")
            if yn in ["Y","y"]:
                return "y"
            elif yn in ["N","n"]:
                exit
            else:
                raise Exception
        except Exception:
            print("Given a incorrect character")

    def connect_ec2(self,list_of):
        self.ec2_list_of_instances()
        try:
            val = int(list_of)
            inst_id = self.all_inst_dict_tolist[val-1]["InstanceId"]
            for reservation in self.ec2_responce["Reservations"]:
                for instance in reservation["Instances"]:
                    if inst_id == instance["InstanceId"]:
                        ip = instance["PublicIpAddress"]
            print("logging into the host "+inst_id+" Please enter the password")
            os.system("ssh hari@"+ip)
            print("Successfully logged out of"+inst_id)
        except ValueError:
            try:
                for reservation in self.ec2_responce["Reservations"]:
                    for instance in reservation["Instances"]:
                        if list_of == instance["InstanceId"]:
                            ip = instance["PublicIpAddress"]
                            print("logging into the host "+list_of+" Please enter the password")                                
                os.system("ssh hari@"+ip)
                print("Successfully logged out of"+list_of)
            except UnboundLocalError:
                print("Error:- The instance which you trying to connect is not found, Please re-check in the table and give inst_id or serial number of instance from the table")

    def range_mapper(self, range_vales):
        range_list = []
        try:
            if range_vales in ("all","stopall","termall","startall"):
                InstanceIds = [i["InstanceId"] for i in self.all_inst_dict_tolist]
            else:
                case_range = range_vales.split(",")
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

class cf_class():
    """
    This is the class to list, create, delete the cloudformation stacks
    """
    def __init__(self):
        self.cf = boto3.client('cloudformation')
        self.all_cf_list = []

    def list_all_cf(self, stackname=[]):
        try:
            listoff_all_cf = self.cf.list_stacks(
            StackStatusFilter=[
                                    'CREATE_IN_PROGRESS','CREATE_FAILED','CREATE_COMPLETE','ROLLBACK_IN_PROGRESS','ROLLBACK_FAILED','ROLLBACK_COMPLETE','DELETE_IN_PROGRESS','DELETE_FAILED','DELETE_COMPLETE','UPDATE_IN_PROGRESS','UPDATE_COMPLETE_CLEANUP_IN_PROGRESS','UPDATE_COMPLETE','UPDATE_ROLLBACK_IN_PROGRESS','UPDATE_ROLLBACK_FAILED','UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS','UPDATE_ROLLBACK_COMPLETE','REVIEW_IN_PROGRESS',
                                ] 
            )
        except  botocore.exceptions.EndpointConnectionError as err:
            print("Error:- Couldn't connect to the internet Please check the network setting")
            sys.exit(1)
        if stackname:
            for eachstack in listoff_all_cf["StackSummaries"]:
                if eachstack["StackName"] == stackname:
                    print("The stack or stackname is already exist with status:- "+ eachstack["StackStatus"])
                else:
                    return "NotFound"
        else:
            for eachstack in listoff_all_cf["StackSummaries"]:
                each_cf_list = {}
                if eachstack["StackStatus"] not in ("DELETE_COMPLETE"):
                    each_cf_list["StackName"] = eachstack["StackName"]
                    each_cf_list["Status"] = eachstack["StackStatus"]
                    self.all_cf_list.append(each_cf_list)
            self.table_format()

    def create_stack(self, stackname):
        check_stack_before_create = self.list_all_cf(stackname)
        if check_stack_before_create == "NotFound":
            create_stack = self.cf.create_stack(
                StackName=stackname,
                TemplateURL='https://cf-templates-4capd5jy2c6q-us-west-1.s3-us-west-1.amazonaws.com/2019266NEJ-welove_launch_cf',
                Parameters=[{'ParameterKey': 'KeyName','ParameterValue': 'sshpair'}],
                TimeoutInMinutes=5,
                Tags=[{'Key': 'Name','Value': 'with_auto_cf'}],
        )

    def describe_stack(self, stackname):
        print("These is the all info about the stack:- "+stackname)
        cfdescribe = boto3.resource('cloudformation')
        stack = cfdescribe.Stack(stackname)
        print("\nStack Info:-")
        print("Stack Id:- "+stack.stack_id)
        print("Stack Description:- "+stack.description+"\n")
        print("Stack Status:- "+stack.stack_status)
        print("Stack Created On:- "+str(stack.creation_time))
        print("\nResources:-")
        resource = self.cf.describe_stack_resources(
            StackName = stackname
        )
        list_all = []
        for each in resource["StackResources"]:
            list_each = {}
            list_each["LogicalResourceId"] = each["LogicalResourceId"]
            list_each["PhysicalResourceId"] = each["PhysicalResourceId"]
            list_each["ResourceType"] = each["ResourceType"]
            list_all.append(list_each)
        # for i in list_all:
        #     print(i)
        list_dict = {}
        list_dict = { i : list_all[i] for i in range(0, len(list_all) ) }

        fields = ["LogicalResourceId", "PhysicalResourceId", "ResourceType"]
        max_len = {"name": max(map(len, list_all)) + 2}
        for f in fields:
            max_len[f] = max(map(len, [f] + [str(resource[f]) for resource in list_dict.values()]))
        pad = lambda s, f: str(s).ljust(max_len[f])
        print(pad("No", "name") + " ".join(pad(f.upper(), f) for f in fields))
        for name, resource in list_dict.items():
            print(pad(name, "name") + " ".join(pad(resource[f], f) for f in fields))
        print("\nPARAMETERS:-")
        for each in stack.parameters:
            list_all = []
            for k,v in each.items():
                list_all.append(v)
            print(list_all[0]+":- "+list_all[1])

        try:
            print("\nOUTPUTS:- ")
            for each in stack.outputs:
                list_all = []
                for k,v in each.items():
                    list_all.append(v)
                print(list_all[0]+":- "+list_all[1]+"\n"+"Description:- "+list_all[2])
        except TypeError:
            print("Outputs are not yet there")

    def delete_stack(self, stackname):
        deletecf = self.cf.delete_stack(
            StackName = stackname
        )
        print("Successfull deleted the stack "+stackname+" on your command")

    def table_format(self):
        try:
            self.columns = list(self.all_cf_list[0].keys()) 
            self.columns.insert(0, "No.")   
            tb = SimpleTable(self.columns)
            row_number = 0
            for i in self.all_cf_list:
                row_data = []
                row_number += 1
                row_data.append(str(row_number))
                for k, v in i.items():
                    row_data.append(v)
                tb.add_row(row_data)
            tb.print_table()
        except IndexError:
            print("cloudformation stack are not available, Please use --launchcf to create a new stack")

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
                            epilog='python automation_of_aws_with_python.py --list(or) --start')
    parser.add_argument("--listcf", dest="listcf", action="store_true", help="List instances")
    parser.add_argument("--launchcf", dest="launchcf", help="To launch new cloudformation stacks")
    parser.add_argument("--describecf", dest="describecf", help="please give the stack name.. To know more about the stack ")
    parser.add_argument("--deletecf", dest="deletecf", help="Please give the stack name.. To delete the stack")
    parser.add_argument("--stop", help="Stop instances")
    parser.add_argument("--start",help="Start instances")
    parser.add_argument("--term", help="Terminate Instances")
    parser.add_argument("--create", help="Creating instances")
    parser.add_argument("--running",dest="running", help="--running with 'stopall' 'termall' stop or terminate all the running instances")
    parser.add_argument("--stopped",dest="stopped", help="--stopped with 'startall' 'termall' start or terminate all the stopped instances")
    parser.add_argument("--terminated",dest="terminated", action="store_true", help="To list all the terminated instances")
    parser.add_argument("--connect", dest="connect", help="To ssh to the host. Please specify the ID or serial number from list table")
    args = parser.parse_args()
    ec2obj = ec2_class()
    cfobj =  cf_class()
    if args.listcf:
        cfobj.list_all_cf()

    if args.launchcf:
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if(regex.search(args.launchcf) == None): 
            cfobj.create_stack(args.launchcf)
        else:
            print("The name which you had give has special characters.. please check")
            exit

    if args.deletecf:
        confirm = ec2obj.confirmation(args.deletecf)
        if confirm in ["Y","y"]:
            cfobj.delete_stack(args.deletecf)

    if args.describecf:
        cfobj.describe_stack(args.describecf)

    if len(sys.argv)<2:
        ec2obj.ec2_list_of_instances()
        ec2obj.table_format()

    if args.stop:
        ec2obj.ec2_list_of_instances()
        list_option_filter = ec2obj.range_mapper(args.stop)
        confirm = ec2obj.confirmation()
        if confirm in ["Y","y"]:
            ec2obj.stop_instance(list_option_filter)

    if args.start:
        ec2obj.ec2_list_of_instances()
        list_option_filter = ec2obj.range_mapper(args.start)
        confirm = ec2obj.confirmation()
        if confirm in ["Y","y"]:
            ec2obj.start_instance(list_option_filter)

    if args.term:
        ec2obj.ec2_list_of_instances()
        list_option_filter = ec2obj.range_mapper(args.term)
        confirm = ec2obj.confirmation()
        if confirm in ["Y","y"]:
            ec2obj.term_instance(list_option_filter)

    if args.create:
        ec2obj.create_sec_grp(args.create)

    if args.running in ("stopall","termall"):
        ec2obj.ec2_list_of_instances("running")
        list_option_filter = ec2obj.range_mapper(args.running)
        confirm = ec2obj.confirmation()
        if confirm in ["Y","y"]:
            if args.running == "stopall":
                ec2obj.stop_instance(list_option_filter)
            elif args.running == "termall":
                ec2obj.term_instance(list_option_filter) 

    if args.stopped in ("startall","termall"):
        ec2obj.ec2_list_of_instances("stopped")
        list_option_filter = ec2obj.range_mapper(args.stopped)
        confirm = ec2obj.confirmation()
        if confirm in ["Y","y"]:
            if args.stopped == "startall":
                ec2obj.start_instance(list_option_filter)
            elif args.stopped == "termall":
                ec2obj.term_instance(list_option_filter)
    
    if args.terminated:
        ec2obj.ec2_list_of_instances("terminated")
        ec2obj.table_format()

    if args.connect:
        ec2obj.connect_ec2(args.connect)
