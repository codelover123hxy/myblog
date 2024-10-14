---
title: "Go项目部署+实战（一）"
subtitle: ""
date: 2024-10-02T18:38:14+08:00
lastmod: 2024-10-02T18:38:14+08:00
draft: 
author: "hxy"
authorLink: ""
license: ""
tags: ["技巧"]
categories: ["技巧"]
featuredImage: ""
featuredImagePreview: ""
summary: ""
hiddenFromHomePage: false
hiddenFromSearch: false
toc:
  enable: true
  auto: true
mapbox:
share:
  enable: true
comment:
  enable: true
---

## go项目部署+实战（一）
### 写在前面
从大二下接触后端开始，笔者一直使用Springboot+mybatis+Redis这一套。
此次开发新项目，一方面想尝试新语言，另一方面听说go具有高并发的优势，故采用go语言。

花费了一晚上的时间完成配置以及初步编程，并记录了部署和实战过程中的一些技巧和问题。

### 项目伊始
笔者采用了go + gin + gorm的主流框架
采用go get -u xxx下载包，下载后自动更新在go.mod中。十分类似于maven。
```powershell
go get -u github.com/gin-gonic/gin
go get -u gorm.io/gorm
go get -u gorm.io/driver/mysql
```
![alt text](../image-6.png)
出现报错。显然，和pip、apt安装时类似，采用换源方法，配置国内源。
```powershell
go env -w GOPROXY=https://mirrors.aliyun.com/goproxy,direct
```

```markdown
1. 在 golang 安装路径下寻找：
'go1.17.2\src\runtime\internal\sys\zversion.go' 文件
2. 打开 'zversion.go' 文件，在其中追加如下行（你的版本号）并保存
const TheVersion = `go1.23.2`
3. 再次 配置 goland 的 GOROOT 路径，即可正常配置
```

配置好后，运行
```powershell
go run main.go
```

### 打包部署云服务器
相比于java，go的打包部署更为简单。
总结而言，采用.bat + .ssh方式，一键部署。

编写.bat文件实现一键上传
```bat
@echo off
set GOOS=linux
set GOARCH=amd64
go build -o server_name main.go

scp -P port -i C:\Users\PC\.ssh\id_rsa_ddhl chorus_server config.yaml username@ip:your-path

ssh -p port -i C:\Users\PC\.ssh\id_rsa_ddhl username@ip "/{your-path}/startup.sh"
```
#### 注意
set GOOS=linux

set GOARCH=amd64
两句话不可省略，否则默认打包成exe。

### 配置ssl证书
类似于java，go的配置更为简洁。

```go
func main() {
	config.InitDB()
	r := gin.Default()
	routers.SetupRouter(r)
	// 启动 HTTPS 服务器
	err := r.RunTLS(":{port}", "/your-path/fullchain.pem",
		"/your-path/privateKey.pem")
	if err != nil {
		log.Fatalf("Failed to start HTTPS server: %v", err)
	}
}
```

### 配置viper读取yaml
go项目中，可用viper读取yaml文件。
```go
import (
	"github.com/spf13/viper"
)
var Config = viper.New()
func init() {
	// 设置配置文件名（不需要后缀）
	Config.SetConfigName("config")
	// 设置配置文件的路径，可以设置多个路径，Viper 会自动搜索
	Config.AddConfigPath(".") // 当前目录
	// 设置配置文件的格式
	Config.SetConfigType("yaml")
	// 读取配置文件
	if err := Config.ReadInConfig(); err != nil {
		log.Fatal("Config not find", err)
	}
}
```

至此，基本配置已经完成。后续将阐述go+gin+gorm开发中的技巧与难点。
