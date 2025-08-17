---
title: "Taro"
subtitle: ""
date: 2024-09-30T22:25:26+08:00
lastmod: 2024-09-30T22:25:26+08:00
draft: true
author: "hxy"
authorLink: ""
license: ""
tags: ["技巧"]
categories: [""]
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

# taro 开发小程序

## 配置

按照官网文档开始配置，过程总体比较顺利。

其中有一个有趣的发现，以往我都是左右分屏，一边用vscode写代码，另一边看模拟器展示。事实上，开发者工具本身具有终端，因此不必多此一举。

#### 遇到问题
```powershell
(base) PS E:\Desktop\WeChorus> yarn dev:weapp
yarn run v1.22.19
$ npm run build:weapp -- --watch

> WeChorus@1.0.0 build:weapp
> taro build --type weapp --watch

文件名、目录名或卷标语法不正确。
error Command failed with exit code 1.
info Visit https://yarnpkg.com/en/docs/cli/run for documentation about this command.
```

### 解决方法

## 一些工具集成

在开发Taro小程序过程中，需要集成一些工具。下面笔者以一个常见的应用场景予以阐述。

### 头像昵称获取

对于微信小程序，最常用的场景就是头像和昵称获取。微信关于此方面的接口也改变了许多次，从getUserInfo到getUserProfile再到全部废弃。

当今，唯一官方途径就是采用Button来手动获取。

### 上班打卡工具

该应用场景需要实现位置签到功能。需要获取位置和附近地图。事实上，使用<Map>组件可渲染地图，无需刻意调用第三方接口。

## 录音组件合成

在子组件中，使用useEffect的hook监听组件的生成与消亡。

还有其他一些第三方工具，可自行查阅资料，此处不再赘述。
