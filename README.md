# Devops
devops installation file


# to install and configure awscli and boto3 in AWS

```sh
yum update -y
yum install -y python3
python3 --version
pip3 --version
pip3 install awscli
export PATH=~/.local/bin:$PATH
source ~/.bash_profile
aws configure  
```
If pip isn't installed with python then try to get the appropriate pip
```sh
cd /tmp
curl -O https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py --user
pip3 --version
```
