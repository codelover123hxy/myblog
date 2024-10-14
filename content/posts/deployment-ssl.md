---
title: "部署技巧——ssl证书自动更新"
date: 2024-09-22T13:30:00+08:00
draft: false
author: hxy
categories: ["部署技巧"]
tags: ["经验"]
---

## ssl证书自动部署教程
ssl证书有多种渠道获取，如阿里云、腾讯云等。但费用很贵。
ohttps支持免费泛域名证书。
可支持多种自动部署方式。其中API方式较为灵活。仅需调用api可获取证书中的文本信息。

笔者采用nodejs + axios + crontab方式部署

### 导包并封装函数
```javascript
const CryptoJS = require('crypto-js');
const axios = require('axios');
const fs = require('fs');

// 封装request请求
const request = (url) => {
    return axios.get(url)
        .then(response => {
            console.log(response.data);
            return response.data;
        })
        .catch(error => {
            console.error('Error: ', error);
            throw error;  // 抛出错误以便外部捕获
        });
}

// 写入文件
function writeFile(filePath, data) {
    fs.writeFile(filePath, data, (err) => {
        if (err) {
            return console.error(`Error writing to file: ${err.message}`);
        }
        console.log('File has been saved.');
    });
}
```

### 配置参数
```javascript
// 用以获取传入字符串的32位小写MD5哈希值
function md5(string) {
    // 创建一个MD5哈希对象
    return CryptoJS.MD5(string).toString(CryptoJS.enc.Hex);
}
// 部署节点Id
const apiId = "your-api-id"
// API接口密钥
const apiKey = "your-api-key"
// 当前ms时间戳
const timestamp = new Date().getTime()
// 目标证书ID
const certificate_dict = {
    '*.familystudy.cn': {
        certId: 'your-cert-id',
        keyFilePath: '/etc/nginx/cert/aiyin.club.key',
        pemFilePath: '/etc/nginx/cert/aiyin.club.pem'
    }
}
const certificateId = certificate_dict['*.aiyin.club']['certId']
// 用于请求的参数列表
const params = [`apiId=${apiId}`, `timestamp=${timestamp}`, `certificateId=${certificateId}`]
// 用于签名的参数列表：用于请求的参数列表 + API接口密钥
const paramsForSign = [...params, `apiKey=${apiKey}`]
// 用于签名的参数列表使用字母序进行排序
paramsForSign.sort()
// 用于签名的参数列表使用"&"号进行拼接成用以签名的字符串
const stringForSign = paramsForSign.join('&')
// 以上字符串的32位小写MD5哈希值即为参数签名
const sign = md5(stringForSign) 
// 接口最终请求地址
```
### 开始部署
```javascript
async function deployCert(keyFilePath, pemFilePath) {
    const res = await request(url)
    certKey = res.payload.certKey
    fullChainCerts = res.payload.fullChainCerts
    // 文件路径
    writeFile(keyFilePath, certKey)
    writeFile(pemFilePath, fullChainCerts)
}

// 注意最终请求的参数中不包含apiKey
const url = `https://ohttps.com/api/open/getCertificate?sign=${sign}&${params.join("&")}`
console.log(url)

// 请求并上传证书
for (key in certificate_dict) {
    console.log(key)
    const keyFilePath = certificate_dict[key]['keyFilePath']
    const pemFilePath = certificate_dict[key]['pemFilePath']
    deployCert(keyFilePath, pemFilePath)
    console.log(`${key}证书部署成功`)
}
```
除此之外，也可使用python爬虫、java后端调用等多种方式，非常灵活。大家可以选择自己喜欢的方式进行尝试。

### 定期更新
解决了部署问题，还需要设置函数的定期执行。
```powershell
crontab -e
# 输入代码
0 0 */15 * * /home/hxy/cert_deploy/deploy.sh
```
0 0 */15 * * 是一个 cron 表达式，表示每15天执行一次。

#### 拓展 cron表达式
```markdown
* * * * *
┬ ┬ ┬ ┬ ┬
│ │ │ │ │
│ │ │ │ └──── 星期几 (0 - 7) (0 或 7 代表星期日)
│ │ │ └────── 月份 (1 - 12)
│ │ └──────── 月份中的天数 (1 - 31)
│ └────────── 小时 (0 - 23)
└──────────── 分钟 (0 - 59)
```

到此，一个规范的部署流程完成了。
