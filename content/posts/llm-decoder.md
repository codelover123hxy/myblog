---
title: "llm decoder的研究"
subtitle: ""
date: 2025-01-20T16:00:20+08:00
lastmod: 2025-01-20T16:00:20+08:00
draft: false
author: "hxy"
authorLink: ""
license: ""
tags: ["科研"]
categories: [""]
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

## llm decoder的研究
### 引入

对于大模型来说，常见的是decoder-only transformer架构。因此，研究解码器的原理至关重要。
笔者通过实践，实践了默认解码方法的调用和自己重写解码器。

### 如何调用开源LLM

LLM可分为开源和闭源两种。其中闭源的LLM会提供api，如gpt4等模型。
可使用requests库发送请求并接收信息。部分llm支持openai库

```python
from openai import OpenAI

client = OpenAI(api_key=api_key, base_url=base_url)
# 调用API检索
response = client.chat.completions.create(
  model=model_name,
  messages=[
    {"role": "user", "content": prompt},
  ],
  stream=False
)
# 获取优化后的代码结果
result = response.choices[0].message.content
```
stream=True代表流式输出。反之直接输出最终的文本。

对于开源llm，可使用transformers库来调用

在科研中，尽管开源的llm调用起来十分方便，但也没有那么自由。因此，当我们需要访问llm的logits、attention权重等参数时，需选择开源llm进行研究。

常见的有llama系列（llama2, llama3）、mistral系列等。

```python
# 读取模型
model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16, device_map="auto")
# 读取分词器
tokenizer = AutoTokenizer.from_pretrained(model_path)

prompt = """Your prompt"""

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt},
]

input_ids = tokenizer.apply_chat_template(messages, return_tensors="pt")

# Generate the output using the custom decoder
output_ids = model.generate(input_ids, max_length=1024, do_sample=True, top_k=50)

# do_sample=False意味着贪心解码，反之是按照概率采样。
# top_k指的是采样范围是前k个潜在token。
# max_length是生成的最大长度。

generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
```

其中input_ids是输入文本在词库中的索引列表，如Tensor([[1033, 736, 887, 921]])。
output_ids是模型预测得到文本在词库中的索引列表。
它是一个二维张量，将output_ids[0]用tokenizer.decode函数解析，即可得到最终生成的文本。


### 重写解码过程

尽管本身提供了一些常见的解码策略，如贪心、束搜索等，但如果需要自定义策略，可重写GenerationMixin类来实现
代码如下：

```python
class CustomDecoder(GenerationMixin):
    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def generate(self, input_ids, max_length: int = 100, do_sample: bool = True, top_k: int = 50, **kwargs):
        # Initialize the output sequence with the input_ids
        output_ids = input_ids.clone()

        for i in range(max_length - input_ids.size(1)):
            # Get the logits for the next token
            with torch.no_grad():
                outputs = self.model(output_ids)
                next_token_logits = outputs.logits[:, -1, :]

            # Apply top-k filtering
            if top_k is not None:
                next_token_logits = self.top_k_filter(next_token_logits, top_k)

            # Sample the next token
            if do_sample:
                probs = torch.softmax(next_token_logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
            else:
                next_token = torch.argmax(next_token_logits, dim=-1, keepdim=True)
                
            # Append the next token to the output sequence
            output_ids = torch.cat([output_ids, next_token], dim=-1)

            # Custom action: print the generated token
            generated_token = self.tokenizer.decode(next_token[0], skip_special_tokens=True)

            # Check for end of sequence (optional)
            if next_token.item() == self.tokenizer.eos_token_id:
                break

        return output_ids

    def top_k_filter(self, logits, top_k):
        values, top_k_indices = torch.topk(logits, top_k)
        min_values = values[:, -1].unsqueeze(-1)
        return torch.where(logits < min_values, torch.ones_like(logits) * -float('inf'), logits)
```
核心在于
```python
outputs = self.model(output_ids)
next_token_logits = outputs.logits[:, -1, :]
```
然后使用自定义解码方式选择token。每一次仅解码新的一个token，解码完成后将这个token拼接到尾部，下一次输入给模型，获取新的logits。

调用上只需要改为将model.generate改为
```python
custom_decoder = CustomDecoder(model, tokenizer)
output_ids = custom_decoder.generate(input_ids, max_length=1024, do_sample=True, top_k=50)
```
非常简单。
