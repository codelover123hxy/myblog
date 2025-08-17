---
title: "部署技巧——clash"
date: 2024-09-07T12:19:47+08:00
lastmod: 2024-12-03T15:36:53+08:00
draft: false
author: hxy
categories: ["部署技巧"]

tags: ["经验"]
---
## clash 配置教程

部署AI模型经常需要从github和huggingface上clone文件，然而每次本地下载后拷贝服务器十分麻烦且耗时，尤其当大模型有几十个G时，因此需要在linux服务器上配置clash。笔者经过一段时间的探索，在两类Linux服务器上成功部署了Clash。网上的配置方法繁杂且质量不高，极具误导性，因此写一篇博客来总结。

### 配置方法

#### 纯命令行Linux服务器

1. 下载clash-for-linux [链接](https://github.com/wnlen/clash-for-linux)  里面也讲述了后续步骤。

2. 配置.env文件

```bash
cd clash-for-linux
vim .env
```

把`CLASH_URL`设置为你的Clash订阅地址。

3. 启动clash

```bash
sudo bash start.sh
```

4. 执行后续指令

```bash
source /etc/profile.d/clash.sh
proxy_on
```

#### 注意

如果没有sudo权限，需要做局部修改。

将

``````bash
cat>/etc/profile.d/clash.sh<<EOF
``````

修改为

```bash
cat>~/.clash_profile<<EOF
```

#### 图形化界面的Linux

针对具有图形化界面的Linux系统用户来说，往往需要在浏览器中访问google等网站。使用上述命令行的方法，无法针对浏览器奏效。
笔者经过实践，给出下面完整的方法。

1. 下载兼容Linux的**Clash-for-Windows** [链接](https://github.com/handshow888/Clash-for-Windows-0.20.30-x64-linux)

```bash
tar -xf Clash\ for\ Windows-0.20.30-x64-linux.tar.xz
cd Clash\ for\ Windows-0.20.30-x64-linux/
./cfw
```

之后可双击图标打开Clash。

2. 导入节点

   和Windows上一样，将订阅地址复制至Profiles处，选择节点

   ![image-20241203150739575](https://media.tidechoir.cn/image/image-20241203150739575.png)

   等待成功导入即可。

3. 配置代理

   clash配置后，还需要单独在系统设置中配置代理。

   ![image-20241203150543046](https://media.tidechoir.cn/image/image-20241203150543046.png)

   ![image-20241203150614216](https://media.tidechoir.cn/image/image-20241203150614216.png)

将代理改为手动，并将HTTP和HTTPS的URL均改为127.0.0.1，端口改为7890。大功告成！

#### 遇到的bug

配置过程中，首先使用clash-for-linux，但无法正常使用。随后下载兼容Linux的Clash-for-Windows后，笔者成功将订阅地址导入，同时配置了代理。然而所有节点都是Time out。反复尝试无果，最后发现换了一个订阅地址就能正常使用！星链计划（星星加速器）**不适用**该版本的Clash。