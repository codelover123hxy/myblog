---
title: "部署技巧——clash"
date: 2024-09-07T12:19:47+08:00
draft: false
author: hxy
categories: ["部署技巧"]
tags: ["经验"]
---

## clash 配置教程
部署AI模型经常需要从github和huggingface上clone文件，然而每次本地下载后拷贝服务器十分麻烦且耗时，尤其当大模型有几十个G时。
因此有必要直接在linux服务器上配置clash。
### 步骤
1. 下载clash-for-linux
2. 配置.env文件
```powershell
vim .env
```
把`CLASH_URL`设置为你的Clash订阅地址。

3. 启动clash
```powershell
sudo bash start.sh
```
4. 配置clash.sh文件
```vim /etc/profile.d/clash.sh
# 把上面所有的 127.0.0.1 修改为自己的 ip 地址，保存退出
source /etc/profile.d/clash.sh
```
