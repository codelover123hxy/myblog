---
title: "浅析大模型思维链方法"
date: 2024-11-03T12:19:00+08:00
draft: false
author: "hxy"
categories: ["科研"]
tags: ["经验贴"]
---
## 大模型Prompt——思维链

### 初探思维链

思维链方法由google大脑研究院（现跳槽至OpenAI）的Jason Wei大佬在

首篇论文《**Chain-of-Thought Prompting Elicits Reasoning in Large Language Models**》中提出。

#### 思维链的形式

给定Prompt，包含三元组 **<input, chain of thought, output>**

举例：

![image-20241101141119393](https://media.tidechoir.cn/image/image-20241101141119393.png)

#### 思维链的妙处

- COT使得模型将多步骤问题解构成直接的步骤，意味着附加计算能够被分配到需要更多推理步骤的问题。
- COT对模型的表现提供了可解释的窗口，表明它如何到达具体的答案，并且提供debug推理错误的机会。
- COT推理能够被用于数学文字问题、常识推理和表征计算，并有潜力应用（原则上）到人们能通过语言解决的任何问题。

#### 思维链的效果

在**数学推理、常识推理、象征推理**三大领域运用数据集予以验证。

#### 错误的思维链分析

- 计算错误
- 象征映射错误
- 少步骤错误

#### 思维链存在的局限性

- 尽管思维链模仿了人类推理过程的步骤，这并没有回答神经网络是否真的在推理，留作开放性讨论。
- 尽管在少样本环境下，手动将思维链条增加到示例中的成本很低，但这种标注成本在微调时可能是不可承受的。
- 思维路径并没有保证是正确的，这可能导致生成正确或错误的答案；提高语言模型生成事实性内容的准确性是未来研究的一个方向。
- 最后，思维链条推理的涌现只有在大型模型中才会出现，这使得其在实际应用中成本较高；进一步的研究可以探索如何在小型模型中引导出推理能力。

### 拓展与改进

### 1. 自动思维链 AutoCoT

在思维链引出之后，**李沐老师**团队发表了《**AUTOMATIC CHAIN OF THOUGHT PROMPTING** **IN LARGE LANGUAGE MODELS**》。

思维链的两种范例：

- 在提问之前给出简单的prompt 如“让我们一步一步地思考”   —— **Zero-Shot-CoT**
- 使用一些人工的案例，提供问题解构和推理链从而得到答案。—— **Manual-CoT**

其中第一种方法能够减轻人工的工作量，但生成的思维链常常包含错误。

但第二种方法很费人力，因为对于不同类型的任务（数学推理、常识推理等）都需要人工标注思维链。

因此论文提出一种新的自动COT提示词范式——**AutoCoT**。旨在自动化构建例子包含问题和推理链。具体地，Auto-CoT利用LLM的“让我们一步步思考“的提示词为每一个样例逐个生成推理链。

#### 挑战

给定数据集中的一个测试问题，检索语义近似的问题并加入Zero-Shot-CoT来生成推理链将会失败。

我们的分析显示关键在于**样例问题的多样性**。因此，我们的**AutoCoT**方法通过两步：

- 将给定数据集分成几个簇
- 从每个簇中选取一个有代表性的问题，使用简单的通过启发式方法，使用零样本CoT生成推理链。

#### 两种方法：

- **Retrieval-Q-CoT**

  使用sentence-BERT将问题编码，使用余弦相似度检索前k个。

- **Random-Q-CoT**

  随机选取k个样本。

实验证明，Random-Q-CoT反而效果好。原因在于思维链由Zero-Shot-CoT生成，错误经常在同一个簇中发生。

<p align="center">
  <img src="https://media.tidechoir.cn/image/image-20241101225216249.png">
</p>

#### OverReview

![image-20241101225620537](https://media.tidechoir.cn/image/image-20241101225620537.png)

#### 方法概述：

- **问题聚类**

  先嵌入向量，然后用k-means聚类。

- **示例取样**

  为每个簇生成一个示例$d^{(i)}$,  并遍历问题列表，直到符合挑选法则。

  通过$[Q: q_j^{(i)}. A:[P]]$的提示词生成思维链。最终对第i个簇给出$[Q: q_j^{(i)}. A: r_j^{(i)} \dot a_j^{(i)}]$

  挑选法则：如果$d^{(i)}$拥有问题$q_j^{(i)}$，不到60个token并且对应的推理$r_j^{(i)}$不到5步。

### 2. 自协调思维链

在AutoCoT的基础上，来自新加坡的研究者对其进一步改进，提出了自调节思维链提示词方法《**Self-Harmonized Chain of Thought**》。

将多样化的解决路径合并成统一且有效的解决模式。

#### 论文贡献

- 提出**ECHO**方法，通过统一化多样性提升示例质量
- 设计了可迭代的统一化提示词框架，通过减少示例的变化使得在多种任务重普遍有效。
- 扩展实验表明我们的方法通过减少多样性，在**算术、常识、象征推理**中均得到有竞争力的结果。

#### Overview

![image-20241102123408403](https://media.tidechoir.cn/image/image-20241102123408403.png)

#### 模型步骤

1. 问题聚类
2. 示例采样
3. 示例统一

前两步基本和AutoCoT一致，第三步为论文贡献。

- **示例统一**

  连续迭代T次，对于在D中的每个示例$d^{(i)}$，使用余下的示例生成提示词P，并使用少样本学习生成新的推理过程$r_{new}^{(i)}$，实现示例更新。最后取D中前m个元素。

  每个重新生成的推理过程逐渐与样例中的推理过程对其。通过连续的迭代，此过程达到融合，在所有推理过程之间有统一的模式。

#### 局限性

1. 大模型推理开销大，因为反复迭代。
2. 有可能过拟合。
3. 假设数据集具有相似性。但实际上有可能并不想关或具有错综复杂的关系。

### 总结

从提出CoT到AutoCoT以及Self-Harmonized CoT，思维链不断演进。

一开始只是Manual思维链，后来依靠聚类思想和Zero-Shot思维链，完成了自动构建思维链的方法。即对数据集中的问题聚类，为每一类有代表的问题生成示例。

Self-Harmonized CoT方法进一步使用其他聚类中的示例来优化Zero-Shot生成的推理过程。

AutoCoT和Self-Harmonized CoT在多样性方面各自提出了不同的见解。前者认为多样性有利于减少Zero-Shot中的生成错误，但后者更注重一致性。

### 术语&生词积累

<table border="0" width="100%">   
    <tr>     
        <td width="50%" valign="top">  
            paradigm n. 范式 <br>
            exemplar n. 范例<br>
            leverage v. 利用 n. 影响力；杠杆<br>
            eliminate v. 减少<br>
            mitigate v. 减轻<br>
            elicit v.引起，引出<br>
            in-context learning(ICL) 语境学习<br>
            rationale n. 根本原因<br>
            empirical adj. 经验主义的<br>
            underscore v. 加下划线；强调<br>
            via v. 通过<br>
            coherent adj. 连贯的；有条理的<br>
            few-shot 少样本的<br>
            类似有zero-shot、one-shot<br>
            linguistic adj. 语言的<br>
            aforementioned adj. 前面提及的<br>
            disparity n. 差距；差异<br>
            hypothesis n. 假设；假说<br>
            inferior adj. 较差的 <b>反义词</b>prior<br>
            ubiquitous adj. 无处不在的<br>
            perturbation n. 扰乱<br>
            impede v. 妨碍<br>
            pervasive adj. 普遍的<br>
        </td>     
        <td width="50%" valign="top">  
            annotate v. 注解   annotator n.注解者<br>
            emulate v. 仿真；模仿<br>
            surmount v. 克服<br>
            emergence n. 涌现<br>
            orthogonal adj. 正交的<br>
            concatenate v. 连接 （缩写为concat）<br>
            OOD(out-of-domain) 出域<br>
            synthetic adj. 合成的<br>
            syntax n. 语法   semantics n. 语义<br>
            task-agnostic n. 可在多个任务上运行<br>
            hinge on 取决于<br>
            nontrivial adj. 非平凡的；不容易的    trivial adj. 微不足道的<br> 
            decent adj.适当的<br>
            heuristics n. 启发式<br>
            induce v. 诱导<br>
            fluctuation n. 波动<br>
            sidelining v. 使靠边<br>
            elevate v. 提升<br>
            compromise v. 妥协<br>
            undermining v. 逐渐削弱<br>
            distort v.扭曲；曲解<br>
            quagmire n. 泥潭<br>
            tweak v.& n. 拧<br>
        </td>   
    </tr> 
</table>