---
title: "机器学习——表格数据分类"
subtitle: ""
date: 2024-09-26T16:44:53+08:00
lastmod: 2024-09-26T16:44:53+08:00
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

## 表格分类问题案例

### 数据集分析
数据集来源于问卷，部分列为数值变量，其余为分类变量。

### 数据预处理
1. 将分类变量转化为数字编号
2. 剔除异常值
3. 选择需要训练的列

代码示例
```python
  # 可以使用df_encoded进行模型训练和评估
    y = df_encoded['depress2f_*'] # 因变量
    X = df_encoded.drop('depress2f_*', axis=1)  
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.70, test_size=0.30, random_state=42)
    # 使用 SMOTE 进行数据平衡处理 NC
    index_list = list(range(0, 9)) + list(range(12, 18)) + list(range(18, 22))  # 索引分类变量
    smotenc = SMOTENC(categorical_features=index_list, random_state=42)
    X_train, y_train = smotenc.fit_resample(X_train, y_train)
    scaler = StandardScaler()
    # 提取非指定列
    remaining_columns = [col for col in X_train.columns if X_train.columns.get_loc(col) not in index_list]
    X_train[remaining_columns] = scaler.fit_transform(X_train[remaining_columns])
    X_test[remaining_columns] = scaler.transform(X_test[remaining_columns])

    X_train = torch.tensor(X_train.values, dtype=torch.float)
    X_test = torch.tensor(X_test.values, dtype=torch.float)

    y_train = torch.tensor(y_train.values, dtype=torch.float).unsqueeze(1)
    y_test = torch.tensor(y_test.values, dtype=torch.float).unsqueeze(1)
```

#### 注意
1. 数据增强可运用SMOTE或SMOTENC，其中前者用于数值型数据，后者数值和类别混合。
2. 仅可对训练集进行数据增强，切勿对测试集操作，否则数据泄露。
3. StandardScaler用于标准化，仅对数值数据进行标准化。

```python
X_train[column] = scaler.fit_transform(X_train[column])
X_test[column] = scaler.fit_transform(X_test[column])
```

经过数据预处理后，可以进行模型训练。

### 模型建立与训练
#### 机器学习模型
笔者调用sklearn库中的svc、xgboost等单独模型以及boost模型和集成学习模型。
```python
models = {
        # 单独机器学习模型
        'SVC': SVC(kernel='rbf', C=1.0, gamma='scale', probability=True),
        'LR': LogisticRegression(max_iter=100, solver='lbfgs'),
        'MLP': MLPClassifier(hidden_layer_sizes=(40,), max_iter=100, solver='adam', random_state=42),
        'RF': RandomForestClassifier(),
        'LightGBM': lgb.LGBMClassifier(),

        # boosting算法
        'XGBoost': xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss'),
        'AdaBoost': AdaBoostClassifier(n_estimators=50),
        'GradientBoosting': GradientBoostingClassifier(),

        # 集成学习
        'Bagging': BaggingClassifier(n_estimators=50),
        'Stacking': StackingClassifier(estimators=[
            ('MLP', MLPClassifier(hidden_layer_sizes=(40,), max_iter=100, solver='adam', random_state=42)),
            ('RF', RandomForestClassifier()),
            ('LightGBM', lgb.LGBMClassifier()),
            ('XGBoost', xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')),
            ('AdaBoost', AdaBoostClassifier(n_estimators=50)),
            ('GradientBoosting', GradientBoostingClassifier()),
        ], final_estimator=LogisticRegression(max_iter=100, solver='lbfgs')),

        'Voting': VotingClassifier(estimators=[
            ('MLP', MLPClassifier(hidden_layer_sizes=(40,), max_iter=100, solver='adam', random_state=42)),
            ('RF', RandomForestClassifier()),
            ('LightGBM', lgb.LGBMClassifier()),
            ('XGBoost', xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')),
            ('AdaBoost', AdaBoostClassifier(n_estimators=50)),
            ('GradientBoosting', GradientBoostingClassifier()),
        ], voting='soft')
    }
```
分类效果在0.75左右


#### 深度学习模型

深度学习方法包括定义优化器、损失函数，设置超参数，开启训练即可。

笔者对不同神经网络进行训练尝试

- 简易神经网络实现
```python
class MyNet(nn.Module):
    def __init__(self, input_dim, hidden_dim):
        super(MyNet, self).__init__()
        self.dropout = nn.Dropout(0.5)
        # 第一层
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.bn1 = nn.BatchNorm1d(hidden_dim)
        # 第二层
        self.fc2 = nn.Linear(hidden_dim, hidden_dim * 2)
        self.bn2 = nn.BatchNorm1d(hidden_dim * 2)
        # 残差连接
        self.fc_res = nn.Linear(input_dim, hidden_dim * 2)  # 用于残差连接
        # 第三层
        self.fc3 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.bn3 = nn.BatchNorm1d(hidden_dim)
        # 输出层
        self.fc4 = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        # 第一层
        out = F.leaky_relu(self.bn1(self.fc1(x)))
        out = self.dropout(out)
        # 第二层
        out2 = self.bn2(self.fc2(out))
        out2 = self.dropout(out2)
        # 添加残差连接
        out2 += self.fc_res(x)  # 残差连接
        out2 = F.leaky_relu(out2)
        # 第三层
        out = F.leaky_relu(self.bn3(self.fc3(out2)))
        out = self.dropout(out)
        # 输出层
        out = torch.sigmoid(self.fc4(out))
        return out
```

常见要素为dropout、batchnorm，防止过拟合。
最后一层用sigmoid函数激活。

- embedding分类变量

- 引入transformer等更复杂模型
