---
title: "Langgraph"
date: 2024-09-21T12:19:47+08:00
draft: true
author: hxy
categories: ["科研"]
tags: ["源码解析"]
---

## Langgraph
### 背景引入
RAG（检索增强生成）是目前LLM应用
为了实现多智能体（multi-agent），采用langgraph框架。

![alt text](../image-3.png)

### 参考博客
["彻底搞懂LangGraph"](https://developer.volcengine.com/articles/7370376546193768458)

#### 遇到的错误
1.找不到langgraph包
```python
python langgraph.py 
Traceback (most recent call last):
  File "/newdata/intern/hxy/Langchain-Chatchat-Old/myagent/langgraph.py", line 1, in <module>
    from langgraph.graph import StateGraph, END
  File "/newdata/intern/hxy/Langchain-Chatchat-Old/myagent/langgraph.py", line 1, in <module>
    from langgraph.graph import StateGraph, END
ModuleNotFoundError: No module named 'langgraph.graph'; 'langgraph' is not a package
```
##### 解决方法
一开始百思不得其解，重新装包，改conda环境均无法解决。
后来发现是python文件的文件名和包名撞了。

### 代码精析
LangGraph的核心概念把Agent工作流以图的方式建模。
1. 状态(State)
2. 节点(Nodes)
3. 边(Edges)

#### 状态图

#### 消息图

#### 状态


```python




```
