---
title: "Langchain-chatchat"
date: 2024-09-20T12:19:47+08:00
draft: false
author: hxy
categories: ["科研"]
tags: ["源码解析"]
---

## 部署
按照read-me.md进行配置
1. 需要git clone huggingface库到本地/自己服务器
2. 安装llama_index注意细节
```powershell
pip install llama_index==0.41.0
# 不要错误地写成pip install llama-index!
```

3. clone前运行命令
```powershell
source /etc/profile.d/clash.sh
proxy_on # 开启clash服务
```
也可在autodl上开启镜像

## 源码技术栈
### webui streamlit
```python
dialogue_mode = st.selectbox(
    "请选择对话模式：",
    dialogue_modes,
    index=index,
    on_change=on_mode_change,
    key="dialogue_mode",
)
```
### asyncio
asyncio是python协程库。
所谓「异步 IO」，就是你发起一个 IO 操作，却不用等它结束，你可以继续做其他事情，当它结束时，你会得到通知。

#### 示例
```python
async def chat():
    async def chat_iterator():
        ...
        task = asyncio.create_task(wrap_done(
            chain.acall({"input": query}),
            callback.done),
        )
        async for token in callback.iter():
            yield ...
        await task
    return EventSourceResponse(chat_iterator())
```

### fastapi前后端交互
#### 前端发送请求
```python
def chat_chat(
            self,
            query: str,
            conversation_id: str = None,
            history_len: int = -1,
            history: List[Dict] = [],
            stream: bool = True,
            model: str = LLM_MODELS[0],
            temperature: float = TEMPERATURE,
            max_tokens: int = None,
            prompt_name: str = "default",
            embedding_model: str = "None",
            **kwargs,
    ):
        '''
        对应api.py/chat/chat接口
        '''
        data = {
            "query": query,
            "conversation_id": conversation_id,
            "history_len": history_len,
            "history": history,
            "stream": stream,
            "model_name": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "prompt_name": prompt_name,
            "embedding_model": embedding_model
        }

        response = self.post("/chat/chat", json=data, stream=True, **kwargs)
        return self._httpx_stream2generator(response, as_json=True)
```

#### xxxxxxxxxx ​​​​python
```python
app.post("/chat/chat",
             tags=["Chat"],
             summary="与llm模型对话(通过LLMChain)",
             )(chat) # 括号内为对应的函数

app.post("/chat/search_engine_chat",
        tags=["Chat"],
        summary="与搜索引擎对话",
    )(search_engine_chat)

app.post("/chat/feedback",
        tags=["Chat"],
        summary="返回llm模型对话评分",
    )(chat_feedback)
```

#### 封装返回类
```python
class BaseResponse(BaseModel):
    code: int = pydantic.Field(200, description="API status code")
    msg: str = pydantic.Field("success", description="API status message")
    data: Any = pydantic.Field(None, description="API data")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }

class ListResponse(BaseResponse):
    data: List[str] = pydantic.Field(..., description="List of names")

    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": ["doc1.docx", "doc2.pdf", "doc3.txt"],
            }
        }
```
事实上，看懂这些代码后，自己完全可以独立写一个langchain-chatchat。

### agent实战
langchain框架提供了一种很好的方法，从而使大模型能够调用agent工具。
步骤如下：
#### 编写函数
```python
# search_internet.py
def search_result2docs(search_results):
    docs = []
    for result in search_results:
        doc = Document(page_content=result["snippet"] if "snippet" in result.keys() else "",
                       metadata={"source": result["link"] if "link" in result.keys() else "",
                                 "filename": result["title"] if "title" in result.keys() else ""})
        docs.append(doc)
    return docs

def search_internet(query: str):
    search = DuckDuckGoSearchAPIWrapper()
    results = search.results(query, 10)
    docs = search_result2docs(results)
    context = "\n".join([doc.page_content for doc in docs])
    return context

class SearchInternetInput(BaseModel):
    location: str = Field(description="Query for Internet search")
```

#### 设置prompt模版
```python
agent_prompt_templates = {
    "default": 'Answer the following questions as best you can. If it is in order, you can use some tools appropriately. '
            'You have access to the following tools:\n\n'
            '{tools}\n\n'
            'Use the following format:\n'
            'Question: the input question you must answer1\n'
            'Thought: you should always think about what to do and what tools to use.\n'
            'Action: the action to take, should be one of [{tool_names}]\n'
            'Action Input: the input to the action\n'
            'Observation: the result of the action\n'
            '... (this Thought/Action/Action Input/Observation can be repeated zero or more times)\n'
            'Thought: I now know the final answer\n'
            'Final Answer: the final answer to the original input question\n'
            'Begin!\n\n'
            'history: {history}\n\n'
            'Question: {input}\n\n'
            'Thought: {agent_scratchpad}\n'
}
```

#### 编写工具
```python
## 请注意，如果你是为了使用AgentLM，在这里，你应该使用英文版本。
tools = [
    Tool.from_function(
        func=search_internet,
        name="search_internet",
        description="Use this tool to use duckduckgo search engine to search the internet",
        args_schema=SearchInternetInput,
    ),
    Tool.from_function(
        func=fetch_pages,
        name="fetch_pages",
        description="Use this tool to fetch web source code",
        args_schema=FetchPagesInput,
    )
]

tool_names = [tool.name for tool in tools]
```

#### 初始化模型并调用工具
```python
# 初始化ChatOpenAI模型，指定模型名称和API key
llm = ChatOpenAI(
    model="deepseek-coder",
    api_key="your_deepseek_api_key",
    base_url="https://api.deepseek.com/beta"
)

agent_prompt_template = agent_prompt_templates['default']

prompt_template_agent = CustomPromptTemplate(
    template=agent_prompt_template,
    tools=tools,
    input_variables=["input", "intermediate_steps", "history"]
)

output_parser = CustomOutputParser()
llm_chain = LLMChain(llm=llm, prompt=prompt_template_agent)

agent = LLMSingleActionAgent(
                llm_chain=llm_chain,
                output_parser=output_parser,
                stop=["\nObservation:", "Observation"],
                allowed_tools=tool_names,
            )

agent_executor = AgentExecutor.from_agent_and_tools(agent=agent,
                                                    tools=tools,
                                                    verbose=True)

query = "写一段pytorch代码，实现transformer。请结合搜索结果。"
result = agent_executor.invoke({"input": query, "history": []})
print(result['output'])
```

#### 运行结果
![alt text](../image-2.png)
