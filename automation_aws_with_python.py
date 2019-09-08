#!/usr/local/bin/python3
import boto3

class main_class():
    def __init__(self):
        self.ec2_conn_list = boto3.client('ec2')
        self.ec2_conn_create = boto3.resource('ec2')
        self.total_inst_list = {}
        self.inst_running = []
        self.inst_term = []
        self.inst_stop = []

    def ec2_list_of_instances(self):
        ec2_responce = self.ec2_conn_list.describe_instances()
        for reservation in ec2_responce["Reservations"]:
            for instance in reservation["Instances"]:
                inst_id = instance["InstanceId"]
                if instance["State"]["Name"] == "running":
                    self.total_inst_list[inst_id] = "Running"
                elif instance["State"]["Name"] == "terminated":
                    self.total_inst_list[inst_id] = "Terminated"
                elif instance["State"]["Name"] == "stopped":
                    self.total_inst_list[inst_id] = "Stopped"
        for k, v in self.total_inst_list.items():
            if v == "Running":
                self.inst_running.append(k)
            elif v == "Terminated":
                self.inst_term.append(k)
            elif v == "Stopped":
                self.inst_stop.append(k)
        if len(self.inst_running) != 0:
                print("Running:- {0}".format(",".join(self.inst_running)))
        if len(self.inst_term) != 0:
                print("Terminated:- {0}".format(",".join(self.inst_term)))
        if len(self.inst_stop) != 0:
                print("Stopped:- {0}".format(",".join(self.inst_stop)))
        
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

    #def show_and_choose(self):

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
