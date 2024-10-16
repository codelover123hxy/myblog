---
title: "部署技巧——运维篇"
date: 2024-09-07T12:19:47+08:00
draft: false
author: hxy
categories: ["部署技巧"]
tags: ["经验"]
---
## 云服务器ssh登录
```powershell
ssh -p port username@ip
```

vscode
编辑 C:\Users\{username}\.ssh\config
```ini
# config
Host 云服务器
  HostName ip
  User username
  Port port
  IdentityFile  C:\Users\{username}\.ssh\id_{method} # 如果是秘钥，实现免密登录，更加安全
```
ssh-gen
生成私钥和公钥
公钥上传至服务器 `~/.ssh/authorized_keys`中

## 配置云服务器免密登录
```powershell
vim ~/.ssh/authorized_keys
```
复制秘钥至文件中

### vscode配置
```ini
# .config文件
Host name # 如云服务器
  HostName host # xx.xx.xx.xx
  User username
  Port port
  IdentityFile file-path
```
### powershell登录
```powershell
ssh -i file-path -p port username@host
```

## 调整秘钥权限教程
#### 1. 打开 PowerShell 或命令提示符：
以 管理员身份 运行 PowerShell。
#### 2. 执行以下命令来移除 Everyone 用户的权限并只允许当前用户访问文件：
修改权限步骤：
```powershell
icacls "C:\Users\PC\.ssh\id_rsa" /remove "Everyone"
icacls "C:\Users\PC\.ssh\id_rsa" /grant:r "PC:(F)"
icacls "C:\Users\PC\.ssh\id_rsa" /inheritance:r
```
#### 注释：
/remove "Everyone"：移除 Everyone 用户对该文件的权限。
/grant:r "PC:(F)"：授予当前用户（假设用户名是 PC）对文件的完全控制权限。如果你的用户名不是 PC，请将 PC 替换为你实际的用户名。
/inheritance:r：禁用从父目录继承的权限。

#### 3. 验证文件权限：
要检查文件的权限，执行以下命令：
```powershell
icacls "C:\Users\PC\.ssh\id_rsa"
你应该看到输出类似于：
C:\Users\PC\.ssh\id_rsa PC:(F)
这表示只有 PC 用户拥有完全控制权限。
```
#### 4. 再次尝试 SSH 连接：
bash
ssh -p **port** -i **secret_url** **username@ip**

## 后端守护进程部署
- 使用systemd守护进程
#### 1.上传jar包至服务器相关目录
#### 2.编写service
创建用户级service
```powershell
vim ~/.config/systemd/user/service-name.service
```
service-name.service
```ini
[Unit]
Description=Your Service
After=network.target

[Service]
ExecStart=java -jar xxx.jar
# 这里可以换成其他命令，仅支持一行，若有多个语句需写入sh
WorkingDirectory=/home/ubuntu/backend
Restart=always

[Install]
WantedBy=default.target
```
#### 3.运行以下脚本
```powershell
systemctl --user restart service-name
systemctl --user enable service-name # 实现服务器开机自启动
```

- 使用nohup命令
```powershell
nohup java -jar xxx.jar &
```
其中nohup和&相互配合。nohup保证退出终端继续运行，而&保证ctrl+C不会终止进程。

这是一种较为偷懒的部署方式，但开启关闭较为复杂，需要查找进程号。

- 使用后台终端
这种更适合长时间跑模型，可随时查看、终止。
```powershell
tmux new -s test
tmux at -t test
```

## 免插件一键上传服务器
现有插件有Alibaba Toolkit,然而自己写脚本更简便。
利用.bat文件 + scp命令实现
.bat 使用%variable%
```bat
set src_file=xxx

@REM 定义目标服务器信息
set dest_user=xxx
set dest_ip=xxx
set dest_path=xxx

@REM 定义 SSH 私钥路径
set ssh_key=C:/Users/PC/.ssh/id_rsa
@REM 定义端口号
set port=xxx

@echo start building... && npm run build && @echo start uploading... && scp -r -P %port% -i %ssh_key% %src_file% %dest_user%@%dest_ip%:%dest_path%

pause
```

## bash配置
```powershell
vim ~/.bachrc 或 ~/.zshrc
```
定义默认操作
#### 例如
```sh
export PATH=xxx:$PATH
export PYTHONPATH=xxx
cd your-path
if [ -f ~/.clash_profile ]; then
    source ~/.clash_profile
fi
```
```powershell
source ~/.bachrc 或 ~/.zshrc
```

## uwsgi容器部署
### 示例 django框架项目部署
可以用uwsgi容器和nginx部署django、flask框架的后端，实现稳定的运行。
- 配置uwsgi.ini
```ini
[uwsgi]
chdir = /home/myproject
module = myproject.wsgi:application
socket = 127.0.0.1:8000
master = true
processes = 4
threads = 2
pidfile = uwsgi.pid
daemonize = /home/myproject/run.log
disable-logging = true
pythonpath = /root/anaconda3/envs/django_new/lib/python3.10/site-packages
static-map = /static=//home/myproject/staticfiles
wsgi-file=myproject/wsgi.py
```
