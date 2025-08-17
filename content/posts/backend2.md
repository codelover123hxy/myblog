---
title: "后端杂谈（二）"
subtitle: ""
date: 2024-09-17T21:30:52+08:00
lastmod: 2024-09-20T23:40:52+08:00
draft: false
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
author: "hxy"
---

## Java开发

上期我们主要讲述了后端springboot开发规范和一些基本配置，现在阐述一些常用技巧。
如发邮件、微信配置等，这些都十分简单但易忘，故集中整理。

### 微信接口集成
调用微信官方api即可。
核心要素为api_key和api_secret，配置在yaml中。

#### accessToken的获取
```java
public static String getAccessToken() throws Exception{
        HttpClient httpClient = new HttpClient();
        String url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=" + appid
                + "&secret=" + secret;
        GetMethod getMethod = new GetMethod(url);
        getMethod.addRequestHeader("accept", "*/*");
        //设置Content-Type，此处根据实际情况确定
        getMethod.addRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        String result = "";
        try {
            int statusCode = httpClient.executeMethod(getMethod);
            if (statusCode == 200) {
                result = getMethod.getResponseBodyAsString();
                JSONObject json = (JSONObject) JSON.parse(result);
                String token = (String) json.get("access_token");
                return token;
            }
            else {
                throw new Exception();
            }
        } catch (Exception e) {
            throw new Exception();
        }
    }
```

#### 微信支付与退款

1. 后端配置接口
```java
// 配置签名等信息
PrivateKey merchantPrivateKey = PemUtil.loadPrivateKey(Files.newInputStream(Paths.get(wxPayAppConfig.getMerchantPrivateKey())));
certificatesManager = CertificatesManager.getInstance();
sign = SecureUtil.sign(SignAlgorithm.SHA256withRSA, merchantPrivateKey.getEncoded(), null);
certificatesManager.putMerchant(wxPayAppConfig.getMchID(), 
        new WechatPay2Credentials(wxPayAppConfig.getMchID(), new PrivateKeySigner(wxPayAppConfig.getMchSerialNo(),
                merchantPrivateKey)), wxPayAppConfig.getApiV3key().getBytes(StandardCharsets.UTF_8));
Verifier verifier = certificatesManager.getVerifier(wxPayAppConfig.getMchID());
WechatPayHttpClientBuilder builder = WechatPayHttpClientBuilder.create()
        .withMerchant(wxPayAppConfig.getMchID(), wxPayAppConfig.getMchSerialNo(), merchantPrivateKey)
        .withValidator(new WechatPay2Validator(verifier));
httpClient = builder.build();

JSONObject requestMap = new JSONObject(); //设置请求体
requestMap.put("mchid", wxPayAppConfig.getMchID());
requestMap.put("appid", wxPayAppConfig.getAppID());

...

HttpPost httpPost = new HttpPost("https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi");
httpPost.addHeader("Accept", "application/json");
httpPost.addHeader("Content-type", "application/json; charset=utf-8");
httpPost.setEntity(new StringEntity(requestMap.toJSONString(), "UTF-8"));
CloseableHttpResponse response = httpClient.execute(httpPost); //发送请求
```

2. 前端发起请求
3. 微信支付成功后反馈

```java
@ResponseBody
@PostMapping("/pay/notify")
public String handleTradeNotify(HttpServletRequest request, HttpServletResponse response) {
    try {
        System.out.println("已支付");
        ServletInputStream inputStream = request.getInputStream();
        BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(inputStream));
        String line;
        String result = "";
        while((line = bufferedReader.readLine()) != null){
            result += line;
        }
        // 通过微信支付通知的返回结果，校验是否支付成功
        JSONObject obj = JSONObject.parseObject(result);
        ...
        //重点：解密支付内容
        AesUtil aesUtil = new AesUtil(secret.getBytes());
        String res = aesUtil.decryptToString(associatedData.getBytes(), nonce.getBytes(), ciphertext);
        JSONObject payInfo = JSONObject.parseObject(res);
        ...
        // 处理数据库逻辑
```
退款与之类似，不再赘述。
微信小程序开发中还有许多需要用到官方接口，如扫二维码、消息推送等，可查阅[微信官方文档](https://developers.weixin.qq.com/miniprogram/dev/api/)。

### 发送邮件与短信
后端开发中，免不了发送短信/邮件，尤其在电商项目中。
#### 发送邮件
Springboot有EmailUtil

1. 配置application.yaml
```yaml
  mail:
    host: smtp.qq.com
    port: 587
    username: qq-number@qq.com
    password: password
    smtpHost: smtp.qq.com
    properties:
      mail:
        smtp:
          auth: true
          starttls:
            enable: true
```

2. 编写EmailUtils类

```java
import jakarta.mail.*;
import jakarta.mail.internet.*; //引入发邮件相关包

public class EmailUtils {
    private String smtpHost; // 邮件服务器地址
    private String sendUserName; // 发件人的用户名
    private String sendUserPass; // 发件人密码
    private MimeMessage mimeMsg; // 邮件对象
    private Multipart mp;// 附件添加的组件

    private void init() {
        // 创建一个密码验证器
        MyAuthenticator authenticator = null;
        authenticator = new MyAuthenticator(sendUserName, sendUserPass);
        // 实例化Properties对象
        Properties props = System.getProperties();
        props.put("mail.smtp.host", smtpHost);
        props.put("mail.smtp.auth", "true"); // 需要身份验证
        props.put("mail.smtp.port", 587);
        props.put("mail.smtp.starttls.enable", "true");
        // 建立会话
        Session session = Session.getDefaultInstance(props, authenticator);
        // 置true可以在控制台（console)上看到发送邮件的过程
        session.setDebug(true);
        // 用session对象来创建并初始化邮件对象
        mimeMsg = new MimeMessage(session);
        // 生成附件组件的实例
        mp = new MimeMultipart();
    }

    ...

    public boolean send() throws Exception {
        mimeMsg.setContent(mp);
        mimeMsg.saveChanges();
        System.out.println("正在发送邮件....");
        solveError();
        Transport.send(mimeMsg);
        System.out.println("发送邮件成功！");
        return true;
    }
}
```

#### 发送短信
1. 到官网注册，例如阿里云等
一般均需要企业实名认证 + 签名审核 + 模版审核。需要耐心等待数天。
2. 找到api或者sdk，编写后端代码。
以阿里云为例：
```java
com.aliyun.dysmsapi20170525.models.SendBatchSmsRequest sendBatchSmsRequest = new com.aliyun.dysmsapi20170525.models.SendBatchSmsRequest()
                .setTemplateCode(templateCode)
                .setTemplateParamJson(templateParamJson)
                .setSignNameJson(signNameJson)
                .setPhoneNumberJson(phoneNumberJson);
        com.aliyun.teautil.models.RuntimeOptions runtime = new com.aliyun.teautil.models.RuntimeOptions();
        try {
            // 复制代码运行请自行打印 API 的返回值
            SendBatchSmsResponse response = client.sendBatchSmsWithOptions(sendBatchSmsRequest, runtime);
            System.out.println(response.getBody().getMessage());
        } catch(...) {
          ...
        }
```
3. 调api查询短信是否发送成功
