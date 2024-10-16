---
title: "前端杂谈"
subtitle: ""
date: 2024-09-16T20:30:59+08:00
lastmod: 2024-09-16T20:30:59+08:00
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

# 前端杂谈（一）

## 前端项目集锦

- ### 原生

叮当葫芦-认知障碍数据分析平台
["认知障碍数据分析平台"](http://124.220.179.33:82/)

- ### Jquery

- ### Vue

#### vue-element-admin
["水果电商后台服务端"](https://management.aiyin.club/)

- ### uniapp

- ### React

["智问领航"](http://47.120.38.169:86/)

#### ant-design-pro

------

## 函数封装思维
###  API接口封装
封装request.js用于ajax请求
利用Promise的特性，封装axios、ajax、uni.request、taro.request等等

#### 示例
```javascript
export const request = ({ url, method, data, headers }) => {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        // 如果是 GET 请求，将 data 转为查询参数
        if (method.toUpperCase() === 'GET' && data) {
            const queryString = Object.keys(data)
                .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(data[key]))
                .join('&');
            url += '?' + queryString;
        }
        
        xhr.open(method, baseURL + url, true);

        // 设置请求头
        if (headers) {
            Object.keys(headers).forEach(key => {
                xhr.setRequestHeader(key, headers[key]);
            });
        }

        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                reject(new Error('Request failed: ' + xhr.status + ' ' + xhr.statusText));
            }
        };

        xhr.onerror = () => {
            reject(new Error('Network error'));
        };

        xhr.send(data ? data : null);
    });
}
```

```javascript
export const request = (options) => {
  // 1. 返回 Promise 对象
  return new Promise((resolve, reject) => {
    uni.request({
      ...options,
      // 响应成功
      success(res) {
        // 状态码 2xx， axios 就是这样设计的
        if (res.statusCode >= 200 && res.statusCode < 300) {
          // 2.1 提取核心数据 res.data
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // 401错误  -> 清理用户信息，跳转到登录页
          // const memberStore = useMemberStore()
          // memberStore.clearProfile()
          uni.navigateTo({ url: '/pages/index/index' })
          reject(res)
		} else {
          // 其他错误 -> 根据后端错误信息轻提示
          uni.showToast({
            icon: 'none',
            title: (res.data).msg || '请求错误',
          })
          reject(res)
        }
	  },
      // 响应失败
      fail(err) {
		console.log(err)
        uni.showToast({
          icon: 'none',
          title: '网络错误，换个网络试试',
        })
        reject(err)
      },
    })
  })
}
```
#### 核心：

使用promise封装请求函数。

```javascript
new promise((resolve, reject) => {if (xxx) resolve(xxx); else reject(xxx)})
```

#### 封装接口
```javascript
// api.js
const api = {
    user: {
        list: '/api/user/list',
        query: '/api/user/query',
        ...
    }
}
    
// user.js
const getDataAPI = () => {
    return request({
        url: api.user.list,
        method: 'GET',
        data
    })
}

// home.jsx
const async getUsers = () => {
  const res = await getUsersAPI()
  if (res.code === 200) {
      ...
  }
}
```

### 自定义组件封装
### Vue
#### 选项式API
```vue
<template>
    <div>...</div>
</template>

<script>
export default {
    name: "MyComponent",
    data() {
        return {

        }
    },
    created() { },
    mounted() { },
    methods: {
        func() { }
    }
}
</script>
```
#### 组合式API
```vue
<template>
    <div>...</div>
</template>

<script setup>
const data = {

}
const func = () => {
    ...
}
</script>
```
### React
```jsx
const MyComponent = (props) => {
    const data = {
        ...
    }
    
    const func = () => {
        ...
    }
    const [data, setDate] = useState({})
	useLoad(()=>{})
    useEffect(()=>{})

    return (
        <div>...</div>
    )
} 
```