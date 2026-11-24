# 深度补光与现场会话

本页说明 2.5D 深度辅助补光的离线准备、热会话调灯、现场窗口接回以及离线预览副本另存。所有子命令的精确字段先用 `compositing describe --operation <op> --schema` 核对。

## 路线选择

- **素材自带扎实光照**：以全画面环境光色与柔和氛围微调为主，把可关闭的弱补光当辅助，保护原有明暗结构和主光源逻辑。
- **需要大改光影或遮挡**：直接回三维灯光与渲染部门重渲。深度半空间和单一接收平面适合局部氛围与轮廓补光，遇到复杂穿插遮挡或真实全局光照变化，三维重渲更省心。

## 第一步：准备与检验深度包

1. **已有深度图或法线通道（`depth-prepare`）**：
   - 提供 RGB、标量深度文件与 SHA256、图像尺寸域、空间解释（`axial_z` 与艺术 `heightfield` 分开声明）、显式有效域掩膜和 `resources`。
   - 需要直接导入渲染出来的相机空间或世界空间法线时，按 1.1 `import_geometry` 配方提供有符号 `FLOAT32` 法线数组、独立有效掩膜以及正确的旋转矩阵；上游先归一化原 Pass 法线再传入。
2. **从纯 RGB 自动估深（`depth-estimate`）**：
   - 先运行 `compositing describe --operation depth-estimate --param budget` 核对预算参数。
   - 输入 64 到 2048 像素的 8-bit `display_sRGB` PNG（RGB 或全不透明 RGBA）并绑定本机已配置的运行环境；消费返回的精确配方接着跑 `depth-prepare`。
3. **冷验与复用（`depth-inspect`）**：
   - `depth-prepare` 成功后，跑一次 `compositing depth-inspect --params <json>` 核对输入、产物和完整 SHA。
   - 后续调灯、换灯位或做多组候选对比时，直接复用已通过的深度包，省去重复估深。

超时设置留足余量：`depth-estimate` 父超时至少为 worker 预算加 90 秒，`depth-prepare` 至少加 30 秒，`depth-inspect` 至少 30 秒。长路径目录容易触发系统路径上限时，在工作区里选用短 `jobs` 目录。

## 第二步：离线单批补光与序列补光

- **单帧单批补光（`compositing depth-relight`）**：
  消费已通过的深度包和派生法线，确保坐标系与父深度包一致，线性覆写输入明确标注 `scene_linear_Rec709`、Straight Alpha 与 `float32`。
- **序列补光（`compositing depth-sequence`）**：
  对连续帧执行统一补光配方。只改灯位或灯强、不改原图序列时，通过 `reuse_raw` 复用已成功的原始深度包，跳过模型重算。强换光容易在连续帧里产生闪烁或色斑，优先选用稳定的柔和补光配方并播放全序列验收。

## 第三步：GPU 热会话与按修订号控图

频繁调灯位、灯强、表面粗糙度和局部受光区时，起一个 `depth-session` 热会话，一次加载常驻内存后连续出图。

1. **启动热会话**：先用 `compositing describe --operation depth-session --param relight` 核对字段，运行 `compositing depth-session --params <json>`。
2. **局部区域与投影控制**：
   - 支持最多 8 个有序椭圆或矩形局部区域，可单独控制漫反射、高光、线稿保护、深度偏移、局部粗糙度，以及接收面（`receiver`）和投射区（`caster`）衰减。
   - 拖拽轮廓只改草稿，显式执行 Apply 后才生成新数据代际；灯位、灯强、全局粗糙度与接收平面参数可在同一数据代际上热更新。
   - 叠加投影时把原图已有阴影和新增有符号贡献图分开查看，确认接收面没有误切进主体。
3. **按修订号读取与停机（`compositing depth-control`）**：

```powershell
# 查看当前会话最新配方与修订号
& $ctl --jobs-dir $jobs compositing depth-control inspect --help

# 基于已知修订号提交新参数、按精确修订号读图、完成后优雅停机
& $ctl --jobs-dir $jobs compositing depth-control submit --help
& $ctl --jobs-dir $jobs compositing depth-control read --help
& $ctl --jobs-dir $jobs compositing depth-control stop --help
```

`final` 输出包含 32-bit float ZIP 压缩的线性 Straight Alpha EXR 与预览 PNG；交付终稿时明确点名已验收的固定修订号。停机后用 `job wait` 确认父作业收尾。

## 第四步：接手现场窗口与另存离线控制副本

### 现场窗口接回（`compositing session-live`）

用户在打开的 Blender 预览窗口里手调补光时，先在主窗口显式附接会话，再用 `compositing session-live` 读写现场状态、微调参数或提交终稿。

```powershell
# 核对现场上下文与预检 SHA
& $ctl compositing session-live --session-dir $sDir --session-id $sId --operation inspect
& $ctl compositing session-live --session-dir $sDir --session-id $sId --operation preflight

# 绑定补光作业、切换原图/结果视图、微调灯距、提交原尺寸终稿并另存工作副本
& $ctl compositing session-live --session-dir $sDir --session-id $sId --operation bind --job-id $jobId --ready-sha256 $readySha
& $ctl compositing session-live --session-dir $sDir --session-id $sId --operation display --view RESULT
& $ctl compositing session-live --session-dir $sDir --session-id $sId --operation aim-distance --light-id $lightId --distance 2.5
& $ctl compositing session-live --session-dir $sDir --session-id $sId --operation final
& $ctl compositing session-live --session-dir $sDir --session-id $sId --operation save-copy --output $copyBlend
```

常用操作说明：
- `inspect` / `preflight`：拿回当前上下文校验值与绑定所需的 `ready-sha256`。
- `anime` / `display` / `aim-distance`：写入原生控件、切换 `ORIGINAL`/`RESULT` 或沿当前方向调整 `SPOT`/`AREA` 灯距。
- `final`：按当前控件与已应用区域提交原尺寸终稿；随后用 `compositing depth-control read` 按修订号取回产物，再 `stop` 并读取作业结果。
- `result`：传入同一个 `--request-id` 恢复挂起中的操作。
- `detach`：解除附接，让用户正在使用的 Blender 窗口保持原样运行。

### 离线快照另存（`compositing preview-copy`）

拿到已经保存下来的补光 `.blend` 快照，需要抽出指定场景和作者的控制工程并保留外链与三态（当前、已应用、已展示）时，运行：

```powershell
& $ctl compositing preview-copy --params $copyParamsJson --output $outBlend
```

`$copyParamsJson` 里写明 `file`、`expected_sha256`、`context`（`scene`、`view_layer`、`frame`）和 `expected_owner`（`relight_preview_owner_v1` 的十六进制 UUID）。如需顺带调整局部区域草稿，在 `region_edits` 里按顺序列出 `add`、`edit`、`toggle`、`remove` 或 `cycle`（使用全图归一化坐标）。这些草稿改动会在下次绑定到活预览会话并执行 Apply 后生成新修订。
