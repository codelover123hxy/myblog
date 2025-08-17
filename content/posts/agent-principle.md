---
title: "Agent原理"
subtitle: ""
date: 2025-01-18T13:20:39+08:00
lastmod: 2025-01-18T13:20:39+08:00
draft: false
author: "hxy"
authorLink: ""
license: ""
tags: ["源码解析"]
categories: ["科研"]
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

## llm Agent的Tool call原理解析
### 引入
转眼间进入2025年，新年第一篇博客记录一下近期的发现。

笔者在实践中，探索langchain框架可以自动调用工具（tool calling）。
见 [langchain](https://www.aiyin.club/posts/langchain/)
然而，众所周知，LLM是用于文本生成的工具，可以理解成func(input:str) -> str
那么工具究竟是谁在调用呢？如何判断何时调用？

### 回顾
我们先简单回顾一下langchain的agent调用工具的例子。

```python
# # 初始化 ChatZhipuAI
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI

# 定义 calculate 函数
def calculate(expression: str) -> float:
    """
    执行数学运算。

    :param expression: 数学表达式，例如 "3 + 5" 或 "10 / 2"
    :return: 计算结果
    """
    try:
        return eval(expression)  # 使用 eval 执行表达式
    except Exception as e:
        return f"Error: {str(e)}"

# 将函数封装为 Tool
calc_tool = Tool(
    name="calculate",
    func=calculate,
    description="A tool to perform mathematical calculations. Input should be a mathematical expression, e.g., '3 + 5' or '10 / 2'."
)

# 初始化大语言模型
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base="https://api.deepseek.com",
    temperature=0.3,
)

# 定义工具列表
tools = [calc_tool]

# 创建 Agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # 使用 Zero-shot ReAct 代理
    verbose=True  # 打印详细日志
)
# 用户输入
user_input = "2的10次方是多少?"
# 调用 Agent
response = agent.run(user_input)
```

结果

<img src="https://media.tidechoir.cn/image/image-20250118132914266.png">

可以看到，agent自动调用了calculate工具。
然而，究竟调用的过程是怎样的？

### 探索
我们可以在ChatOpenAI库的内部，找到_generate函数
<img src="https://media.tidechoir.cn/image/image-20250118133119039.png">
将messages[0].content打印出来，即可看到大模型真正的prompt。

```python
Answer the following questions as best you can. You have access to the following tools:

calculate: A tool to perform mathematical calculations. Input should be a mathematical expression, e.g., '3 + 5' or '10 / 2'.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [calculate]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: 2的10次方是多少?
Thought:
```

该prompt规定了大模型的回答格式（format）
因此，得到的结果也遵循以下格式：
```
Action: calculate
Action Input: 2 ** 10
Observation: 1024
Thought: I now know the final answer.
Final Answer: 2的10次方是1024。
```

接下来，Langchain框架提取回答信息中的Action、Action Input信息。
将Action的名称与工具列表中的工具名称作对比，对应上即调用该工具，将Action Input传入。

至此，Agent Tool Calling的原理已经完全解析清楚了。有兴趣完全可以自己写一个类似的框架。对于科研来说，框架本身并不是高深的东西，它的意义是简化代码，便于实现研究者目的。
