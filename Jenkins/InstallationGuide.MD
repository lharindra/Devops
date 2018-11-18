# Installing Jenkins on RHEL Linux

1. Update packages
```sh
yum update -y
```
2. Update the Hostname file
```sh
echo "jenkins.rulepaper.com" > /etc/hostname
```
3. Install the below packages
```sh
yum install -y wget
yum install -y java
yum install -y java-1.8.0-openjdk*
```
4. Check the Java version
```sh
java -version
```

# Making the Java home directory

1. edit the /root/.bash_profile
```sh
PATH=$PATH:$HOME/bin:$JAVA_HOME:$M2_HOME:$M2
JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.191.b12-1.el7_6.x86_64
```
2. To get it reflected
```sh
source /root/.bash_profile
```

# Jenkins Installation on RHEL server

1. Get the Jenkins Repo
```sh
sudo wget -O /etc/yum.repos.d/jenkins.repo http://pkg.jenkins-ci.org/redhat-stable/jenkins.repo
```
2. import the keys
```sh
sudo rpm --import https://jenkins-ci.org/redhat/jenkins-ci.org.key
```
# Install package of Jenkins

1. Install Jenkins package
```sh
sudo yum install jenkins -y
```
2. start the service and Enable it
```sh
service jenkins start
sudo chkconfig jenkins on
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

# Check the process whether it is running on the server

1. Check the stauts
```sh
service jenkins status
```
2. check the process
```sh
ps -ef | grep -i jenkins
```
# Check for the intial password 

```sh
cat /var/lib/jenkins/secrets/initialAdminPassword
```

# Troubleshooting

1. Check for the security groups whether you had enabled port 8080
