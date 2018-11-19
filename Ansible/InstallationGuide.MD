# Installing Maven on RHEL Linux

### Install Ansible on the New Server.

1. Update packages
```sh
yum update -y
```
2. Install the below packages
```sh
yum install -y wget unzip
```
3. Get the epel-release 
```sh
 wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
 yum install localhost epel-release-latest-7.noarch.rpm
```

# Maven Installation on RHEL server

1. Install Ansible on the server
```sh
yum install ansible -y
```
2. create a user for ansible
```sh
useradd ansible
passwd ansible
```
3. Edit the host file
```sh
vi /etc/ansible/hosts
[web-servers]
192.168.0.1
192.168.0.2

[app-servers]
192.168.1.1
192.168.1.2
```
4. Create a ansible user in the host servers as well
```sh
useradd ansible
passwd ansible
```
5. Give the passwordless and root privileges for ansible user
```sh
visudo
```
6. add the this line after (root    ALL=(ALL)       ALL)
```sh
ansible      ALL=(ALL)       NOPASSWD: ALL
```

# If you had Build the servers in AWS Environment

1. please change the password authetication.
```sh
vi /etc/ssh/sshd_config
```
2. Below mentioned lines should be changed
```sh
#PasswordAuthentication yes
#PermitEmptyPasswords no
PasswordAuthentication no
```
3. change it as below mentioned
```sh
PasswordAuthentication yes
#PermitEmptyPasswords no
#PasswordAuthentication no
```
4. Change the same settings on the host servers as well and restart the sshd service
```sh
service sshd restart
```

# Change the configurations

1. Establish the SSH connectivity between the servers`
```sh
ssh-keygen
```
2. copy the RSA key to the servers
```sh
ssh-copy-id 192.168.0.1
ssh-copy-id 192.168.0.2
ssh-copy-id 192.168.1.1
ssh-copy-id 192.168.1.1
```

# Check the Ping connectivity between the hosts

1. To check the connectivity
```sh
ansible -m ping all
```

# Flush all the firewall Rules on the server side

1. Clear the Iptables
```sh
iptables -F
```
2. Stop the firewalld service
```sh
service firewalld stop
```
3. Disable the SELINUX firewall
```sh
sestatus
vi /etc/sysconfig/selinux
```

# Troubleshooting

1. Check for the ennvironment configurations

