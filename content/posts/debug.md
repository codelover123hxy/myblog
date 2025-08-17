---
title: "记一次前端“幽灵”bug的解决"
subtitle: ""
date: 2024-12-04T22:50:21+08:00
lastmod: 2024-12-04T22:50:21+08:00
draft: false
author: "hxy"
authorLink: ""
license: ""
tags: ["经验"]
categories: ["前端debug合集"]
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

# 记一次前端幽灵bug的解决

## 写在前面

笔者在微信小程序开发具备较多的经验，从原生开发到uniapp，以及Taro均有涉猎。

在一个项目业务逻辑中，每次重进小程序将自动登录最近登录过的账号，同时进入登录页面显示历史账号。
然而，近期出现一个奇怪的bug：小程序无法自动登录，历史账号也消失了。

更令人**匪夷所思**的是，笔者在开发者工具和手机上反复测试，并未发现任何bug。这bug如同幽灵一般，随机的出现。
经过广泛测试，事实上，该bug在一部分人的手机上出现，但在另一部分人手机上完全正常。

## 排查过程

由于笔者调试时并未发现任何问题，并且以往也从未出现该bug，竟然有种无从下手的尴尬。

以下为寻找解决方案的经过。

1. **尝试将代码复原至上一个版本 (<span style="color: red;font-size: 30px">×</span>)**

   首先，我将最新的改动还原，试图解决该问题。然而该问题仍然存在，令人费解。

2. **在出问题的手机上启动“开发调试”（<span style="color: green;font-size: 20px">√</span>）**

   尽管程序看起来逻辑完全正确，但按照常理，一定是有报错阻碍了相关内容的呈现。

   在出现bug的手机上启动小程序“开发调试”，找到了“报错”，如图所示。

   <img src="https://media.tidechoir.cn/image/b683f92dcd7f697fc8f35838471fb5e.jpg" style="zoom:30%" align="center" />

### 解决方法：

经过分析报错，定位到一段代码：

```javascript
onLoad() {
	this.accountList = uni.getStorageSync('accountList') || [] // (1)
	if (this.accountList.length) {
        const [arr1, arr2] = this.accountList.reduce((result, item) => {
            item.identity = Number(item.identity)
            // 根据 identity 将对象分配到不同的数组
            result[item.identity - 1].push(item) // identity取值为1：家长 2：教师
            return result
        }, [[], []]);  // 初始化为两个空数组
        this.parentList = arr1
        this.teacherList = arr2
	}
},
```

意味着result[item.identity - 1]为undefined。进一步调试，item.identity也未定义。

而存储storage的代码为：

```javascript
export function saveLoginInfo(identity, name, password) {
	// 从本地存储中获取账号列表
    let accountList = uni.getStorageSync('accountList') || [] 		// (1)
	 // 检查账号是否已经存在
	let accountExists = accountList.some(account => account.name === name)
	uni.setStorageSync("name", name)
	uni.setStorageSync("password", password)
	if (!accountExists) {
	    // 创建当前登录的账号信息对象
	    let newAccount = { identity: identity, name: name, password: password }
	    // 将新账号信息添加到账号列表中
	    accountList.push(newAccount)
	    // 将更新后的账号列表保存回本地存储
	    uni.setStorageSync('accountList', accountList) // (2)
	} else {
	    console.log('账号已存在，未重复添加')
	}
}
```

因此accountList应该呈现如

```json
Array [Object {identity: 1", name:"xxx", password: "xxxxxx"}, ...]
```

但打印调试信息发现，accountList居然出现了信息丢失，形如

```json
Array [Object {name:"xxx", password: "xxxxxx"}, ...]
```

identity属性直接消失了！

罪魁祸首在于存储本地缓存时未将对象数组利用JSON转变成字符串。

### 修改方法

```javascript
// 将(1)修改为：
let accountList = [];
let accountStr = uni.getStorageSync('accountList')
if (accountStr) {
	accountList = JSON.parse(accountStr)
}

// 将(2)修改为：
uni.setStorageSync('accountList', JSON.stringify(accountList));
```

大功告成! 针对使用过的用户，还需删除原来的缓存。因为原来的缓存中直接存了对象数组，无法读取。

将小程序删除后重新进入即可。

### 总结
经过这次“幽灵”bug的排查与修复，我深感前端的代码务必落实规范性，有些写法看似能用，其实存在极大的隐患，而且不易发现。存取storage时，如遇对象/对象数组，使用JSON.stringify()和JSON.parse()这一套，切勿贪图方便，埋下隐患。
另外，不要过分相信模拟器，务必在多台手机（安卓、苹果）上进行广泛测试，使用开发调试工具来排查bug。