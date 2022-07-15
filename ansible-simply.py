import os,sys
import re
import argparse
import time
import logging
import multiprocessing
import paramiko
from tqdm import tqdm


########------------------------------------------------------########
# 提取host.txt 解析远程主机的IP，端口，用户名，和密码
def GetIPListFromFile(filename):
    IP_LIST = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.replace('\n', '')
            ip_seq = line.split(".")
            ip_seq_0 = int(ip_seq[0])
            ip_seq_1 = int(ip_seq[1])
            ip_seq_2 = int(ip_seq[2])
            ip_user_pwd = ip_seq[3].split(",")
            ip_seq_3 = ip_user_pwd[0]
            ssh_user = ip_user_pwd[1]
            ssh_pwd = ip_user_pwd[2]
            matchObj = re.search('-', ip_seq_3)
            if matchObj:
                endseg = ip_seq_3.split("-")
                IPBegin = int(endseg[0])
                IPEnd_end = endseg[1].split(":")
                IPEnd = int(IPEnd_end[0])
                ssh_port = IPEnd_end[1]
                # print(IPEnd)
                while IPBegin <= IPEnd:
                    aIP = str(ip_seq_0) + '.' + str(ip_seq_1) + '.' + str(ip_seq_2) + '.' + str(IPBegin) + ',' + str(
                        ssh_port) + ',' + \
                          str(ssh_user) + ',' + str(ssh_pwd)
                    IP_LIST.append(aIP)
                    '''
          print(f'解析后的IP列表是：{ip_seq_0}.{ip_seq_1}.{ip_seq_2}.{IPBegin} ,SSH端口是：{ssh_port}, 主机用户名：{ssh_user}, '
                f'主机密码：{ssh_pwd}')
          '''
                    IPBegin += 1
            else:
                # print(ip_seq_3)
                IPEnd_end = ip_seq_3.split(":")
                IPEnd = int(IPEnd_end[0])
                ssh_port = IPEnd_end[1]
                aIP = str(ip_seq_0) + '.' + str(ip_seq_1) + '.' + str(ip_seq_2) + '.' + str(IPEnd) + ',' + str(
                    ssh_port) + ',' + \
                      str(ssh_user) + ',' + str(ssh_pwd)
                IP_LIST.append(aIP)
                '''
        print(f'解析后的IP列表是：{ip_seq_0}.{ip_seq_1}.{ip_seq_2}.{IPEnd} ,SSH端口是：{ssh_port}, 主机用户名：{ssh_user},'
              f'主机密码：{ssh_pwd}')
        '''
        return IP_LIST


########------------------------------------------------------########
# 执行远程主机上的Linux命令
class TaskManager:
    def ssh_connect(self, ip, ssh_port, ssh_user, ssh_passwd):
        try:
            # 连接服务器
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=ip, port=ssh_port, username=ssh_user, password=ssh_passwd, banner_timeout=60,
                           timeout=10)
        except Exception as e:
            print('\x1b[1;31m主机：%s ssh连接失败!!! 错误信息：%s \x1b[0m' % (ip, str(e)))
        return client  # 返回client实例化对象

    def ssh_exec(self, ip, ssh_port, ssh_user, ssh_passwd, remote_cmd):
        # 把client对象赋值给变量ssh
        ssh = self.ssh_connect(ip, ssh_port, ssh_user, ssh_passwd)
        local_ip = "echo -e \"\E[1;32m ===> ==> => $(/sbin/ip addr |  grep -w 'inet'   \
                            | egrep -v '127.0.0.1|/32' | grep 'brd' | awk '{print $2}'  \
                            | cut -d'/' -f1 | head -n 1;echo) ===> ==> => OK! \E[0m\" "
        tqdm_para = "|/usr/bin/env python3 -m tqdm --total=$(" + remote_cmd + "|wc -l) --unit=\'毫秒\', --unit_scale --colour=\'green\' --desc=\'Processing\'"

        '''
        sudo使用方法
        https://stackoverflow.com/questions/6270677/how-to-run-sudo-with-paramiko-python
        https://codingdict.com/questions/169384
        '''
        sudo = '/usr/bin/sudo -S /bin/bash -c  '
        #stdin, stdout, stderr = ssh.exec_command(local_ip + ';' + sudo + '\'' + remote_cmd + tqdm_para + '\'' ,get_pty=True)
        # ,get_pty=True)
        stdin, stdout, stderr = ssh.exec_command(local_ip + ';' + sudo + '\'' + remote_cmd + '\'')
        stdin.write(ssh_passwd + '\n')  # 自动输入密码
        stdin.flush()
        ### 获取命令返回值 ###################
        channel = stdout.channel
        status = channel.recv_exit_status()
        ######################################
        if status == 0:
            print(stdout.read().decode('utf-8'))
        else:
            print('\x1b[1;31m执行命令: {0} 失败 - {1}\x1b[0m'.format(remote_cmd, ip))
            print(stderr.read().decode('utf-8'))
        # 关闭连接
        ssh.close()

    def __get_all_files_in_local_dir(self, local_dir):
        """
        实现目录上传
        :param local_dir: 传入上传的目录
        :return: 返回目录下的所有文件，包含子目录的所有文件
        """
        mark = str()
        all_files = []
        if os.path.exists(local_dir):
            if os.path.isfile(local_dir):
                all_files.append(local_dir)
                mark = 'isfile'
            else:
                files = os.listdir(local_dir)
                for f in files:
                    filename = os.path.join(local_dir, f)
                    # print("文件名是:" + filename)
                    # 判断是否包含子目录
                    if os.path.isdir(filename):
                        all_files.extend(self.__get_all_files_in_local_dir(filename))
                    else:
                        all_files.append(filename)
                mark = 'isdir'
            return all_files, mark
        else:
            print('{}上传的文件或目录不存在，请检查！'.format(local_dir))
            pool.terminate()
            sys.exit(1)

    def sftp_put_dir(self, ip, ssh_port, ssh_user, ssh_passwd, local_dir, remote_dir):
        # 把client对象赋值给变量ssh
        remote_file = str()
        ssh = self.ssh_connect(ip, ssh_port, ssh_user, ssh_passwd)
        sftp = ssh.open_sftp()

        if local_dir[-1] == '/':
            local_dir = local_dir[0:-1]

        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]

        all_files, mark = self.__get_all_files_in_local_dir(local_dir)

        if mark == 'isdir':
            tmp_all_files = re.sub('(\[|\]|isdir| +|\')', "", str(all_files)).split(',')
            all_files = [i for i in tmp_all_files if i != '']

        for file in all_files:
            filename = os.path.split(file)[-1]
            if mark == 'isdir':
                remote_file = os.path.split(file)[0].replace(local_dir, remote_dir)
            elif mark == 'isfile':
                remote_file = remote_dir
            else:
                pass
            path = remote_file
            # 创建多级目录
            sudo = '/usr/bin/sudo -S /bin/bash -c  '
            stdin, stdout, stderr = ssh.exec_command(sudo + '\'' + 'mkdir -p ' + path + ';'
                                                     + 'chown -R ' + ssh_user + '.' + ssh_user + ' ' + path + '\'')
            stdin.write(ssh_passwd + '\n')  # 自动输入密码
            stdin.flush()
            ### 获取命令返回值 ###################
            channel = stdout.channel
            status = channel.recv_exit_status()
            ######################################
            if status == 0:
                print(stdout.read().decode('utf-8'))
            else:
                print('\x1b[1;31m创建目录失败: {0} 失败 \x1b[0m'.format(path))
                print(stderr.read().decode('utf-8'))
            try:
                remote_filename = path + '/' + filename
                print('上传路径：%s  上传文件：%s' % (path, filename))
                sftp.put(file, remote_filename)
            except Exception as e:
                print('\x1b[1;31m主机：%s 上传文件失败!!! 错误信息：%s \x1b[0m' % (ip, str(e)))
        # 关闭连接
        ssh.close()

######################################################################
# end class TaskManager
########------------------------------------------------------########
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='ansible-simple简易版')
    parser.add_argument('inventory', help='host.txt主机ip文件')
    parser.add_argument('-c', '--cmd', dest='cmd', type=str, metavar='', required=False,
                        help='输入执行的命令，多个命令用;分号分割')
    parser.add_argument('-p', '--mput', dest='msftp', type=str, nargs=2, metavar='',
                        required=False, help='sftp上传目录文件 [本地路径]  [远程路径]')
    args = parser.parse_args()
    #print(args)
    # 第一步，先获取到主机ip信息
    result = GetIPListFromFile(args.inventory)

    # 第二步，实例化对象
    task = TaskManager()
    pool = multiprocessing.Pool(processes=os.cpu_count())

    # 第三步，定义执行进度条
    pbar = tqdm(total=len(result), unit='秒', unit_scale=True)
    pbar.set_description('任务执行总进度')
    update = lambda x: pbar.update()

    if args.cmd and args.msftp:
        print('\n')
        print('\x1b[1;31m只能输入一个参数-c或者-p\x1b[0m','\n')
        sys.exit(0)  
    elif args.cmd:
        for i in result:
            ip, ssh_port, ssh_user, ssh_passwd = i.split(",")
            pool.apply_async(task.ssh_exec, (ip, ssh_port, ssh_user, ssh_passwd, args.cmd), callback=update)
        pool.close()
        pool.join()
        print('\n' + '-' * 100)
        print('执行命令: 【 {0} 】结束 '.format(args.cmd), time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime()), '\n')
    elif args.msftp:
        for i in result:
            ip, ssh_port, ssh_user, ssh_passwd = i.split(",")
            pool.apply_async(task.sftp_put_dir, (ip, ssh_port, ssh_user,
                                                 ssh_passwd, args.msftp[0], args.msftp[1]), callback=update)
        pool.close()
        pool.join()
        print('\n' + '-' * 100)
        print('本地目录：{0} 已上传至远程目录：{1} '.format(args.msftp[0], args.msftp[1]),
              time.strftime('%Y-%m-%d %H:%M:%S %Z', time.localtime()), '\n')
    else:
        print('\n')
        print('\x1b[1;31m请输入参数-c或者-p\x1b[0m','\n')
        sys.exit(0)
