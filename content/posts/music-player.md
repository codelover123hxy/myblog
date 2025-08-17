---
title: "Web智能乐谱播放器实现"
subtitle: ""
date: 2025-03-24T22:01:38+08:00
lastmod: 2025-03-24T22:01:38+08:00
draft: false
author: "hxy"
authorLink: ""
license: ""
tags: ["音乐"]
categories: ["趣味项目", "技巧"]
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

## Web智能乐谱播放器实现
### 简介
在上一篇博客中，我实现了智能钢琴Web项目，仅需上传midi或musicxml可自动弹奏，同时支持更换音源。作为音乐爱好者，笔者在思索如何渲染乐谱，和钢琴曲一同播放。

### 技术流程

乐谱播放器的研发流程分为
1. 读取乐谱
2. 渲染乐谱
3. 与midi同步，动态更新播放进度

musicXML是一种标准的乐谱记录格式，能够还原谱子全貌。市面上有许多读取musicxml的库，包括VexFlow、OpenSheetMusicDisplay等。

受[用VUE实现一个乐谱播放器](https://www.jianshu.com/p/a4ad9337decb)启发，笔者选用OpenSheetMusicDisplay库作为musicxml的渲染工具。

### 核心原理
#### 乐谱渲染
首先安装opensheetmusicdisplay库
```json
"opensheetmusicdisplay": "^1.8.4"
```
接着初始化osmd库
```javascript
import { OpenSheetMusicDisplay as OSMD } from 'opensheetmusicdisplay'
mounted() {
  this.setupOsmd()
},

methods: {
  async setupOsmd() {
    if (this.$refs.container) {
      this.osmd = new OSMD(this.$refcontainer, { 
        autoResize: this.autoResize, 
        backend: "svg",
        drawTitle: true,
        // followCursor: true, // 乐谱跟随光标播放
      });
        
      // 渲染xml this.file是containestyle.width = "720px";路径
      await this.osmd.load(this.filethis.title);
      await this.osmd.render();
      // 初始化光标
      this.osmd.cursor.show();
      // 设置光标初始位置
      this.osmd.cursor.reset();
    }
  }
}
```
通过初始化，即可将musicxml文件渲染到项目中，支持调节宽度，显示光标。

渲染效果
![image](https://media.tidechoir.cn/image/111.png)

#### 乐谱同步
乐谱渲染后，最大的难点在于如何将乐谱的**光标（cursor）**和**midi**完全同步。
cursor带有previous()、next()和reset()方法，分别前移、后移和重置。
笔者最初想到的方法是将midi中的音符按照起点时间分组，每经过一组音符调用一次cursor.next()。
这种方法的确能处理简单的谱子，但存在很大的弊端。
1. 对于琶音、休止符等很难处理。midi里只有音符流，并没有标明这些音符，使用时间差的阈值来判断，不精确。
2. 连音符号在midi中只有一个音，但cursor会多次移动。
3. 误差会逐渐累计，无法修正。

查阅多种资料，仍未发现有什么很好的同步方法。

经过思考，笔者认为最合理的方法是利用时间来同步，也就是midi播放到某个音时，cursor也必须移动到对应时间的音符上。
我们分别得到midi和cursor的时间：
```javascript
// midi音符的时间
group.notes.forEach((note) => {
  console.log(note.time) // 获取音符的时间
  // play this note
});

// cursor指向音符的时间
let iterator = cursor.iterator
let realValue = iterator.currentTimeStamp.realValue 
```

经过打印数据，寻找两者的关系。发现cursor指向的“时间”其实是乐谱中的小节数，例如10.25代表该音符位于第11个小节的1/4处。两者能够通过BPM建立等式。

另外一个问题是，处理节拍中途切换的复杂谱子。我们需要实时读取cursor对应的BPM。然后既可分段处理，也可将musicxml的音符位置累计转换成时间。笔者采取后者。

- 移动光标逻辑：
```javascript
// 接收到midi音符时移动cursor
move_cursor(time) {
  let iterator = this.osmd.cursor.iterator
  // 设置一个误差阈值
  while (this.currentTime < time && time this.currentTime > 0.01) {
    this.osmd.cursor.next() // 向后移动cursor
    let realValue = iterator.currentTimeStamrealValue
    this.currentTime += 4 * 60 / this.currentBP* (realValue - this.currentRealValue)
    // 谱子一个小节四拍
    this.currentRealValue = realValue
    // 更新BPM
    let BPM = iterator.currentMeasurtempoInBPM
    if (BPM !== this.currentBPM) {
      this.currentBPM = BPM
    }
  }
}
```
经过不断尝试、修正，最终实现了完美的同步。看着谱子上的cursor随着音乐自动播放，还是挺欣喜的。未来，将会实现移动端的适配。

### 智能化运用
事实上，可以利用扒谱工具将上传的mp3自动转换成midi，并生成musicxml。这样就可以自动扒谱并同步演奏。
[transkun](https://github.com/Yujia-Yan/Transkun)是一款强大的扒谱工具，由基于transformer的预训练模型构成。

```python
pip3 install transkun
transkun input.mp3 output.mid
```
仅需两步，即可将mp3格式的钢琴曲转成高质量的midi。

### 结语
经过这次实践，揭开了智能乐谱软件的神秘面纱。这并不复杂，只需要midi和musicxml即可完美实现。相反，将谱子打入电子软件是一件非常耗费人力的事情。

现成的PDF转电子谱效果差强人意，也许可以自研深度学习算法试试，大抵是一件更具挑战性和趣味的事情。
