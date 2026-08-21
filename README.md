# Shining Moments

[English](README.en.md) | 简体中文

<p align="center">
  <a href="https://github.com/ErdonChen/shining-moments/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/ErdonChen/shining-moments?style=flat-square"></a>
  <a href="https://github.com/ErdonChen/shining-moments/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/ErdonChen/shining-moments/ci.yml?branch=main&amp;style=flat-square&amp;label=CI"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square"></a>
  <img alt="Codex Skill" src="https://img.shields.io/badge/Codex-Skill-111111?style=flat-square">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white">
</p>

## 核心亮点

Shining Moments 是一次保守的“第一次过滤”：它帮助缩小复筛范围，但把最终选择权留给用户。

- **先选素材类型，再使用对应标准：** 开始时从综合、风景旅行、建筑空间、人文纪实、人像、家庭、朋友、Vlog/活动或自定义中选择；每类素材使用针对性的筛选标准，不把同一套评分模板反复套用到所有内容。
- **用分类参考校准审美，而不追逐热度：** 风景与建筑可参考 500px、YouTube、ShotDeck；人像与纪实可参考 LensCulture、Magnum Photos；关系影像与视频叙事还会参考 Vimeo Staff Picks。Instagram、小红书和 X 只提供趋势线索，不以点赞量代替视觉语言与叙事判断；[完整分类参考见“参考网站”](#参考网站)。
- **照片与视频统一分层，另设情感通道：** 输出主选、备选复筛和纪念留档；亲友关系与不可替代的情感瞬间可以独立于纯技术质量获得保留。
- **交付方式可选，原片始终不动：** 用户可选择链接或副本；视频可选择只标时间码或导出新的候选片段。原文件永不移动、覆盖或删除。

一个面向个人照片与视频的保守型初筛 Skill。它先排除明确不可用的素材，再把主选、可用备选、重复项和具有亲情或友情价值的瞬间留给用户复筛，而不是替用户做最终决定。

## 命名灵感

名称 **Shining Moments** 的灵感来自《煌めく瞬間に捕われて》，中文常译作《捕捉闪耀的瞬间》。这里的“闪耀”既指构图、光线和叙事出色的画面，也指技术不完美但不可替代的亲情、友情和人生瞬间。

## Agent 与模型兼容性

Shining Moments 并非 Codex 专用。核心 `SKILL.md`、分类与筛选规则、`references/` 参考资料和 `scripts/build_review_set.py` 整理脚本本身不绑定具体模型；只要 Agent 能读取这些文件并具备所需工具，就能采用同一套流程。

- **本机 Codex：** 当前安装于 `~/.codex/skills/shining-moments`，属于 Codex 个人 Skills 目录，因此 Codex 能自动发现。其他 Agent 需要把完整 Skill 目录安装到各自官方支持的 Skills 位置，或在任务中手动读取 `SKILL.md`。
- **GitHub Copilot：** 官方文档列出的项目 Skills 位置是 `.github/skills/<skill-name>`、`.agents/skills/<skill-name>` 和 `.claude/skills/<skill-name>`；个人 Skills 位置是 `~/.copilot/skills/<skill-name>` 或 `~/.agents/skills/<skill-name>`，每个 Skill 子目录内放置 `SKILL.md`。参见 [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) 和 [Adding agent skills for GitHub Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)。
- **Google 的相关 Agent 环境：** Google Gemini API managed agents 使用的 Antigravity runtime 可从 `.agents/skills/<skill-name>/SKILL.md` 自动发现 Skill；这不代表所有 Google 聊天产品都具有相同能力。参见 [Building managed agents](https://ai.google.dev/gemini-api/docs/custom-agents)。
- **Codex 元数据：** `agents/openai.yaml` 只提供 Codex 的界面与调用元数据；其他 Agent 可以忽略它，不影响核心 Skill。

普通聊天模型也可以采用这里的筛选准则并协助判断，但如果没有本地文件访问、图片/视频分析和命令执行工具，就无法自动遍历素材、创建链接或副本，也无法导出视频片段。对于上面未列出的 Agent，不预设其自动发现机制，请以该产品的官方文档为准或让它直接读取 `SKILL.md`。

实际执行依赖：Python 3.10+；选择导出视频候选片段时需要 `ffmpeg` 和 `ffprobe`；链接模式需要操作系统支持符号链接。

## 开始任务时的三个选择

开始前先确认素材来源和一个全新的输出目录，然后依次询问以下三项。

### 第一步：选择素材类型

| 选项 | 主要筛选重点 |
|---|---|
| 综合/混合 | 每张照片或每个视频片段分别匹配最合适的类别 |
| 风景与旅行 | 光线、天气、空间层次、地点感和旅行叙事 |
| 建筑与空间 | 几何、尺度、材质、动线及人与空间的关系 |
| 人文与纪实 | 真实行动、环境语境、文化细节和人物尊严 |
| 人像与写真 | 表情、眼神、姿态、身份感、肤色与背景控制 |
| 家庭与亲情 | 关系、情感真实性、家庭节奏和不可替代性 |
| 朋友与友情 | 共同动作、相互反应、默契、支持和群体关系 |
| Vlog 与活动 | 叙事功能、时间进展、镜头变化、声音和可剪辑性 |
| 自定义 | 根据用途、受众、必留时刻和参考样片建立规则 |

未选择时默认使用“综合/混合”。即使选择了其他类型，关系与纪念价值仍是安全保留底线。

### 第二步：选择整理方式

- **建立链接（默认）**：不复制媒体文件，适合素材量大或存储空间有限的任务。
- **建立副本**：复制入选素材，适合素材较少或需要便携交付的任务。

两种方式都不会移动、覆盖或删除原文件。非空输出目录会被拒绝，避免覆盖旧结果。

### 第三步：选择视频交付方式

- **只标时间码（默认）**：保留整条原视频的链接或副本，在清单中标注推荐片段的开始和结束时间。
- **导出独立新片段**：从原视频另存新的主选或备选片段，供用户直接复筛；原视频不会被裁切或改写。

导出片段需要 `ffmpeg` 和 `ffprobe`。脚本会先检查时间码是否有效并且没有超过原视频时长。为避免二次画质损失，默认保留原音视频流，因此粗剪边界可能对齐附近关键帧。

## 初筛规则

- **双通道判断**：同时考虑审美与叙事价值，以及人物关系与纪念价值。
- **主选 `select`**：最值得优先查看的素材，仍由用户最终决定。
- **备选 `review`**：可用、存疑、可修复、重复或受关系价值保护的素材。
- **纪念留档 `memory`**：具有情感意义，但不建议进入正常成片的素材。
- **排除 `excluded`**：明确不可用且没有已知纪念价值的素材；只记录原因，不建立链接或副本。
- **重复素材**：同组可推荐一个主选，其余所有可用版本进入备选供用户比较。
- **视频抖动**：普通视频在合理防抖后仍不可用时可以排除；人物和互动仍可辨认的亲友视频进入备选；完全不可视但意义明确的内容只进纪念留档。
- **长视频**：按片段判断并记录精确时间码，不能用单个坏画面否定整条视频。

## 输出结构

```text
01_主选/
02_备选_用户复筛/
03_纪念留档/
筛选清单.csv
排除清单.csv
筛选报告.md
```

## 参考网站

这些网站用于校准构图、光线、动作、节奏和叙事方式，不复制具体作品，也不把点赞量或播放量当作质量分数。

| 类型 | 参考站点 |
|---|---|
| 风景、旅行与地点叙事 | [500px](https://500px.com/)、[YouTube](https://www.youtube.com/)、[ShotDeck](https://shotdeck.com/)、[National Geographic Photography](https://www.nationalgeographic.com/photography/) |
| 建筑与空间 | [ArchDaily](https://www.archdaily.com/)、[Dezeen](https://www.dezeen.com/)、ShotDeck |
| 人像、人文与纪实 | [LensCulture](https://www.lensculture.com/)、[Magnum Photos](https://www.magnumphotos.com/)、Instagram、小红书 |
| 家庭、亲情与友情 | [Documentary Family Awards](https://documentaryfamilyawards.com/)、[Family Photojournalist Association](https://www.fpja.com/)、[This Is Reportage](https://thisisreportage.com/)、小红书 |
| 视频节奏与情感叙事 | [Vimeo Staff Picks](https://vimeo.com/channels/staffpicks)、[NOWNESS](https://www.nowness.com/)、YouTube |
| 趋势与作者发现 | Instagram、小红书、[X](https://x.com/)；只作发现入口，不以热度判断质量 |

## 使用方式

在 Codex 中调用：

```text
使用 $shining-moments 初筛这个照片和视频文件夹。
```
