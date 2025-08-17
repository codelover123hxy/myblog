---
title: "部署技巧——hugo博客"
date: 2024-10-15T12:19:47+08:00
draft: false
author: hxy
categories: ["部署技巧"]
tags: ["经验"]
---

# Hugo博客部署教程

## 写在前面

今天，笔者有空整理了下hugo搭建教程。

首先在云服务器上下载hugo，pick自己喜欢的主题（我选择了Lovelt）、配置.toml文件 。这些网上有详细的教程，不予赘述。

下面介绍一些小技巧。

### 友链的配置

hugo本身提供了posts、tags、categories，并没有提供友链。因此需要自己单独配置。

在layouts/shortcodes中加入代码friend.html

```html
{{ if .IsNamedParams }}
    {{- $src := .Get "logo" -}}
    {{- $small := .Get "logo_small" | default $src -}}
    {{- $large := .Get "logo_large" | default $src -}}
    <div class="flink" id="article-container">
      <div class="friend-list-div" >
        <div class="friend-div">
            <a target="_blank" href={{ .Get "url"  | safeURL }} title={{ .Get "name" }} >
                <img class="lazyload"
                     src="/svg/loading.min.svg"
                     data-src={{ $src | safeURL }}
                     alt={{ .Get "name" }}
                     data-sizes="auto"
                     data-srcset="{{ $small | safeURL }}, {{ $src | safeURL }} 1.5x, {{ $large | safeURL }} 2x" />
                <span class="friend-name">{{ .Get "name" }}</span>
                <span class="friend-info">{{ .Get "word" }}</span>
            </a>
        </div>
      </div>
    </div>
{{ end }}
```

并且在content/friend/index.md中加入

```html
---
hiddenFromSearch: true
---
{{/*%<friend name="name" url="url" logo="path-to-logo" word="blog-name">%*/}}
```

至此，友链配置完毕，博客总览如下。

![image-20241015020743970](https://image.familystudy.cn/image/generic/image-20241015020743970.png)

### Typora+Github同步部署

由于每次都需要vscode打开服务器进行编辑，有些麻烦。笔者想到利用markdown工具Typora在本地编辑，然后利用github作为中间媒介完成上传。一来可以利用仓库完成博客内容备份，二来不必每次都登录服务器。

仓库如下：

![](https://image.familystudy.cn/image/generic/image-20241015015634271.png)

然而手动更新仍十分麻烦，每次都需要在服务器上git pull更新最新内容。

因此想到cron表达式执行定时任务。此前介绍过，cron -e可以设置执行时间和任务。这里设置为* */1 * * * 表示每小时定时执行一次。

笔者利用.sh文件集成打开clash代理 + git pull + hugo上传的一整套流程。

```sh
# !/bin/bash
source /etc/profile.d/clash.sh
proxy_on
cd /home/hxy/myblog
git pull origin main
hugo
```

至此，仅需每次将博客在Typora中编辑好，上传github即可。若要进一步“偷懒”，还可以编写.bat文件。

这样连git add xxx、git commit、git push xxx等都不需要写了。

#### picgo + typora上传图片

由于hugo的图片存在static中，使用绝对路径渲染，无法在markdown中预览，因此采用图床的方法。

在typora中配置picgo，如图所示，至此将实现图片自动上传。

![image-20241016231210425](https://image.familystudy.cn/image/generic/image-20241016231210425.png)

#### github action自动执行脚本

除了定时任务外，还可使用github action完成commit后自动执行脚本。

![image-20241016231526147](https://image.familystudy.cn/image/generic/image-20241016231526147.png)

可在.github/workflows里面编写.yaml文件。

```yaml
name: Deploy My Blog

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ip -p port >> ~/.ssh/known_hosts # 若端口号不是22，不能省略

      - name: Deploy
        run: |
          ssh -i ~/.ssh/id_rsa -p port username@ip "xxx.sh"
```

这样可以使得git push时自动执行后面的脚本。不需要手动登录服务器 git pull。
