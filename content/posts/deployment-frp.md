---
title: "部署技巧——内网穿透"
date: 2024-09-19T12:53:47+08:00
draft: false
author: hxy
categories: ["部署技巧"]
tags: ["经验"]
---
## 内网穿透
### ngrok快速穿透
优点：简单，新手上手很快。
缺点：依赖别人的服务器，每次生成的url不同。
### frp自由配置
frp可快速实现端口代理，可将本地和服务器、服务器之间端口转发。

1. 下载对应的frp版本，windows或linux版。
2. 配置文件

frp的目录如下
-frp
    -frpc
    -frps
    -frpc.ini
    -frpc.toml
    -frps.toml

s代表服务端，也就是提供端口服务的主机，c代表客户端，也就是需要转发的主机
下面以frpc.ini为例
```ini
[common]
server_addr = xx.xx.xx.xx
server_port = bind_port

[ssh] ;配置ssh端口,用于在其他服务器上访问该服务器
type = tcp
local_port = xxx ;本机端口
local_ip = 127.0.0.1
remote_port = xxx ;远程端口

[http] ;配置http
type = tcp
local_port = xxx ;本机端口
local_ip = 127.0.0.1
remote_port = xxx ;远程端口
```
frps.ini对应
```ini
[common]
bind_port =  bind_port
```
就这样，内网穿透就完成了。