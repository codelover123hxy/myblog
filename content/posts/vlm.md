---
title: "多模态大模型与Stable Diffusion"
subtitle: ""
date: 2025-04-30T21:28:02+08:00
lastmod: 2025-04-30T21:28:02+08:00
draft: true
author: "hxy"
authorLink: ""
license: ""
tags: [""]
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

## 多模态大模型与Stable Diffusion
近日，笔者接触了VLM与SD，还是挺有趣的，记录一篇博客解析其中的Prompt技巧。

### VLLM调用
VLLM是一款快速调用LLM与VLM的框架，仅需启动如下命令，即可实现高效推理、API自动封装
```powershell
CUDA_VISIBLE_DEVICES=0,1 python3 -m vllm.entrypoints.openai.api_server \
    --model {your_path}/InternVL3-78B \
    --served-model-name InternVL3-78B \
    --tensor-parallel-size 2 \
    --trust-remote-code \
    --quantization fp8 \
    --gpu-memory-utilization 0.9 \
    --max-model-len {max_model_len} \
    --port {port}
```

推理时的API风格与OpenAI一致。以下为请求函数：
```python
def chat_api_curl(img_path, prompt):
    """
    请求openai的api
    """
    # 加载本地图片
    with open(img_path,'rb') as f:
        image_str = base64.b64encode(f.read()).decode('ascii')

    # 请确保将以下变量替换为您的实际API密钥
    openai_api_key = 'EMPTY'
 
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
 
    Systems = "你是一个图片分析专家。"
    
    data = {
        "model": "qwen2.5_vl-72b",
        "messages": [
            {
                "role": "system",
                "content": Systems,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/webp;base64,%s" % (image_str),
                        },
                    },
                ],
            },
        ]
    }
    
    response = requests.post("http://{ip}:{port}/v1/chat/completions", headers=headers, json=data)
 
    # 检查响应是否成功
    if response.status_code == 200:
        # 解析响应数据
        response_data = response.json()
        # 获取choices列表中的第一个元素的message字典的content值
        content = response_data['choices'][0]['message']['content']
        return content
    else:
        print("请求失败，状态码：", response.status_code)
        print("响应内容：", response.text)
```
可以看到，API的设计符合日常规范，十分清晰。对于VLM来说，我们需读取图片并转为Base64码传入模型，模型分析并给出回答。其他调用过程与LLM一致。
```python
image_str = base64.b64encode(f.read()).decode('ascii')
```


### Stable Diffusion
Stable Diffusion(SD)模型是一种文生图模型。

#### 文生图
```python
pipe = StableDiffusion3Pipeline.from_pretrained(
    "your-path/stable-diffusion-3.5-large",
    torch_dtype=torch.float16,
    variant="fp16"
).to("cuda")
prompt = "Please desribe a railway station."
image = pipe(prompt).images[0]
image.save("station.png")
```

#### 文+图->图
SD一大牛逼之处，能够基于已有图片结合文字描述，生成新的图片。
```python
pipe_img2img = AutoPipelineForImage2Image.from_pretrained(
    "your-path/stable-diffusion-3.5-large",
    torch_dtype=torch.float16
).to("cuda")

original = Image.open(image_path).convert("RGB")
result = pipe_img2img(
    prompt = prompt,
    image = original,
    strength=0.5,
    guidance_scale=16.0,
    num_inference_steps=40,
    negative_prompt=negative_prompt
).images[0]
result.save(f"./output_imgs/fake_imgs/{folder}/image_{i}.png")
```
其中strength代表生成的空间有多大，例如0.1代表0.1的部分自由生成，适合局部调整；0.5以上意味着一半重绘，仅保留整体布局。

guidance_scale代表prompt的强度，该值越大prompt作用力越大。\
num_inference_steps是生成步数，越大图像越清晰。\
prompt与negative_prompt是正反提示词。

实验证明，反面提示词效果更明显。

#### 优势
这种img2img的方法非常适合用于图像数据增强，能够有助于训练或微调VLM.
