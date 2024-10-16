---
title: "后端杂谈（一）"
subtitle: ""
date: 2024-09-17T20:30:52+08:00
lastmod: 2024-09-20T23:20:52+08:00
draft: false
author: ""
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
### 开发规范
1. 使用dto封装类实现数据传输，少用Map。
2. 使用@RequestBody和@RequestParam接收请求参数。
3. 接口类型一般为GET、POST、DELETE。
3. 统一使用{"code": "", "msg": "", data: ""} 的规范返回数据。其中200代表正常，500代表错误。
4. 统一使用全局异常处理，少用try catch，保证代码简洁性。
5. 数据具有关联性时，使用逻辑删除代替物理删除。
6. 统一使用jwt token，从中读取用户信息。防止平行越权漏洞。
7. 加入必要的注释，便于多人合作。
8. 开发者更新后上传jar包至服务器，同时将最新代码commit到github上。
9. 变量名统一小驼峰，类名大驼峰

### 全局异常处理
GlobalExceptionHandler

### SSL的配置
笔者在之前的博客中阐述了nginx部署ssl证书的方式。与此同时，后端也务必加上ssl证书。因为微信小程序等平台校验域名合法性。
与之前稍有不同的是，springboot部署ssl证书要求的是jks格式证书。可采用线上工具将证书合成为jks。
配置过程非常简单，简述如下。
1. application.yaml
```yaml
server:
  port: 8083 # 示例
  ssl:
    enabled: true
    key-store: classpath:ssl/api.xxx.cn.jks
    key-store-password: password
    key-store-type: JKS
```

2. HttpsConfig.java
```java
@Configuration
public class HttpsConfig {

    @Value("${custom.http-port: 8858}")
    private Integer httpPort;

    @Value("${server.port}")
    private Integer port;

    @Bean
    public TomcatServletWebServerFactory servletContainer() {
        // 将http请求转换为https请求
        TomcatServletWebServerFactory tomcat = new TomcatServletWebServerFactory() {
            @Override
            protected void postProcessContext(Context context) {
                SecurityConstraint constraint = new SecurityConstraint();
                // 默认为NONE
                constraint.setUserConstraint("CONFIDENTIAL");
                SecurityCollection collection = new SecurityCollection();
                // 所有的东西都https
                collection.addPattern("/*");
                constraint.addCollection(collection);
                context.addConstraint(constraint);
            }
        };
        tomcat.addAdditionalTomcatConnectors(httpConnector());
        return tomcat;
    }

    /**
     * 强制将所有的http请求转发到https
     *
     * @return httpConnector
     */
    @Bean
    public Connector httpConnector() {
        Connector connector = new Connector("org.apache.coyote.http11.Http11NioProtocol");
        connector.setScheme("http");
        // connector监听的http端口号
        connector.setPort(httpPort);
        connector.setSecure(false);
        // 监听到http的端口号后转向到的https的端口号
        connector.setRedirectPort(port);
        return connector;
    }
}
```
至此，springboot的ssl证书就配置完毕。


### jwt token的配置
为避免平行越权等问题，保证接口安全性，需要使用jwt方式进行鉴权。
此处，笔者通过构建JwtInterceptor类实现jwt拦截器，检测前端请求Headers里是否有token。
```java
public class JwtInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        //如果不是映射到方法直接通过
        String origin = request.getHeader("Origin");
        response.addHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, HEAD");
        response.addHeader("Access-Control-Allow-Headers", "Content-Type, Authorization, token");
        response.addHeader("Access-Control-Allow-Credentials", "true");
        response.addHeader("Access-Control-Max-Age", "3600");
        if (!(handler instanceof HandlerMethod)) {
            return true;
        }
        //从 http 请求头中取出 token
        String token = request.getHeader("token");
        System.out.println("此处测试是否拿到了token：" + token);
        if (token == null) {
            throw new RuntimeException("无 token ，请重新登陆");
        }
        //验证 token
        JwtUtil.checkSign(token);
        //验证通过后， 这里测试取出JWT中存放的数据，获取 token 中的 userId
        String userId = JwtUtil.getUserId(token);
        //获取 token 中的其他数据
        Map<String, Object> info = JwtUtil.getInfo(token);
        info.forEach((k, v) -> System.out.println(k + ":" + v));
        return true;
    }
}
