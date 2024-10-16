---
title: "部署技巧——nginx（前端、图床等）"
date: 2024-09-07T12:19:47+08:00
draft: false
author: hxy
categories: ["部署技巧"]
tags: ["经验"]
---
## nginx配置教程
```powershell
cd /etc/nginx/conf.d
vim src/myblog.conf
```
输入以下代码:
```ini
# myblog.conf
server {
    listen       port;
    server_name  localhost;
      
    location / {
        try_files $uri $uri/ =404;
        root /home/hxy/myblog/public;
        index index.html index.xml;
    }
}
```
### nginx无法解析
1. 没有赋予html目录权限
一般放在/usr/share/nginx/xxx
若是其他目录，需要手动赋权。确保nginx用户可正常访问
2. 域名解析错误
3. 云服务器未打开

### 配置https
- 申请https证书
免费获取证书 [ohttps网站](https://www.ohttps.com/)

```ini
server {
	listen 80;
	server_name your-domain;
	rewrite ^(.*)$ https://$host:443$1 permanent;
	location / {
    		proxy_pass http://localhost:port;
	}
}
```

```ini
server {
    listen 443 ssl; 
    server_name blog.aiyin.club; 
    ssl_certificate path/aiyin.club.pem; 
    ssl_certificate_key path/aiyin.club.key; 
    ssl_session_timeout 5m;
    ssl_protocols TLSv1.2 TLSv1.3; 
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE; 
    ssl_prefer_server_ciphers on;

    location / {
        try_files $uri $uri/ @router;
        root  /path-to-html;
        index  index.html index.htm;
    }
 }
```

## nginx搭建自己的图床
众所周知，图床有多种搭建方法，如oss、云开发托管等，而nginx+自己的服务器是一种轻便的图床搭建方法。

1. 首先在服务器上选择一个放图片的目录，如~/imagehost
2. sudo vim /etc/nginx/conf.d/imagehost.conf
输入配置内容
```ini
server {
    listen port;
    server_name  localhost;

    location / {
        index  index.php index.html index.htm;
    }
    
    error_page 500 502 503 504  /50x.html;
     
    location /imagehost/ {
        root /home/{username}/imagehost/; # 绝对路径
    }
}

# 将图床服务转发到子域名上 https://image.xxx.cn
server{
    listen 80;
    server_name image.xxx.cn;
    rewrite ^(.*)$ https://$host:443$1 permanent; # 自动https
    location / {
        proxy_pass http://localhost:port;
    }
}
```
3. 访问https://image.xxx.cn/{filename}{suffix}，suffix为图片后缀，如.jpg、.png等

事实上，~/imagehost中还可存放其他任意文件。需要保证云服务器的带宽满足图床要求。

### 快速上传到自己的图床
- 编写后端上传接口，用apifox上传
- 使用picgo工具上传

1. 

   ![](https://image.familystudy.cn/image/generic/image-2.png)

2. 编写.json文件。可存入C:\Users\{username}\.config\picgo目录
```json
{
	"MyImagehost": {
		"url": "https://image.xxx.cn",
		"path": "/image/jxfruit/{fullName}",
		"uploadPath": "/home/hxy/imagehost/image/jxfruit/{fullName}",
		"host": {ip},
		"port": {port},
		"username": {username},
		"privateKey": {privateKey_path}
	}
}
```
3. 

![alt text](https://image.familystudy.cn/image/generic/image-3.png)

### 开启一键上传

事实上，有诸多方法上传。仅需连接**ssh + 移动文件**
也可前端利用组件库完成快速上传。
