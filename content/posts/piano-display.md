---
title: "Web智能钢琴实现"
subtitle: ""
date: 2025-03-17T22:12:00+08:00
lastmod: 2025-03-17T22:12:00+08:00
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

## Web智能钢琴实现

### 简介
笔者热爱音乐，擅长钢琴，最近想做一个自动播放乐谱的功能。诸如此类自动演奏的软件有不少，弹琴吧、虫虫钢琴均可实现钢琴模拟和乐谱同步，但都收取会员费。
因此，借助Web技术手动实现一个是非常实用且有趣的事情。


### 参考项目
全部手搓太耗时间，笔者在github上找到一个很棒的项目。
[自动钢琴](https://github.com/AutoPiano/AutoPiano)

运行也非常简单
```bash
yarn install
yarn start
```
![image-20250317213816830](https://media.tidechoir.cn/image/image-20250317213816830.png)

这是一个Vue项目，用CSS模拟了钢琴的黑白键。不过仔细一看，这个钢琴缺少了低音域和高音域。

笔者决定做一个88键 **“满血版”**。经过一个多小时，大功告成!
![image-20250317214119446](https://media.tidechoir.cn/image/image-20250317214119446.png)

- 布局技巧

所有白键直接均匀排开，麻烦的是黑键布局。可将每五个黑键分成一个组，组里采用绝对定位，组与组之间间隔相等。

### 项目原理
#### 按键
事实上，这个“钢琴”是通过一个json来实现的，每个键都对应一个mp3。
![image-20250317214619248](https://media.tidechoir.cn/image/image-20250317214619248.png)

88个键范围： 白键从A0-C8 黑键从A#0-A#7。

如果要更换音源，需要修改这88个音的MP3。人工对钢琴的每个键录音非常麻烦。
事实上，玩音乐的人都知道，musescore软件中音源是通过sf2格式存储的。那么有无办法将sf2文件转成所有音的MP3文件呢？

笔者查询百度和DS未果，一筹莫展之际，偶然间在github中找到一个读取sf2的库。

```python
import sf2_loader as sf
loader = sf.sf2_loader(r"you-path.sf2")

music_list = [
    'A0', 'B0', 'C1', ..., 'A7', 'B7', 'C8'
]

for note in music_list:
    loader.export_note(note, format='mp3', name=f'{note}.mp3')
```

一波操作，导出所有白键的音源（黑键同理）。这样就实现了钢琴换音源工作。可以将钢琴换成施坦威等高级音质。


#### 自动播放midi
该项目还支持自动播放midi功能。
具体上是依赖@tonejs库，读取midi后转换成所有音符的列表，记录了音符的音调、持续时间、开始的时间戳等。通过递归函数即可根据midi弹奏我们的Web钢琴。
```javascript
import { Midi } from '@tonejs/midi'
```

以下为核心代码：
- 读取midi
```javascript
loadMidiAndPlay(midi) {
  Midi.fromUrl(midi).then((data) => {
    this.currentMidiData = data
    this.midiOffset = 0
    this.playMidi()
  });
}
```
- 开始播放midi
```javascript
if (this.currentMidiData) {
  this.midiStop = false
  this.midiNotes = []
  this.currentMidiData.tracks.forEach((track, trackIndex) => {
    this.midiNotes = this.midiNotes.concat(track.notes)
  })
  this.groupNotesByTime(); // 按照起始时间分组
  this.startTime = +new Date() // 获取开始时间
  this.playLoop()
}
```

- 演奏midi主体程序
```javascript
playLoop() {
  if (this.midiStop) return
  let now = +new Date()
  let playedTime = now - this.startTime // 单位毫秒ms
  // 遍历分组后的音符
  for (let i = 0; i < this.groupedNotes.length; i++) {
    const group = this.groupedNotes[i];
    if (playedTime >= group.time && !group.played) {
      group.played = true; // 标记该组已被播放
      // 播放该组的所有音符
      group.notes.forEach((note) => {
        Observe.$emit(OBEvent.PLAY_MIDI_NOTE, note);
      });
    }
  }
  // 检查是否播放完毕
  if (this.groupedNotes.every(group => group.played)) {
      Observe.$emit(OBEvent.MUSIC_END);
      return;
  }
  requestAnimationFrame(() => this.playLoop()); // 递归执行
}
```
通过这样的原理，即可实现midi自动化演奏，十分有趣。未来，笔者还将研究乐谱自动渲染和同步播放。项目不久后将在开放公网访问，欢迎支持。
