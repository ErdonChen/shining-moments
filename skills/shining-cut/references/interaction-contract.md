# Interaction contract

Shining Cut normally has three centralized confirmations. Gather decisions in batches and prefill recommendations from the paths, manifests, reports, and media inventory. Do not turn each field into a separate question.

## Before the first confirmation

Inspect the inputs read-only and classify readiness:

- `shining-moments`: a Shining Moments output with usable reports or manifests.
- `other-screened`: another explicitly screened set with an included-material path and, when available, a selection list.
- `unscreened`: raw or mixed footage without a trustworthy inclusion decision.
- `unclear`: the claimed selection cannot be mapped to readable files or cannot be separated from rejected footage.

For `unscreened`, pause and recommend `$shining-moments`. For `unclear`, ask only for the missing path, manifest, or selection boundary. Neither case starts the editing workflow.

When a Shining Moments result is supplied, read `筛选清单.csv`, `未入选清单.csv`, `排除清单.csv`, and `筛选报告.md` when present. Resolve links, review clips, or derivatives to the manifest's high-quality `source_path` and retained source interval. Use primary selections first and backup selections only as needed.

## Confirmation 1: material and reference plan

Present one compact, numbered block with recommended values already filled:

1. **Material readiness and location:** screening route, included-material path, manifest/report path, and whether original mapping is complete.
2. **Content and final form:** infer a likely topic and form such as travel Vlog, portrait story, short documentary, music montage, or a custom form. Label uncertain inferences and let the user edit them.
3. **Keywords:** extract reliable location, people, season, event, and mood terms from paths and reports. Do not guess when evidence is weak.
4. **Reference plan:** state that automatic public-reference discovery will run. Prefill enhancement as `off`; the only enhanced options are `YouTube` or `Bilibili`.
5. **User reference:** accept an optional main-reference URL. If absent, Shining Cut selects the main reference automatically.
6. **Project output:** propose a new location under the footage project's `edit/` area and state that originals remain untouched.

Close with this interaction pattern:

> 在开始剪辑之前，我们先一次性确定素材与参考方案。下面已经预填了推荐值；你可以回复“全部按推荐”，也可以按编号一次性修改任意几项。

Do not ask whether automatic discovery should run; it is mandatory. Do not ask about photos unless the user requested them. A user-managed login/readiness handoff for an enabled enhancement is an operational pause, not a new editorial confirmation.

## Confirmation 2: script and storyboard blueprint

After reference calibration and source analysis, present the complete blueprint defined in `script-blueprint.md`. It must already recommend runtime, aspect ratio, publishing destination, structure, original timecodes, storyboard frames, sound, captions, transitions, and reference rationale.

Close with:

> 这是根据素材和参考视频生成的剪辑脚本与分镜蓝图。你可以回复“按此蓝图初剪”，也可以一次性说明需要修改的部分。

The approved blueprint also satisfies the downstream `video-use` requirement for a plain-English editing-strategy confirmation. It must show the proposed primary grade. Do not add another routine strategy round.

## Confirmation 3: fine-cut decision

Only after a playable rough cut has been rendered, watched, and converted into a timecoded change list, present:

> 初剪和推荐的细剪方案已经完成，请选择：
>
> 1. 保留当前初剪，不再细剪。
> 2. 按推荐方案自动细剪。
> 3. 修改细剪方案后执行；可以一次性说明节奏、镜头、音乐、字幕、转场、色彩或时长调整，也可以提供具体时间码。

Also show the color choice in the same confirmation: keep the rough cut's primary grade by default, apply the recommended secondary grade, or describe a custom secondary-grade adjustment. Entering fine cut alone never authorizes secondary grading.

If the user chooses option 1, retain the rough cut, perform delivery QA on that artifact, and label it accurately as the accepted rough-cut version. Options 2 and 3 proceed to the confirmed fine cut without another ordinary approval.

## Genuine blockers

An extra question is allowed only when continuing would be unreliable or unsafe, including:

- unreadable, corrupt, missing, or unmappable source media;
- multiple unrelated events that cannot be separated from existing evidence;
- an inaccessible user-supplied main reference, where replacing it would change the user's choice;
- no playable automatic reference evidence;
- an obvious privacy or consent risk;
- an unwritable or conflicting output target;
- a required editing or viewing runtime that fails preflight.

State the exact blocker, the evidence already checked, and the smallest user action needed. Do not scatter optional taste questions between confirmations.
