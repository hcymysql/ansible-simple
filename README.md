# ansible-simple
ansible简易版，是我日常工作中经常使用到的批量执行命令和上传文件，参考了ansible工作模式，根据自己的情况定制了一个ansible-simple

# 依赖的第三方模块库
```
shell> pip3 install paramiko  -i "http://mirrors.aliyun.com/pypi/simple" --trusted-host "mirrors.aliyun.com"

shell> pip3 install argparse  -i "http://mirrors.aliyun.com/pypi/simple" --trusted-host "mirrors.aliyun.com"

shell> pip3 install tqdm  -i "http://mirrors.aliyun.com/pypi/simple" --trusted-host "mirrors.aliyun.com"
```
-------------------------------------------------------

使用介绍：
```
# chmod 755 ansible-simple
# ./ansible-simple --help
```
usage: ansible-simple [-h] [-c] [-p ] inventory

ansible-simple简易版（默认按照CPU核数并发执行）

positional arguments:

  inventory       host.txt主机ip文件

optional arguments:

  -h, --help      show this help message and exit
  
  -c , --cmd      输入执行的命令，多个命令用;分号分割
  
  -p  , --mput    sftp上传目录文件 [本地路径] [远程路径]
  
  
# 1）host.txt文件格式如下：

ip:ssh端口,用户名,密码（端口不能省，必须加上）
```
shell> cat host.txt

192.168.137.131:22,hechunyang,123456

如果想设置连续多个ip机器列表，加一个横杠，如下：

192.168.137.131-150:22,hechunyang,123456
```
# 2）支持上传文件和目录
```
shell> ./ansible-simple host.txt -p '/root/soft' '/tmp/soft/'
```
将本地/root/soft文件夹上传至远程主机/tmp/soft/目录下

# 3) 执行远程主机Linux命令
```
shell> ./ansible-simple host.txt -c 'df -hT;date'
```
![image](https://raw.githubusercontent.com/hcymysql/ansible-simple/main/%E6%89%A7%E8%A1%8C%E5%91%BD%E4%BB%A4.png)
![image](https://raw.githubusercontent.com/hcymysql/ansible-simple/main/%E4%B8%8A%E4%BC%A0%E6%96%87%E4%BB%B6%E7%9B%AE%E5%BD%95.png)

#### 批量创建用户修改密码
```
shell> ./ansible-simple host.txt -c 'useradd hechunyang;echo "123456" | passwd --stdin hechunyang;echo "hechunyang    ALL=(ALL)NOPASSWD: ALL" >> /etc/sudoers'
```
#### 注：工具适用于Centos7 系统。
