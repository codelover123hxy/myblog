---
title: "部署技巧——Docker"

date: 2024-09-07T12:19:47+08:00
draft: true

author: "hxy"
---
# 部署技巧——Docker

## 写在前面

在运维过程中，有时需要快速部署前后端服务。然而每次从mysql的安装、迁移，到前后端环境的配置，十分费时。Docker正是用来简化部署流程的一大工具。我们将服务打包成docker镜像，之后只需一条命令即可运行。

## dockerfile

```dockerfile
# 使用 OpenJDK 作为基础镜像
FROM openjdk:17-jdk-alpine

# 将工作目录设置为 /app
WORKDIR /app

# 复制项目的 jar 文件到容器中
COPY target/your-app-name.jar /app/your-app-name.jar

# 暴露应用的端口（通常为8080）
EXPOSE 8080

# 运行 Spring Boot 应用
ENTRYPOINT ["java", "-jar", "/app/your-app-name.jar"]
```

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:5.7  # 使用 MySQL 5.7 镜像
    container_name: my-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydatabase
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - ./mysql-data:/var/lib/mysql  # 持久化 MySQL 数据
    ports:
      - "3306:3306"

  springboot:
    build: .
    container_name: springboot-app
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/mydatabase
      SPRING_DATASOURCE_USERNAME: user
      SPRING_DATASOURCE_PASSWORD: password
    ports:
      - "8080:8080"
    depends_on:
      - mysql  # 确保 MySQL 服务先启动
```
