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
- **固定的免登录自动校准：** 照片使用 Wikimedia Commons 图片、Flickr 公开内容和 Google 图片；视频使用 Wikimedia Commons 视频和 Google 视频。不再让用户逐站勾选。照片与视频分别校准，每种请求的媒体至少要有两个本次真正可见/可播放的独立来源。
- **每次最多一个人工增强：** 自动校准后，用户可选人机验证增强（Unsplash 照片或 Pexels 照片/视频）、用户登录增强（小红书、Instagram、YouTube 或 Bilibili），或输入其他网址。Skill 只推荐一个最合适来源；Pexels 一次人机验证可同时用于照片和视频。
- **质量优先的软比例守卫：** 主选 10%、备选 25% 只是检测滥选的二次复筛触发线，不是硬上限或配额。有意义、高质量、可用且不重复的素材可以凭明确证据超过比例；视频按总时长与时间段并集计算，不按文件个数。
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

## 开始任务时的四个步骤

先确认原素材只读，再依次完成以下四步；第四步才确认整理方式和全新的输出目录。

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

### 第二步：选择素材媒体类型

选择“照片”、“视频”或“照片 + 视频”。照片和视频会分别进行参考校准：图片必须真正显示，视频必须真正播放，并且每种被请求的媒体都要有至少两个独立可见来源。

### 第三步：自动校准与可选人工增强

Skill 先固定执行免登录自动来源，不让用户逐站勾选：照片使用 Wikimedia Commons 图片、Flickr 公开内容和 Google 图片；视频使用 Wikimedia Commons 视频和 Google 视频。Google 图片的放大预览必须同时记录原始来源网址，缩略图不算；Google 图片/Google 视频各自只算一个参考来源。

自动层完成后，Skill 再询问是否需要一个人工增强：

- **人机验证增强**：按题材和媒体只推荐一个 Unsplash（照片）或 Pexels（照片/视频）。用户在自己的可见浏览器通过验证；Pexels 的一次验证会连续用于照片与视频，不再二次验证。
- **用户登录增强**：按题材和语言只推荐一个小红书、Instagram、YouTube 或 Bilibili。用户自己选站并在自己的可见浏览器登录。
- **其他网址**：用户可输入其他参考 URL。Skill 先打开；公开可见就直接参考，遇人机验证就引导用户通过，只有网站真正要求登录时才请用户自行登录。

用户可接受推荐、换成另一个已列网站，或输入自定义 URL。拒绝或增强失败时，自动校准仍然继续。自动与人工实际可见证据可合并满足双来源门槛。

### 第四步：选择链接或轻量副本

- **建立链接（默认）**：不复制媒体内容，视频保留原文件链接和精确时间码，是最省空间的方式。
- **建立轻量副本**：普通照片安全复制，RAW 优先复用配对 JPEG 或生成 JPEG 审看副本，入选视频时间段导出约 720p H.264/AAC 审看片段。不复制整条高码率视频，但并非零占用，写入前会显示估算。

这一步同时确认一个全新、独立的输出目录。两种方式都不会移动、覆盖或删除原文件；非空输出目录会被拒绝。如用户主动要求，可将视频副本改为仅时间码映射。导出需要 `ffmpeg` 和 `ffprobe`，HDR/HLG、旋转元数据或可变帧率会先做短小样验证；失败不会回退为复制整条原视频。

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
- **10%/25% 只是软触发线**：主选超过 10% 或备选超过 25% 时自动二次复筛，先去重复、弱替代、泛化画面和视频空段。它们不是配额或硬上限。
- **质量例外**：有意义、高质量、可用且不重复的素材可在记录明确证据后超过触发线，没有第二个百分比上限。普通主选溢出转备选，普通备选溢出转未入选，绝不转纪念留档或排除。
- **照片/视频分母分开**：照片按 RAW+JPEG/完全重复去重后的候选数计算；视频按可读源总时长和时间段并集计算，不按文件数。可读视频总时长不超过 60 秒时保留自然首轮结果。

## 输出结构

```text
01_主选/
02_备选_用户复筛/
03_纪念留档/
筛选清单.csv
未入选清单.csv
排除清单.csv
筛选报告.md
```

## 参考网站

这些网站用于校准构图、光线、动作、节奏和叙事方式，不复制具体作品，也不把点赞量或播放量当作质量分数。执行顺序是：固定免登录自动校准，然后最多选择一个人机验证、用户登录或自定义 URL 增强。下表是唯一的用户侧来源说明。

| 流程层级 | 照片来源 | 视频来源 | 用户操作与使用规则 |
|---|---|---|---|
| **1. 免登录自动校准（固定执行）** | [Wikimedia Commons 图片](https://commons.wikimedia.org/wiki/Category:Images)：地点、建筑、历史、文化与纪实语境。<br>[Flickr 公开内容](https://www.flickr.com/explore)：真实事件、街头、社区与个人视角。<br>[Google 图片](https://images.google.com/)：跨站广泛发现；放大预览必须记录原始来源 URL，缩略图不算。 | [Wikimedia Commons 视频](https://commons.wikimedia.org/wiki/Category:Videos)：纪实、历史、文化、地点与公共媒体动态参考。<br>[Google 视频](https://www.google.com/videohp)：跨站发现动作、节奏、镜头结构和题材相关视频。 | 不询问逐站勾选。只有完整图片/合格放大预览或真正视频播放才算。Google 图片与 Google 视频各只算一个来源。 |
| **2A. 可选人机验证增强（最多一个）** | [Unsplash](https://unsplash.com/)：精选构图、光线、旅行、人像与生活方式照片。<br>[Pexels](https://www.pexels.com/)：人物、生活方式和通用场景照片。 | [Pexels Videos](https://www.pexels.com/videos/)：动作、镜头结构和通用 B-roll。 | Skill 按题材/媒体只推荐一个。用户在自己的可见浏览器通过人机验证。Pexels 的一次验证会连续用于照片与视频，不做二次验证。 |
| **2B. 可选用户登录增强（最多一个）** | [小红书](https://www.xiaohongshu.com/explore)：中文生活方式、旅行和本地语境。<br>[Instagram](https://www.instagram.com/)：当代人像、生活方式和创作者照片语言。 | [YouTube](https://www.youtube.com/)：长短视频叙事、镜头组织和剪辑结构。<br>[Bilibili](https://www.bilibili.com/)：中文 Vlog、活动、文化和社区视频。<br>小红书与 Instagram：短视频和当代视觉表达。 | Skill 按题材/语言只推荐一个，用户自己选站并在自己的可见浏览器登录。 |
| **2C. 用户自定义 URL** | 由用户输入的照片参考站 | 由用户输入的视频参考站 | 先打开 URL；公开可见就直接用，遇人机验证则由用户通过，只有网站真正要求时才请用户自行登录。 |

人工增强过程中，Skill **永不索取、接收、保存或处理**用户名、密码、MFA 验证码、Cookie、API 密钥、账户凭据或其他认证秘密，也不会绕过任何保护。用户拒绝或无法使用人工增强时，自动校准仍然继续，不会因此取消。

X 和 Vimeo 不属于路由来源。只打开网页、看到文字、搜索摘要、缩略图或记忆中的平台风格，都不能算视觉校准。照片与视频分别需要两个本次可见来源；一个则为部分可用，零个为不可用，未获得用户明确静态标准授权时必须暂停筛选。

## 使用方式

在 Codex 中调用：

```text
使用 $shining-moments 初筛这个照片和视频文件夹。
```
