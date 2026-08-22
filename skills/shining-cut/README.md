# Shining Cut

[English](README.en.md) | 简体中文

Shining Cut 是一个智能剪辑 Skill，推荐搭配 Shining Moments 使用。它从相近参考视频中提炼节奏、结构、镜头语言、声音和色彩方向，再映射到用户已经筛选的视频素材。

## 参考方式

- **自动参考**：默认使用 Google Videos 和 Wikimedia Commons Videos。
- **增强参考（可选）**：可选择 YouTube 或 Bilibili，也可以直接提交自己的参考视频链接。

## 三步流程

1. **确认题材与参考目标**：读取已筛选素材，确认题材、关键词和参考方案。
2. **脚本与初剪**：生成剪辑脚本、时间码分镜和一级调色方案；用户确认后制作初剪。
3. **细剪（可选）**：审查初剪并给出修改清单；用户需要时再进行细剪、可选二级调色和最终质检。

Shining Cut 可以读取 Shining Moments 的筛选清单和原片映射，也可以接收其他方式筛选完成的视频。未筛选的原始素材会先推荐使用 Shining Moments。

所有剪辑都使用高质量原片映射，不移动、覆盖或删除原始素材。

## 包内运行时

- **Watch**：负责参考视频和本地成片的真实解码、时间戳帧与字幕/转录证据。
- **Video Use**：负责逐字转录、EDL、剪辑渲染、字幕/动画合成和切点自检。

完整安装 `Shining-Moments-Cut` 技能包时，这两个 Skill 已位于 Shining Cut 的同级目录。Shining Cut 的蓝图确认同时满足 Video Use 的策略确认要求，不会重复询问一次常规剪辑策略。
