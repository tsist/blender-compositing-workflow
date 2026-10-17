# Blender 合成工作流

实验性预发布 **0.8.0**：两条具名原生1080p/24fps/full120稳定补光作品及用户连续观看已通过；两条强换光实验美术拒收，仅推荐稳定版。准确范围、保留失败与未验边界见验证矩阵。


[English](README.md)

实验性 Compositing Workflow 原生扩展 **0.8.0**、兼容 CLI 源码 **0.75.0**、唯一可移植技能 **0.8.0**，GPL-3.0-or-later。已验本机基线为 Windows、Blender5.2.1 LTS/build `9e2066aef7ef`，其它机器、版本与平台需另验。

支持可编辑合成图、Image/Render Layers、有限序列与显式SDR Movie、模板/批量/静态候选、受保护工程与技术HDR输出。新增深度准备/冷读、固定环境RGB估深、补光、GPU热会话以及2–120帧镜头序列。全部13操作通过 `compositing describe` 发现，详见[使用说明](docs/usage.md)与[深度序列](docs/depth-sequence.md)。

原生扩展提供 Relight 侧栏和CLI源码根偏好；先在外部CLI建立活会话，再setup/bind真实ready。它不安装环境或启动模型。工程重开后须建立新session并显式rebind。原生包恰好11成员，技能包仅一个 `blender-compositing`，源码包保留同字节技能。[安装与角色](docs/SKILLS.md)、[依赖](docs/dependencies.md)、[热会话](docs/relight-session.md)分别说明。

命令使用显式 `BLENDERCTL_ROOT`、`BLENDERCTL_PYTHON`（已批准bundled Python）与实际Blender路径；Host、固定GPU环境、GUI是三个角色。GPU profile没有随包发行，不能通过搬目录或伪造精简profile取得新机器准入。不会自动下载、安装或降级guard。

运行时精确集合为213文件，aggregate `ae89b1e85145c2d2385bc7db312557aee9e44499108299dc18dac7b48cd34370`；Geometry持久化支持8源另记，不据其它领域源码存在宣称整个领域可用。完整逐成员SHA/大小、Schema和公开说明记录在PUBLICATION；构建输出三个独立包及各自member index。

[验证矩阵](docs/validation.md)区分历史证据、最终包CPU检查、实际运行、视觉与用户认可。具名真实1080p/120帧稳定整片、最终导出helper运行及GUI live已按矩阵完成有限验收；强实验与额外AI解析失败保留。静态绿色或文件存在不能提升为作品通过。

发行物不含模型、权重、venv、第三方二进制、生产素材、私密profile/回执或个人配置。DAV2外部源码Apache-2.0与Large权重CC-BY-NC-4.0分别适用，项目GPL不授予Large商用权利。见[许可](docs/licensing.md)与[NOTICE](NOTICE.md)。
