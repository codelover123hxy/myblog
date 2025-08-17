---
title: "Langgraph"
date: 2024-12-31T12:19:47+08:00
draft: true
author: hxy
categories: ["科研"]
tags: ["源码解析"]
---

## Langgraph
### 背景引入
多智能体（multi-agent）技术是当前LLM十分热门的技术，目前有多种实现框架，如Langgraph、Crewai、AutoGen等。此处，笔者采用著名的langgraph框架。Langgraph框架是一个基于LangChain构建的扩展库,主要用于构建有状态和多角色的Agents应用。

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
#### 解决方法
一开始百思不得其解，重新装包，改conda环境均无法解决。
后来发现是python文件的文件名和包名撞了。

### 代码精析
LangGraph的核心概念把Agent工作流以图的方式建模。
1. 状态(State)
2. 节点(Nodes)
3. 边(Edges)

事实上，langgraph的使用非常简单。Nodes对应的是agent。Edges对应的是agent之间的协同顺序。

下面，笔者用multi-agent模拟一场辩论赛。

首先，定义agent所使用的大模型。我们利用ChatOpenAI库，可方便地调用gpt、deepseek等模型。
```python
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=DEEPSEEK_API_KEY,
    openai_api_base="https://api.deepseek.com",
    temperature=0.3,
)
"""
必要时，可以自定义一个'ChatOpenAI',继承类BaseChatModel，重写方法。
"""
```

接下来，定义system prompt
```
GEN_SYS_MSG = """你是辩论赛的正方。你需要不断收集和正方观点相关的论据，完成辩论。每次发言控制在200字以内。可针对对方的发言进行驳斥。"""
REFLECTION_SYS_MSG = """你是辩论赛的反方。你需要不断收集和反方观点相关的论据，完成辩论。每次发言控制在200字以内。可针对对方的发言进行驳斥。"""

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            GEN_SYS_MSG,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            REFLECTION_SYS_MSG,
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

generator = generation_prompt | llm  # llm can be same or different
reflector = reflection_prompt | llm
```

定义状态、节点、边
```python
class State(TypedDict):
    messages: Annotated[list, add_messages]

def generation_node(state: State) -> State:
    return {"messages": [generator.invoke(state["messages"])]}


def reflection_node(state: State) -> State:
    # Other messages we need to adjust
    cls_map = {"ai": HumanMessage, "human": AIMessage}
    # First message is the original user request. We hold it the same for all nodes
    translated = [state["messages"][0]] + [
        cls_map[msg.type](content=msg.content) for msg in state["messages"][1:]
    ]
    res = reflector.invoke(translated)
    # We treat the output of this as human feedback for the generator
    return {"messages": [HumanMessage(content=res.content)]}

builder = StateGraph(State)
builder.add_node("generate", generation_node)
builder.add_node("reflect", reflection_node)
builder.add_edge(START, "generate")


def should_continue(state: State) -> Literal["reflect", END]:  # type: ignore
    if len(state["messages"]) > 4:
        # End after 2 iterations
        return END
    return "reflect"

builder.add_conditional_edges("generate", should_continue)
builder.add_edge("reflect", "generate")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}

debate_content = "xxx题目"
debate_question = f"""{debate_content}利大于弊还是弊大于利。正方： 利大于弊；反方：弊大于利。"""

request = HumanMessage(content=f"辩题：{debate_question}")
for event in graph.stream({"messages": [request]}, config):
    print(event, end="")
    print("--------------------------------")
```
除此之外，还可以自己定义逻辑，实现多个agent进行自由交互。比如，增加评委功能，根据整个辩论中双方的论点进行点评，并给出胜利者。

其实，多智能体的应用并不困难，Langgraph它作为一种框架，根本目的还是为了简化代码，便于实现研究者的意图。
其功能也可以手写实现。