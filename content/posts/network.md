---
title: "Networkx库绘制绚丽的网络图"
subtitle: ""
date: 2024-09-22T01:08:11+08:00
lastmod: 2024-09-22T01:08:11+08:00
draft: false
author: "hxy"
authorLink: ""
license: ""
tags: ["技巧"]
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

### networkx库
在科研中，有时需要绘制网络图。python中常用的为networkx库。
下面笔者通过简短的代码予以展示。
首先对数据进行预处理，获得偏相关系数矩阵。

#### 数据预处理
```python
import networkx as nx
from sklearn.covariance import GraphicalLasso
import matplotlib.pyplot as plt
import pandas as pd

def normalize(lst):
    min_val = min(lst)
    max_val = max(lst)
    # 如果最大值和最小值相等，避免除以零
    if max_val == min_val:
        return [0 for _ in lst]
    return [5 * (x - min_val) / (max_val - min_val) for x in lst]

X = pd.read_csv('data.csv')
# 假设 X 是数据矩阵
model = GraphicalLasso(alpha=0.1)  # alpha 控制正则化的强度
model.fit(X)
# 获取偏相关矩阵
partial_corr_matrix = model.precision_
```
#### 利用networkx绘制网络图
```python
G = nx.DiGraph()
columns = [column for column in X.columns]
columns[1] = "Family insecure"
G.add_nodes_from(columns)
edge_widths = []
edges = []
for i in range(0, len(columns)):
    for j in range(0, len(columns)):
        partial_corr_matrix_value = partial_corr_matrix[i][j]
        if partial_corr_matrix_value > 0 and i != j:
            edge_widths.append(partial_corr_matrix_value)
            edges.append((columns[i], columns[j]))

normalized_widths = normalize(edge_widths) # 归一化
G.add_edges_from(edges)
# 绘制图形，width 参数控制边的粗细
pos = nx.spring_layout(G)  # 生成布局
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=1500,
        edge_color='#6DB5FA', width=normalized_widths, node_shape='o', linewidths=2)
plt.show()
```
核心代码为
```python
G = nx.DiGraph()
G.add_nodes_from(columns)
G.add_edges_from(edges)
nx.draw(G, ...)
```

#### 效果展示
到此，一个漂亮的网络图就画好了，展示如下：![alt text](../image-5.png)
