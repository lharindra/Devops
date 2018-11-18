# Installing Maven on RHEL Linux

### Install Maven on the Jenkins Server.

1. Update packages
```sh
yum update -y
```
2. Install the below packages
```sh
yum install -y wget
yum install -y java
yum install -y java-1.8.0-openjdk*
```
3. check the java version
```sh
java -version
```

# Making the Java home directory

1. edit the /root/.bash_profile
```sh
PATH=$PATH:$HOME/bin:$JAVA_HOME:$M2_HOME:$M2
M2_HOME=/opt/apache-maven-3.6.0
M2=$M2_HOME/bin
```
2. To get it reflected
```sh
source /root/.bash_profile
```

# Maven Installation on RHEL server

1. Get the Maven Repo
```sh
cd /opt/
wget http://mirrors.estointernet.in/apache/maven/maven-3/3.6.0/binaries/apache-maven-3.6.0-bin.zip
```
2. Unzip the zip file
```sh
sudo unzip apache-maven-3.6.0-bin.zip
```

# Change the configuraations

1. change the configuration file /etc/environment
```sh
vi /etc/environment
```
2. Add the below mentioned line in the /etc/environment
```sh
M2_HOME="/opt/apache-maven-3.6.0"
/opt/apache-maven-3.6.0/bin
```

# Update the MVN command

1. Add mvn
```sh
sudo update-alternatives --install "/usr/bin/mvn" "mvn" "/opt/apache-maven-3.6.0/bin/mvn" 0
sudo update-alternatives --set mvn /opt/apache-maven-3.6.0/bin/mvn
```
2. Add Bash completion to mvn so that you can compltecomplex Maven commands by hitting Tab multiple times.
```sh
sudo wget https://raw.github.com/dimaj/maven-bash-completion/master/bash_completion.bash --output-document /etc/bash_completion.d/mvn
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

1. Check the version
```sh
mvn --version
```

# Troubleshooting

1. Check for the ennvironment configurations

