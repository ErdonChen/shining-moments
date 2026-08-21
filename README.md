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
- **副本会自动轻量化，不直接搬运大文件：** 链接模式最省空间；副本模式面向人工复筛，RAW 优先复用配对 JPEG，否则生成 JPEG 审看副本，4K/1080p 视频只把入选时间段导成约 720p 轻量片段，不复制整条高码率原视频。这会显著降低复筛目录占用，但不是“零占用”；脚本会先给出空间估算。
- **保持可追溯与原件安全：** 照片、视频与轻量副本都会记录原路径、类别、理由和时间码映射。原文件永不移动、覆盖或删除；正式剪辑仍使用原件。

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

实际执行依赖：Python 3.10+；生成 RAW 审看 JPEG 需要能解码该相机格式的 ImageMagick (`magick`)、RawTherapee CLI、darktable CLI 或 macOS `sips` 之一（有配对 JPEG 时不需要转换器）；导出视频审看片段需要 `ffmpeg` 和 `ffprobe`；链接模式需要操作系统支持符号链接。转换器或视频工具缺失/失败时，脚本会保留原件映射、在报告中标记 `not-generated` / `failed` 并返回部分成功状态，不会伪装成已生成。

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

- **建立链接（默认）**：不复制媒体内容，是最省空间的方式；仍会产生少量链接、清单和报告数据。
- **建立副本**：生成便于人工复筛的轻量文件。普通可直接审看的 JPEG/HEIC/PNG 等保持安全副本行为；RAW → JPEG 审看副本，4K/1080p 推荐时间段 → 约 720p 审看片段。不会直接复制大体积 RAW 或整条高码率视频，但仍会占用空间，执行前会显示估算。

选择副本时，Skill 会在写入前再确认上述轻量化规则与空间取舍。两种方式都不会移动、覆盖或删除原文件。非空输出目录会被拒绝，避免覆盖旧结果。

### 第三步：选择视频交付方式

- **链接模式默认只标时间码**：建立整条原视频的链接，在清单中标注推荐片段；也可显式选择另存新片段。
- **副本模式默认导出轻量候选片段**：主选、备选和纪念留档中有时间码的入选片段会导出新的 H.264/AAC MP4。横屏最大 1280×720，竖屏最大 720×1280；低于或等于该范围的源不放大、不拉伸。
- **副本模式显式选“只标时间码”**：只保留原路径与时间码映射，不复制整条视频。

导出片段需要 `ffmpeg` 和 `ffprobe`。脚本会检查时间码与原时长；遇到 HDR/HLG、旋转元数据或可变帧率时，先生成短小样检查色彩标记、方向、可播放性和音画时长偏差，再导出完整候选段。任何失败都不会回退为复制整条原视频。

## 轻量副本的清单与示例

输入 CSV 至少包含 `source_path,decision,reason`；视频区间再填 `start_time,end_time`，已知 RAW 配对片可填可选的 `paired_jpeg_path`。未填时，脚本会优先查找同目录同名 `.jpg`/`.jpeg`。

```bash
python3 scripts/build_review_set.py \
  --manifest shortlist.csv \
  --output review-set \
  --mode copy \
  --video-delivery auto
```

`shortlist.csv` 中的映射可以得到如下复筛产物：

| 原始高质量素材 | 复筛产物 | 清单记录 |
|---|---|---|
| `/media/IMG_1234.CR3` | `01_主选/IMG_1234__review.jpg` | `paired-jpeg` 或 `generated-jpeg`；同时保留 RAW 原路径与审看 JPEG 路径 |
| `/media/GH010042.MP4` 的 `00:01:12–00:01:24` | `01_主选/GH010042__00-01-12_to_00-01-24.mp4` | `video-review-clip`；保留原路径、时间码、类别和理由，4K/1080p 源输出约 720p |

`筛选清单.csv` 还会写入 `review_source_path`、`organized_path`、`review_asset_kind`、`generation_status` 和 `generation_detail`。类型可区分原件链接/普通副本、现成配对 JPEG、新生成 JPEG、720p 候选片段、仅时间码映射与未生成项。输出名重复时使用 `__2`、`__3` 等稳定后缀，不覆盖文件。

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
