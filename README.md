# Shining-Moments-Cut

[English](README.en.md) | 简体中文

本仓库是一个包含四个可独立安装 Skill 的完整选片与剪辑技能包：

- **[Shining Moments](skills/shining-moments/README.md)**：智能选片 Skill，结合自动参考与可选参考增强筛选照片和视频。
- **[Shining Cut](skills/shining-cut/README.md)**：智能剪辑 Skill，结合自动参考与可选参考增强生成剪辑脚本、分镜、初剪与可选细剪。
- **[Watch](skills/watch/SKILL.md)**：来自 `bradautomates/claude-video` 的视频理解 Skill，负责解码画面、提取时间戳帧与字幕/转录证据。
- **[Video Use](skills/video-use/README.md)**：来自 `browser-use/video-use` 的对话式剪辑 Skill，负责逐字转录、EDL、渲染、字幕、动画与成片自检。

推荐先用 Shining Moments 筛选素材，再由 Shining Cut 编排 Watch 和 Video Use 完成参考校准、剪辑与质检。四个 Skill 也可以按需独立使用。

## Shining Moments：先找到值得保留的瞬间

Shining Moments 通过参考校准筛选照片和视频，保留不确定但可能有纪念价值的素材，并把最终选择权留给用户。

- **自动参考**：照片使用 Wikimedia Commons Images、Flickr 和 Google Images；视频使用 Wikimedia Commons Videos 和 Google Videos。
- **增强参考（可选）**：可按素材类型选择 Unsplash、Pexels、小红书、Instagram、YouTube、Bilibili 或自定义链接。需要验证或登录时由用户自行完成。
- **大致步骤**：确认题材与参考 → 筛选主选、备选和纪念素材 → 输出清单与原片映射。

筛选完成后，可以继续使用 Shining Cut 自动剪辑入选视频。

## Shining Cut：把入选视频剪成故事

Shining Cut 从相近参考视频中提炼节奏、结构、镜头语言、声音与色彩方向，再映射到用户自己的视频素材。

- **自动参考**：默认使用 Google Videos 和 Wikimedia Commons Videos。
- **增强参考（可选）**：可选择 YouTube 或 Bilibili，也可以直接提交自己的参考视频链接。
- **大致步骤**：确认题材与参考目标 → 生成脚本、分镜和含一级调色的初剪 → 按需细剪与可选二级调色。

如果用户没有使用 Shining Moments，Shining Cut 会在开头确认素材是否已经通过其他方式筛选；已筛选素材可以直接提交路径，未筛选素材则推荐先使用 Shining Moments。

## 整合方式

- Shining Moments 在视频筛选时使用 Watch 获取真实解码帧和时间戳证据，但不会自动开始剪辑。
- Shining Cut 负责素材映射、参考校准、脚本/分镜和三次集中确认；其已获批准的蓝图直接作为 Video Use 所需的剪辑策略确认，避免重复询问。
- Watch 负责“看见和听见”，Video Use 负责“剪辑和验证”。Shining Cut 保留端到端编排权、原片映射和最终交付记录。
- 两个上游 Skill 均以固定提交快照随包提供，运行文件、许可证和来源记录保持完整；详见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和 [UPSTREAM_SOURCES.json](UPSTREAM_SOURCES.json)。

## 包内结构

```text
skills/
├── shining-moments/
├── shining-cut/
├── watch/
└── video-use/
    ├── helpers/
    └── skills/manim-video/
```

安装时必须复制每个 Skill 的完整目录，不能只复制 `SKILL.md`：Watch 需要同级 `scripts/`，Video Use 需要同级 `helpers/`、`pyproject.toml` 和内置的 `skills/manim-video/`。

## 环境要求与致谢

### Watch（来自 `bradautomates/claude-video`）

- Python 3，以及可在 `PATH` 中调用的 `ffmpeg`、`ffprobe` 和 `yt-dlp`。
- Agent 必须允许执行本地命令和读取提取出的 JPEG 帧。Windows 使用 `python`；macOS/Linux 通常使用 `python3`。
- 公共视频有原生字幕时不需要转录密钥；无字幕时可选配 Groq 或 OpenAI API key 作为 Whisper 转录回退。只有提取出的音频会在启用回退时发送给对应服务，视频本身不会上传。

### Video Use（来自 `browser-use/video-use`）

- Python `>=3.10`；在 `skills/video-use/` 中执行 `uv sync` 或 `pip install -e .`，安装 `requests`、`librosa`、`matplotlib`、`pillow` 和 `numpy`。
- `ffmpeg` 与 `ffprobe` 是硬性要求；`yt-dlp` 仅在下载在线素材时需要。
- ElevenLabs API key 是 Scribe 逐字转录所必需的，应通过环境变量或未提交的 `.env` 配置，禁止写入仓库。
- Node.js/npm 仅在使用 HyperFrames 或 Remotion 动画槽位时需要；HyperFrames 当前要求 Node.js 22+。Manim 和其他动画引擎按需安装。

### 致谢

- 感谢 **Bradley Bonanno（Brad Bonanno / [bradautomates](https://github.com/bradautomates)）** 创建 [claude-video](https://github.com/bradautomates/claude-video) 与 Watch Skill。本包保留其 MIT 许可证与版权声明。
- 感谢 **[Browser Use](https://github.com/browser-use)** 团队创建 [video-use](https://github.com/browser-use/video-use)。本包保留其 MIT 许可证与版权声明。
