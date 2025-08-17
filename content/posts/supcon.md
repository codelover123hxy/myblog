---
title: "一些实习的收获与总结"
subtitle: ""
date: 2025-05-30T14:43:34+08:00
lastmod: 2025-05-30T14:43:34+08:00
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

## 一些实习的收获与总结
笔者在一家中厂进行了一个半月的实习，记录一篇博客写一写感受。

进入算法岗，做一做视觉大模型（VLM）的实践，玩玩A100。
由于工作的具体内容需保密，因此本篇博客仅记录个人感受和技术栈本身的梳理。

### 工作主要任务

1. 完成RAG技术的综合调研，详细介绍知识图谱、知识库方案和多模态RAG技术
2. 独立完成RAG、图片检索Demo搭建，学习Streamlit、Gradio的使用。 
3. 对项目图像数据集清洗、分类、增强、标注，微调VLM，测评效果对比
4. 训练Yolov8、Yolov11小模型的效果，测试结果。

### 个人感悟
对于大模型算法岗来说，打标签是实习生经典的任务。同时，想要自己做一个高质量的数据集，确实需要人工标注。

这次有机会接触到A100和H200，公司一般相比高校会有更多的算力资源。

工作内容很看带的导师，有些偏向于做做研究、调研；有些则分配具体任务为主（打标、清洗数据、炼丹）

### 几个重要工作
下面展示几个重要的工作中用到的工程技术。

#### 大模型微调
学习了Llama-factory的使用，这个框架事实上极其简单，配置好yaml即可开始训练。便捷程度堪比Yolo。

```python
export PATH=~/anaconda3/bin:$PATH 
source activate
conda activate your_env
export CUDA_VISIBLE_DEVICES="4,5,6,7" # 选择gpu编号
```
```bash
llamafactory-cli train examples/train_lora/qwen2vl_lora_sft.yaml
```
改成自己的yaml，
Yaml内容根据自己的需求修改，主要是模型名字、保存路径和训练轮次。

合并模型
```bash
llamafactory-cli export examples/merge_lora/qwen2vl_lora_sft.yaml
```

#### SD数据增强

加载pipeline
```python
pipe_img2img = AutoPipelineForImage2Image.from_pretrained(
    "your-path/stable-diffusion-3.5-large",
     torch_dtype=torch.float16
).to("cuda")
```

```python
files = ["img1.png", "img2.png", "img3.png"]     # files是一个图片文件名列表
prompt = "a man is running, 4k"
negative_prompt = "blur face, float object, extra limb"

for i in range(0, 1000):  
    random_file = random.choice(files)
    image_path = os.path.join(image_dir, random_file)
    original = Image.open(image_path).convert("RGB")

    result = pipe_img2img(
        prompt = prompt,
        image = original,
        strength=0.55,       
        guidance_scale=22.0,
        num_inference_steps=40,
        negative_prompt=negative_prompt
    ).images[0]
    result.save(output_path)
```

其中strength控制的是新生成部分的占比，guidance_scale表示prompt遵循程度
num_inference_steps代表生成步数，越大图片质量高，但时间也长。

原图和生成后的图像如下：

原图
![alt text](https://media.tidechoir.cn/image/cat.png)

生成的图
![alt text](https://media.tidechoir.cn/image/cat1.png)

可以看到，两只猫整体布局相同，但颜色、周围布景不同。

### vLLM库的使用
vLLM库是一个快速推理的库，使用非常简单。

```bash
CUDA_VISIBLE_DEVICES=0,1,2 python3 -m vllm.entrypoints.openai.api_server \
    --model /mnt/shared/public_model/llm/InternVL3-78B \
    --served-model-name InternVL3-78B \
    --tensor-parallel-size 2 \
    --trust-remote-code \
    --quantization fp8 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 8192 \
    --port 8699
```

服务启动后，可通过OpenAI规范的API进行调用。

#### 调用方式
利用requests库进行调用
```python
def chat_api_curl(img_path, label):
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
 
    Systems = "你是一个图片分析专家，根据图片描述发生的行为。"
    
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
                        "text": PROMPT,
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
    
    response = requests.post("http://localhost/v1/chat/completions", headers=headers, json=data)
 
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

这是几个重要的工程技术，不难，属于算法岗必备技能。
之后，笔者打算在科研之余去大厂见识一下，进一步提升算法能力。
