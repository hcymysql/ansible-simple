# ansible-simple
ansible简易版，是我日常工作中经常使用到的批量执行命令和上传文件，参考了ansible工作模式，根据自己的情况定制了一个ansible-simple

使用介绍：
# python3 ansible-simply.py --help
usage: ansible-simply.py [-h] [-c] [-p ] inventory

ansible-simple简易版

positional arguments:

  inventory       host.txt主机ip文件

optional arguments:

  -h, --help      show this help message and exit
  
  -c , --cmd      输入执行的命令，多个命令用;分号分割
  
  -p  , --mput    sftp上传目录文件 [本地路径] [远程路径]
  
  
# 1）host.txt文件格式如下：

ip:ssh端口,用户名,密码（端口不能省，必须加上）

cat host.txt

192.168.137.131:22,hechunyang,159753

如果想设置连续多个ip机器列表，加一个横杠，如下：

192.168.137.131-150:22,hechunyang,159753

# 2）支持上传文件和目录

python3 ansible-simply.py host.txt -p '/root/soft' '/tmp/soft/'

将本地/root/soft文件夹上传至远程主机/tmp/soft/目录下

# 3) 执行远程主机Linux命令

python3 ansible-simply.py host.txt -c 'df -hT;date'


