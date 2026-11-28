---
name: blender-compositing
description: 使用 Compositing Workflow 插件与公共 blenderctl 制作、修改和验收合成画面，处理静帧、连续序列、线色叠合、模板复用、参数对比与现场深度补光接回。接到成片调色、辉光景深、三渲二线色合成或深度补光任务时使用。
metadata:
  version: "0.10.0"
---

# Blender 合成

用 `blenderctl compositing describe` 读当前合成合同。多层 EXR 的 Cryptomatte 和光组按实际层名连接。项目 OCIO 随配置、外部变换和媒体的 SHA-256 一起锁定，分别检查线性通道、显示视图和最终编码。

本技能负责利用渲染出来的多层通道做色调统一、辉光景深、线稿叠合、局部深度补光与成片输出，属于 [合成部门](https://github.com/tsist/blender-ai-workflow/blob/main/skills/blender-work-methodology/references/departments/compositing.md)。公共 CLI 的批次目录、SHA 校验与长作业等待规则见 [blender-cli](https://github.com/tsist/blenderctl/blob/main/skills/blender-cli/SKILL.md)。

## 第一步：先划清合成边界，再查真实入口

动手前先看问题适合留在合成还是退回三维场景。靠现有通道就能在连续帧里干净解决的光色微调、辉光、暗角、深度雾和三渲二线色叠合，在合成里做完最快。遇到真实几何遮挡错误、缺投射阴影、材质高光质地不对或大幅改机位，直接退回三维场景重渲，硬修只会越补越花。

查清当前可用命令与参数字段，省去猜字段名和版本差异的麻烦。

```powershell
$ctl = './blenderctl.ps1'

# 查看合成产品入口与宿主环境
& $ctl discover --product compositing

# 不启动 Blender 直接查看契约与分节字段
& $ctl compositing describe
& $ctl compositing describe --operation run --param preview
& $ctl compositing describe --operation study --param cases
```

需要跑哪项子命令，先跑一次 `--help` 或 `describe --operation <op> --schema` 拿到精确字段。

## 第二步：核对输入色彩、视图变换与 Alpha 预乘

开干前先摸清源工程和素材的色彩身份。把色彩空间和 Alpha 搞混，后面怎么调色都会偏色或出黑边。

1. **分清线性 EXR 与显示编码素材**：多层线性 EXR 保留场景线性光数据，遍历全部 subimage 核对所需层和通道，主图默认对应 `Combined`。已经显示编码的 sRGB PNG 或 SDR 视频已烘焙视图映射，目标若为保留原图外观，在独立工作副本上切到 `Standard` / `sRGB`、`None` look、曝光 `0` 与伽马 `1` 后再合成；目标若为重做场景调色，再沿用 `AgX` 这类场景视图变换。
2. **明确每张输入的色彩空间与 Alpha 模式**：在请求里逐项写出主源和额外图像的 `file`、SHA256、`colorspace` 与 `alpha_mode`。PNG 经过 `OIIO` 读取时按直通（Unassociated / Straight）口径检查，合成边缘出现黑边或发灰时优先核对预乘方式。
3. **核对渲染层与去噪通道**：使用 `Render Layers` 时核对目标 `Scene` 和 `ViewLayer`。后台预览阶段关闭原生去噪时，节点去噪直接接 `Image` 以及已启用的 `Denoising Albedo` 与 `Denoising Normal`。
4. **先读后改，保留原件**：在 `work/audit/<batch>/>/jobs` 下工作，用 `compositing inspect` 摸清已有节点图与保护对象，所有改动落在独立工作副本里，源文件留着对照。

```powershell
& $ctl --jobs-dir $jobs compositing inspect $src `
  --expected-sha256 $sha `
  --resources $resourcesJson `
  --scene Scene `
  --workflow-id main-comp
```

## 第三步：按静帧或连续序列搭节点图

整理好 UTF-8 请求文件、`resources` 清单和单一 `manifest` 后，用 `compositing run` 在工作副本上执行 `create`、`update`、`adopt` 或 `detach`。

- **静帧先对画布再调色**：在 `preview` 里写明输出画布尺寸，输入尺寸不一致时先加 `Scale` 或 `Transform` 适配，避免默认居中裁切把边缘切掉。单个直立透明底产品需要精准贴地摆位时，用 `scripts/alpha_layout.py` 测量 Alpha 边界框并统一地面高度。
- **连续序列对齐帧号与帧率**：固定 `reference_frame` 作为基准帧，逐帧列出 `file`、SHA256、`source_frame` 与 `ONE_TO_ONE` 映射，保持 `Scene`、`mapping` 和 `timeline` 的有理帧率一致。需要推进多帧预览时在 `frames` 与 `timeline` 中按需选其一，输出视频时给完整连续 `timeline`。
- **线色叠合与辉光景深**：三渲二镜头分别接入 `Beauty`、`Line` 与 `BeautyLineInteraction` 通道，按 `Combined = Line + Beauty - BeautyLineInteraction` 做不透明相关线色重建，并独立控制线色、线浓度、柔和辉光与景深。调完单帧后抽查连续帧，确认线稿边缘、亮部辉光和背景雾效在运动中保持稳定。
- **接手人工手调**：用户在 Blender 窗口里改完节点后，先显式存成新快照并重算 SHA，再运行 `compositing inspect` 或点名 `update`，让手调结果稳妥接续下去。

```powershell
& $ctl --jobs-dir $jobs --compact compositing run $src `
  --expected-sha256 $sha `
  --manifest $manifestJson `
  --resources $resourcesJson `
  --preview $previewJson
```

长作业提交后用 `job wait <job_id>` 等待终态。色彩编码、Movie 输入、HDR10 `encode` 与 `alpha_layout.py` 细节见 [色彩、序列、模板与批量](references/color-and-templates.md)。

## 第四步：复用模板与做多方案对比

同一套调色或线色配方要跑多个镜头，先沉淀成模板再批量套用，比每个镜头手工重搭省力且画风统一。

- **保存与套用模板**：从验收通过的正常产出里运行 `compositing template-save --params <json>` 导出模板和显式插槽。换新镜头时运行 `compositing template-run --params <json>` 绑定新工程、新素材、参考帧和 `resources`，先出小样看图再跑全序列。
- **多组参数做 `study`**：拿不准辉光强度、色温或暗角风格时，用 `compositing study --params <json>` 一次跑出有限几组静态候选，连同基线并排对比，把最终选择权留给看图环节。
- **多镜头走 `batch`**：同一批镜头统一跑合成时用 `compositing batch --params <json>`。成员各自独立记账，单个失败项单独排查，已通过成员保持完整闭包供续跑复用。

## 第五步：现场深度补光与工作副本接回

素材本身光照扎实、只需补氛围或局部轮廓光时，优先以全画面环境光色与柔和补光为主，保留原本可信的明暗骨架。

1. **准备或复用深度包**：已有深度与法线数据时用 `compositing depth-prepare` 整理，新 RGB 图片估深用 `compositing depth-estimate`，随后用 `compositing depth-inspect` 冷验。调灯阶段直接复用已通过的深度包，省去重复估深。
2. **现场窗口交互调灯**：打开附接的预览窗口后，用 `compositing session-live` 执行 `preflight`、`bind`、`display`、`anime`、`aim-distance`、`final` 与 `save-copy`，把展示状态、灯距和最终修订收进工作副本。
3. **按修订号读图与离线另存**：用 `compositing depth-control` 的 `inspect`、`submit`、`read` 和 `stop` 按确切修订号读取补光预览、诊断图和线性 EXR。拿到用户已保存的补光 `.blend` 快照后，用 `compositing preview-copy --params <json> --output <blend>` 按场景和 `expected_owner` 另存可冷开的控制工程副本。
4. **有限候选自动对比**：需要在已有深度包上一次跑完几组预设补光候选并自动停机，使用 [有限深度补光 study 辅助脚本](references/finite-relight-study.md)。

完整的深度补光与现场接回命令见 [深度补光与现场会话](references/depth-relight-live.md)。

## 第六步：无参数标签对照验收并交下游

数据报告和像素均值用来排错，画面好不好必须亲眼看图拍板。

1. **盲看全图与中景**：先隐藏参数标签看成图，判断曝光、色温、立体感与氛围。
2. **同视图前后对照**：把原图、`baseline` 与 `result` 同视图并排对比，再放大到 100% 裁切查边缘、Alpha 轮廓、接触阴影、高光和噪点。序列镜头额外播放连续帧排查闪烁。
3. **核对回执与冷重开**：核对 `$LASTEXITCODE`、返回 `ok`、源工程保护与独立解码，再对最终 `.blend` 候选跑一次 `compositing inspect` 冷重开确认外链完好。

## Blender 5.3 场景效果栈

整幅结果的场景效果使用原生 **Compositor & Effects**，先从 `discover --product compositing` 核对本机候选，再提交 `production.run`，`domain` 取 `compositing`。先读原生栈，按效果实例名增加、移除、插入、换序或旁路。调参数按接口 socket identifier，分别指定预览和渲染开关。同组多实例有独立控件。

可引用 Blender Essentials 具名效果或项目本地节点组，也可用多个现有节点构造资产并暴露控件。删除前读取驱动依赖回执，效果仍被原生驱动变量引用或删除会使数字索引改绑时返回冲突。修改后对照邻项手调、求值顺序，两项开关分别检查。像素验证使用同机位同帧的场景线性渲染，现场预览按原生 Viewer 读回。不同工程可一轮并行；同场景的栈动作按顺序传候选。本机候选调用（`work/audit/<batch>/`）

## 交给下游

向用户审看或剪辑部门交付时给齐四样东西，并分别写明技术验收、画面观察与用户确认状态：

- 保存好的可编辑合成工程副本（路径与 SHA256）。
- 按镜头编号命名的成片序列、EXR 或视频，标明编码、色彩空间、帧率与起止帧。
- 隐藏参数标签的前后同机位对照图（含整体与 100% 局部裁切）。
- 完整报告路径与模板或恢复引用。

单镜头和静帧在这里完成**审看②（最终帧）**；多镜成片交剪辑部门随**精剪**一起看。

## 例子：给三渲二镜头叠合线稿、调辉光并套模板

接到任务：「给 `work/shot04/shot04_render.blend` 的 24 帧三渲二序列叠合独立线稿、压暗背景并加柔和辉光，定稿后存成模板给 `shot05` 复用。」

1. **摸底**：建 `work/audit/<batch>/`，算出源工程与 `Beauty`、`Line` EXR 的 SHA256。跑 `compositing describe` 核对字段，再用 `compositing inspect` 查目标 `Scene` 与已有节点。
2. **核对通道**：确认输入为线性 EXR、帧率 `24/1`、起止帧 `1..24`，遍历 subimage 核对 `Combined`、`Line` 与 Straight Alpha。
3. **先跑 3 帧小样**：写好 `manifest.json`（线色叠合 + 柔和 `glare` + 背景微压暗）与 3 帧 `preview.json`，跑 `compositing run`。盲看同视图 A/B 对比，并放 100% 裁切查眼部与线稿边缘。
4. **出全序列并冷重开**：确认边缘干净后，换完整 24 帧 `timeline` 跑正式合成与审片视频，播放核对帧间稳定，再对候选 `.blend` 跑 `compositing inspect` 确认外链完好。
5. **存模板与交付**：用 `compositing template-save` 导出模板供 `shot05` 用 `template-run` 套用，把合成工程、24 帧成片序列、前后对照图与报告交剪辑部门并提交审看。

## 参考

- [色彩、序列、模板与批量](references/color-and-templates.md)
- [深度补光与现场会话](references/depth-relight-live.md)
- [有限深度补光 study 辅助脚本](references/finite-relight-study.md)
- [契约文档、Wiki 与历史实证索引](references/sources.md)
- 本技能附带脚本：`scripts/alpha_layout.py` · `scripts/session_study.py`

<!-- runtime_identity: daf85c3c01c8d1d6730f8f0075e8f7ec194341e153b7dfd92690d15b1645fcd9 -->
