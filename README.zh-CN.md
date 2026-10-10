# Compositing Workflow 合成工作流

[English](README.md)

用于可编辑合成节点、受保护磁盘快照、实际图像输出和可恢复 CLI 作业的 Blender 插件及配套代理技能，当前为实验发布。

**插件 0.4.0 · 匹配 blenderctl 快照 0.63.0 · GPL-3.0-or-later。** 本机限定验证使用 Windows、Blender **5.2.1 LTS / build 9e2066aef7ef**。其他 Blender 版本和平台需要另行验证。

## 能力

- 管理原生合成节点组，明确 create/update/adopt/detach，保留外部节点并报告手改冲突。
- 接入图片/EXR、Render Layers，使用任务组件或可扩展节点图，显式绑定色彩、Alpha、资源与 SHA。
- 处理有限图像序列、数值参数动画、外部 BoxMask 跟踪结果和严格声明的 SDR Movie。
- 导出配方/模板、消费新输入、逐项批处理、有限静态候选比较，以及取消/超时后的身份绑定恢复。
- 输出可编辑 `.blend`、前后 PNG 和线性 EXR、显式 SDR 视频预览与技术 HDR10/PQ 编码。

原生插件提供节点图代码与合同，注册时没有专用面板或操作器。完整执行、文件保护、渲染和验收由匹配 CLI 驱动，手工调整使用 Blender 原生节点编辑器。Movie 解码和 HDR 编码需要独立提供运行时，见 [用法](docs/USAGE.md) 和 [依赖](docs/DEPENDENCIES.md)。

## 安装与使用

从匹配版本 Release 获取原生 ZIP，在 Blender **Preferences → Extensions → Install from Disk** 安装。自动化制作使用本仓匹配 CLI 快照。仓库不包含 Blender、Python、编解码器或第三方 Python 包。

```powershell
$env:BLENDERCTL_ROOT = (Get-Location).Path
$env:BLENDERCTL_PYTHON = '<实际 Python.exe 的绝对路径>'
$env:BLENDER_PATH = '<实际 blender.exe 的绝对路径>'
./blenderctl.ps1 --version
./blenderctl.ps1 compositing describe
./blenderctl.ps1 compositing describe --operation run --schema
./blenderctl.ps1 --blender $env:BLENDER_PATH --jobs-dir (Join-Path $env:BLENDERCTL_ROOT 'runtime/compositing-jobs') --timeout 1800 --async --compact request '<请求 JSON 的绝对路径>'
```

全局参数放在子命令前；请求绑定实际绝对路径与 SHA-256。提交、status/result/wait/cancel 始终使用同一显式 jobs-dir。检查 supervisor 终态与完整带 SHA 报告，compact 只作摘要。

七个公开操作为 `compositing.run`、`inspect`、`encode`、`template-save`、`template-run`、`batch` 和 `study`。通过实时 `compositing describe` 发现字段。进一步阅读 [技能安装](docs/SKILLS.md)、[领域合同](docs/CONTRACT.md) 和 [验收范围](docs/VALIDATION.md)。

## 验收与分发范围

本仓保持构成合成身份的 **177 个 runtime 文件**原始字节，实现身份为 `9566cec1c2a9bf6db34c3085d964806b8ce7bafed1e0ae145bbb5259d655e629`。另带原字节 Geometry Nodes Workflow 源码支持包（7 个 Python 文件与 manifest）并独立记录身份：合成 run 通过兼容 CLI 导入其保存候选所需的保留数据块辅助函数。此源码导入无需在 GUI 启用第二个插件。支持包及其他领域模块的存在不代表完整几何节点等制作效果获得本插件认证；此次分仓没有引入子模块或重构运行时。

本机代表证据覆盖 2K/4K 静帧、Cycles/Eevee 来源、外部融合、新 sRGB 留出输入、有限时序样例、模板、批量、study、取消/超时恢复。M1–M4 证据继续归属各自原实现身份。当前公开封包和自有示例执行另行记录，见 [验收范围](docs/VALIDATION.md)。

HDR 文件/色彩/元数据技术检查、真实 mastering、HDR 目标设备观看、AI 视觉观察和用户审美认可分别记录。文件存在、插件注册或 Schema 通过不单独证明作品完成或全部 HDR 认证。

仓库排除生产资产、原验收图、私有 `.blend`、完整本机审计作业、私有 Wiki、工作任务记忆、凭据及外部运行时。公开内容提供验收摘要与可独立安装的技能引用，见 [许可范围](docs/LICENSING.md)。
