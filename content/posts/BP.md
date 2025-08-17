---
title: "机器学习——numpy手搓神经网络"
subtitle: ""
date: 2025-02-11T13:52:04+08:00
lastmod: 2025-02-11T13:52:04+08:00
draft: false
author: "hxy"
authorLink: ""
license: ""
tags: ["机器学习"]
categories: ["代码技巧"]
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

## 机器学习——numpy手搓神经网络

### 引言
笔者近期给数学系学生讲授机器学习课程。讲解BP神经网络的反向传播、梯度下降等操作时，较难理解。
因此，写一篇博客记录一下numpy手搓神经网络的过程。

### BP神经网络
<p align="center">
  <img src="https://media.tidechoir.cn/image/image-20250211132719973.png">
</p>

### 手搓实现
#### 导包
首先导入numpy库和画图的matplotlib库。只需要这两个！
```python
import numpy as np
import matplotlib.pyplot as plt
```

#### 定义激活函数及其导数
```python
# 设置随机种子
np.random.seed(42)

class ReLU:
    def __init__(self):
        pass

    def __call__(self, x):
        self.original_x = x
        return np.maximum(0, x)

    def derivative(self):
        return np.where(self.original_x > 0, 1, 0)

class Sigmoid:
    def __init__(self):
        pass

    def __call__(self, x):
        self.original_x = x
        return 1 / (1 + np.exp(-x))

    def derivative(self):
        x = self.original_x
        return x * (1 - x)
```

对应的公式
$$
ReLU(x) = max(0, x) \\ 
sigmoid(x) = \frac{1}{1 + e^{-x}}
$$

#### 画图函数
```python
def draw(X, y, pred):
    plt.figure()
    plt.plot(X, y, 'o', label='True')
    plt.plot(X, pred, '-', label='Pred')
    plt.legend()
    plt.show()
```

#### 定义Adam优化器
```python
class AdamOptimizer:
    def __init__(self, params, lr=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8):
        self.params = params  # 需要优化的参数
        self.lr = lr  # 学习率
        self.beta1 = beta1  # 一阶矩衰减率
        self.beta2 = beta2  # 二阶矩衰减率
        self.epsilon = epsilon  # 数值稳定性常数
        self.m = [np.zeros_like(p) for p in params]  # 一阶矩
        self.v = [np.zeros_like(p) for p in params]  # 二阶矩
        self.t = 0  # 时间步

    def step(self, grads):
        self.t += 1
        for i, (param, grad) in enumerate(zip(self.params, grads)):
            # 更新一阶矩和二阶矩
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * grad
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (grad ** 2)
            # 偏差校正
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            # 更新参数
            param -= self.lr * m_hat / (np.sqrt(v_hat) + self.epsilon)
```

#### 定义线性层
```python
class Linear:
    def __init__(self, input_size, output_size):
        self.m = None
        self.original_x = None
        self.weights = np.random.randn(input_size, output_size) * np.sqrt(2. / input_size)  # He初始化
        self.bias = np.zeros((1, output_size))
        self.input_size = input_size
        self.output_size = output_size

    def __call__(self, x):
        return self.forward(x)

    def forward(self, x):
        self.original_x = x
        return np.dot(x, self.weights) + self.bias

    def derivative(self, delta):
        d_weights = np.dot(self.original_x.T, delta)
        d_bias = np.sum(delta, axis=0, keepdims=True)
        return d_weights, d_bias
```
对应公式
$$
Y = X \cdot W + b
$$

#### 定义MSELoss损失函数
```python
class MSELoss:
    def __init__(self):
        pass

    def __call__(self, output, y):
        return self.forward(output, y)

    def forward(self, output, y):
        return np.mean((output - y) ** 2)
```

对应公式
$$
\text{MSE} = \frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2
$$

#### 定义神经网络
```python
class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # 初始化权重和偏置
        self.linear1 = Linear(input_size, hidden_size)
        self.linear2 = Linear(hidden_size, output_size)
        # 初始化 Adam 优化器
        self.optimizer = AdamOptimizer([
            self.linear1.weights, self.linear1.bias,
            self.linear2.weights, self.linear2.bias
        ], lr=0.01)
        self.relu = ReLU()

    def __call__(self, x):
        return self.forward(x)

    def forward(self, x):
        # 前向传播
        x = self.linear1(x)
        x = self.relu(x)
        x = self.linear2(x)
        return x

    def backward(self, X, y, output):
        # 反向传播
        # 输出层误差
        output_error = output - y
        # 隐藏层误差
        hidden_error = np.dot(output_error, self.linear2.weights.T)
        hidden_delta = hidden_error * self.relu.derivative()
        # 计算梯度
        d_weights_hidden_output, d_bias_output = self.linear2.derivative(output_error)
        d_weights_input_hidden, d_bias_hidden = self.linear1.derivative(hidden_delta)
        # 更新参数
        self.optimizer.step([d_weights_input_hidden, d_bias_hidden, d_weights_hidden_output, d_bias_output])

    def parameters(self):
        return [
            self.linear1.weights, self.linear1.bias,
            self.linear2.weights, self.linear2.bias
        ]
```
最大的难点在于反向传播的写法。需要从损失函数开始，反向一层层计算梯度，然后用优化器更新梯度。在Pytorch框架中，loss.backward()即可实现全部反向传播。optimizer.step()实现梯度更新。

#### 测试
用手搓的神经网络测试万能逼近定理
```python
# 生成数据
X = np.linspace(-10, 10, 100)
# y = np.exp(1 / 3 * X) + X ** 3 + 1 / 3 * X ** 2 + X
y = np.sin(X) + np.random.normal(0, 0.1)
# 调整X和y的形状
X, y = X.reshape(-1, 1), y.reshape(-1, 1)
# 初始化神经网络
input_size = 1
hidden_size = 100
output_size = 1
model = NeuralNetwork(input_size, hidden_size, output_size)
# 训练神经网络
epochs = 5000

criterion = MSELoss()
for epoch in range(epochs):
    # 前向传播
    output = model(X)
    loss = criterion(output, y)
    # 反向传播
    model.backward(X, y, output)
    # 打印损失
    if epoch % 100 == 0:
        print(f"Epoch {epoch}, Loss: {loss}")

# 测试神经网络
pred = model(X).reshape(-1)

# 调用画图函数进行画图
draw(X, y, pred)
```

拟合结果如下：
<p align="center">
  <img src="https://media.tidechoir.cn/image/image-20250211135007240.png">
</p>

经过这个简单的例子，实现了BP神经网络的手搓实现，效果并不比Pytorch差多少。当然，更加复杂的神经网络还是使用Pytorch，它通过计算图完成tensor的自动求导。
