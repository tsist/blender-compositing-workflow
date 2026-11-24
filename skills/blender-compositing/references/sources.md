# 契约文档、Wiki 与历史实证索引

本页集中存放合成部门的领域合同文档、共享 Wiki 条目、历史版本检查点与审计证据路径，供溯源或排查疑难时按需查阅。日常实操直接按 [SKILL.md](../SKILL.md) 与当前 `blenderctl.ps1 discover --product compositing` 执行。

## 项目领域合同与启动入口

- `合成工作流领域合同`
- `会话与预览交接指南`
- `补光会话控制交接指南`
- `GPU 热预览与画面拖灯`
- `深度准备与读取`
- `RGB 公共估深`
- `深度补光公共消费者`
- `普通法线导入与深度编辑`
- `深度补光序列`
- `独立工厂 GUI 补光预览启动入口`

## 共享 Wiki 知识条目

- `references/blender-compositing-52-wiki.md`：合成知识总入口
- `concepts/blender-compositing-color-alpha-pass.md`：色彩管理、OIIO 直通 Alpha 读取与去噪通道说明
- `procedures/blender-compositing-still-quality-gates.md`：静帧盲看与质量门禁方法
- `references/blender-compositing-practice-source-review.md`：实战来源复核
- `procedures/blender-compositing-execution-recovery.md`：执行恢复与等值数据读取方法
- `procedures/blender-compositing-hdr10-pq.md`：技术 HDR10 / PQ 编码参数说明
- `procedures/blender-depth-relight-data-and-preview-contract.md`：深度准备与补光数据契约
- `procedures/blender-depth-relight-gpu-hot-preview.md`：GPU 热预览操作与实测记录
- `procedures/blender-depth-relight-imported-normal.md`：普通法线导入与局部深度编辑
- `concepts/blender-depth-relight-surface-controls-and-controlled-projection.md`：表面粗糙度控制与受控投影说明

## 关键审计与实证目录（历史查溯）

- **Blender 5.3.0 公共发现与椭圆区域保存复验**：
  - `B110 产品实测`
  - `B28 椭圆区域回执`
  - `Scene-Post 能力范围地图`
- **2026-11-06 旧实验分支清理记录**：
  - `清理与保留范围报告`（该报告记录 2026-10-25/26 补光实验后续分支与旧生产目录 `pseq17-v001` 的归档清理边界；当前通用合成、插件源码与活跃任务继续保留）
- **历史 5.2.1 阶段实证留档**：
  - 基础合成与模板/批量迭代：`2026-10-11 实战审计`
  - 120 帧序列独立验收：`D1 集成复核`
  - RGB 公共估深与单批补光：`估深交付` · `补光交付`
  - 局部编辑、受控投影与热 EXR 回收：`局部编辑交付` · `投影交付` · `EXR 与进程回收交付`
  - 有限补光 study 辅助脚本与原生 GUI 复验：`study 实证` · `原生 GUI 评审` · `独立读回报告`
  - 2026-10-25/26 环境光优先实验分支已按上文 2026-11-06 清理报告归档清理，原目录 `work/audit/<batch>/` 与 `pseq17-v001` 已移除。
