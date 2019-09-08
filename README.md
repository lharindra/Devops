# Devops
devops installation file


# to install and configure awscli and boto3

```sh
       cd /tmp
  506  curl -O https://bootstrap.pypa.io/get-pip.py
  507  python3 get-pip.py --user
  508  pip3 --version
       pip3 install awscli
  536  export PATH=~/.local/bin:$PATH
  537  source ~/.bash_profile
       aws configure
       
```
