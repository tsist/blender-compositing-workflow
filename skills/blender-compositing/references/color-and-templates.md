# 色彩、序列、模板与批量

本页细化日常节点合成里的色彩管理、序列与视频输入、HDR10 编码、模板复用、批量对比以及透明底产品定位脚本。

## 色彩管理与显示编码

1. **线性 EXR 与显示编码分流**：
   - 多层线性 EXR 读取时遍历全部 subimage，按真实层名绑定，主图对应 `Combined`。输出 32-bit float EXR 时按实际 `output_color_space` 和元数据解释。
   - 已经显示编码的 sRGB PNG 放进 `AgX` 场景会再经过一次视图映射。目标为保留原图外观时，先在独立工作副本里把视图设为 `Standard` / `sRGB`、`None` look、曝光 `0`、伽马 `1`，再套合成配方，源文件保持原样。
2. **Alpha 与背景铺底**：
   - 检查 Alpha 轮廓时直接看 PNG 或 EXR 原图，JPEG 和缩略拼图只看 RGB 整体效果。
   - 背景明确需要实底时，在 `Fit`（`Extension X/Y = Extend`）之后、阴影与叠层之前加 `Set Alpha`（`Replace Alpha = 1`）；需要保留透明背景的资产保持原 Alpha 通道。
3. **引擎与去噪口径**：
   - `preview` 里 `engine=SOURCE` 沿用源工程引擎，设备项按需显式写明并记录实际使用的设备与回退状态。
   - 后台预览关闭 Cycles 原生去噪时，节点去噪直接接入 `Image` 及已启用的 `Denoising Albedo` / `Denoising Normal`，缺失辅助通道先回三维场景开启重渲。

## 序列、Movie 输入与外部跟踪

1. **图像序列（`image_sequence`）**：
   - 固定 `reference_frame` 作为基准帧，逐项写明每帧的 `file`、SHA256、`source_frame` 与 `ONE_TO_ONE` 映射。
   - 把原始 `source_frame`、场景 `scene_frame` 和从 1 起算的 `stage_index` 分开记清。
   - 保持 `Scene`、`mapping` 和 `timeline` 的有理帧率一致，帧范围连续完整；需要多帧预览时在 `frames` 与 `timeline` 中选定其一，输出视频时给完整连续 `timeline`。
2. **显式 SDR Movie 输入**：
   - 写明原视频 `file`、SHA256、完整 `1..N` 的 `ONE_TO_ONE` 映射、`interpretation`（`method=BT709_OETF_INVERSE_V1`、`coded_orientation=AS_CODED`、`audio=IGNORE`）以及 `ffmpeg` / `ffprobe` 路径与 SHA256。
   - 视频输入采用逐行扫描、恒定帧率、SAR 1:1、明确 BT.709 色彩标记的 H.264 `yuv420p` 8-bit 源。解码产物按独立线性 RGBA 32f EXR 与原始帧号分开记录。
3. **参数动画与外部跟踪**：
   - 关键帧轨道写入明确可动画的数值属性、匹配维数以及 `LINEAR` 或 `CONSTANT` 插值。
   - 外部跟踪只读取带 SHA 绑定的稠密 JSON（左下角归一化坐标、弧度制），映射到 `BoxMask` 的位置、大小与旋转。

## SDR 视频与技术 HDR10 编码

- **SDR H.264 审片视频（`SDR_MP4_H264`）**：在请求里给出明确的 `ffmpeg` 和 `ffprobe` 路径与 SHA256。选用 `COMPOSITE_BLACK` 会在显示域合黑底；写完后核对单视频流、分辨率、总帧数、有理帧率、PTS 与 BT.709 CICP 标记。
- **技术 HDR10 编码（`compositing encode`）**：作为独立主机后处理步骤运行，先用 `compositing describe --operation encode --schema` 查清字段，再执行：

```powershell
& $ctl --jobs-dir $jobs compositing encode --manifest $encodeManifest
```

在清单里写明 `Standard` 或 SHA 绑定的 `AgX HDR1000`、参考白点映射、Alpha 处理与虚拟母版参数。交付时把技术码流校验、画面观察和目标 HDR 设备观看分开登记。

## 模板复用、批量与参数 study

1. **保存与套用模板**：
   - 从验收通过的 `compositing run` 报告导出配方和显式插槽：
     ```powershell
     & $ctl --jobs-dir $jobs compositing template-save --params $saveParams
     ```
   - 换新镜头套用时提供新工程、SHA、上下文、源绑定、`resources` 和 `preview`：
     ```powershell
     & $ctl --jobs-dir $jobs compositing template-run --params $runParams
     ```
   - 模板中断后需要续跑时，把外层 `template-run-report.json` 作为恢复入口传入，保留完整祖先闭包。新镜头套完模板后先看小样，再决定是否跑全序列。
2. **多镜头批量（`compositing batch`）**：
   - 写好共享输入和成员清单后运行 `compositing batch --params <json>`。
   - 单个成员失败时其余成员继续跑完，汇总状态需核对具体通过与失败清单；修好问题项后原请求续跑可复用已通过成员。
3. **多候选对比（`compositing study`）**：
   - 写明几组待比参数与基线配置后运行 `compositing study --params <json>`。
   - 生成后把原图、基线和各组候选放在同视图下盲看挑选，由人工拍板最终方案。

## 直立透明底产品定位脚本

处理正方形 RGBA、带透明留白和不透明主体的单个直立产品时，可用 `scripts/alpha_layout.py` 只读测量 Alpha 边界框，算出对齐指定地平线的 `Transform` 参数。

用工作区内置的 Blender Python 运行，传入绝对路径与真实 SHA256：

```powershell
& $blenderPython './.agents/skills\blender-compositing\scripts\alpha_layout.py' `
  --image $imgPath `
  --expected-sha256 $imgSha `
  --canvas-width 1024 --canvas-height 1024 `
  --target-height 0.72 --floor-y 0.14
```

拿到返回的平移与缩放值后，接在 `RenderSize Fit` 后面，并把接触阴影锚定在同一 `floor-y` 高度。`alpha_threshold` 用于测量边界框定位，完成后打开全图和 100% 脚底裁切核对接触感。透明玻璃、已自带大面积阴影、非直立或多主体素材改用人工构图定位。
