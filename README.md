# Shining-Moments-Cut

[English](README.en.md) | 简体中文

本仓库是一个包含两个 Skill 的 Skill 集合：

- **[Shining Moments](skills/shining-moments/README.md)**：智能选片 Skill，结合自动参考与可选参考增强筛选照片和视频。
- **[Shining Cut](skills/shining-cut/README.md)**：智能剪辑 Skill，结合自动参考与可选参考增强生成剪辑脚本、分镜、初剪与可选细剪。

推荐先用 Shining Moments 筛选素材，再用 Shining Cut 完成视频剪辑；两个 Skill 也可以独立使用。

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

## 包内结构

```text
skills/
├── shining-moments/
└── shining-cut/
```

两个目录都是独立 Skill，可同时安装，也可按需单独安装。
