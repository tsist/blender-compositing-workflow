---
name: blender-compositing
description: 使用Compositing Workflow与匹配CLI制作、修改和检查可编辑合成图、静帧/有限序列、显式SDR Movie、技术HDR、模板/批量/候选及实验性深度补光；不替代跟踪求解或视频剪辑。
---

# Blender合成与深度补光

以实际图像及可继续编辑工程为交付。匹配addon0.8.0、CLI0.75.0、skill0.8.0，本机基线Windows/Blender5.2.1LTS build9e2066aef7ef；runtime aggregate `ae89b1e85145c2d2385bc7db312557aee9e44499108299dc18dac7b48cd34370`。历史/当前范围与未验项先按任务读取[validation](references/validation.md)，不把CI/Schema/注册成功当成运行或作品通过。

设置实际绝对BLENDERCTL_ROOT指向匹配源码包；BLENDERCTL_PYTHON为已批准Host bundled Python，Blender GUI与固定GPU环境另有角色。先读[usage](references/usage.md)、[dependencies](references/dependencies.md)及[contract](references/contract.md)。本技能不依赖作者Wiki/记忆插件/另一个技能。移植技能不构成GPU profile移机资格；不伪造profile、安装依赖或放宽guard。

```powershell
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') --version
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe --operation run --param preview
```

13操作：`compositing.run`, `compositing.inspect`, `compositing.encode`, `compositing.template-save`, `compositing.template-run`, `compositing.batch`, `compositing.study`, `compositing.depth-prepare`, `compositing.depth-inspect`, `compositing.depth-estimate`, `compositing.depth-relight`, `compositing.depth-session`, `compositing.depth-sequence`。create/update/adopt/detach是run中manifest.operation。按所选操作查字段/Schema；全局参数在子命令前。读compact的状态/错误/完整报告引用，再有目的读取报告，不一次展开所有深层对象。保持同一jobs-dir和job ID，有界wait返回running不重提。

从源快照/Scene/ViewLayer、资源/色彩/Alpha/时间与用途获取信息；不覆盖未保存GUI。独立可恢复工作副本、小样看图、最终约定质量、独立重开/解码/源与非目标保护。实际baseline只旁路主bridge，输出尺寸不会自动fit；原图与baseline/result同时看，100%检查边缘/高光/噪声/主体与接触。sRGBPNG放AgX可能二次映射，保持外观须明确独立Standard/sRGB源；EXR解释与HDR观看分别核，见[color/HDR](references/color-hdr.md)。

模板消费者/外层resume、partial batch与有限study按合同执行，不自动排名艺术最佳。cancel/timeout以supervisor终态为准；完整同身份成功闭包才复用，不改旧SHA、不承诺任意中点恢复。PNG/EXR核Alpha，JPEG/contact只供RGB看图。

选择深度路线时按需读：[prepare/cold inspect](references/depth-data.md)、[RGB estimate](references/rgb-estimate.md)、[single relight](references/depth-relight.md)、[hot session与Relight面板](references/relight-session.md)、[普通Normal](references/imported-normal.md)、[shot sequence](references/depth-sequence.md)。relative深度非metric，finite/Alpha非confidence，RGB非albedo，原影保留；深度数据通过不自动升级展示质量。

调灯复用成功bundle与热session，不反复估深/校验模型。先建立外部公共live session，再setup/bind；重开工程新建session显式rebind。局部轮廓修改须Apply后final，原始raw保留，选明确immutable final revision；closed ready不能绑定为live。先预制有限动作再启动，执行stop后离线看图，不让GPU等代理选图。

辅助：[alpha_layout.py](scripts/alpha_layout.py)只测量SHA守护、方形RGBA/opaque-core cutout并给几何定位，独立技能安装传`--project-root`；[session_study.py](scripts/session_study.py)为有限编排，先读[finite study](references/finite-relight-study.md)，冻结source-index/request/actions/解释器SHA，preflight与正式运行使用各自新短jobs/out。越过submit barrier不自动重提；必须核父终态/实际worker退出/全部成员，仍需看图与fresh工程。

序列改灯可用成功同源RGB/CUDA bundle的`reuse_raw`，全raw复用时model_load0；与partial同配方`resume`互斥，须完整公共父/成员/来源资格。序列须完整帧映射、全镜统计及真实运动源，不把小人工fixture当1080p120视觉完成。完整decode/遮挡/新露出/闪烁/拖影与用户认可分别记录。交付工程、实际图像、必要EXR/视频、完整回执/恢复引用及未验边界。Large外部权重CC-BY-NC-4.0与项目GPL分别适用，见[licensing](references/licensing.md)。

本版本具名两条原生1080p/24fps/120帧stable补光、全成员/cold/视频PTS与用户连续观看通过；两条更强换光full120技术通过但美术拒收，只推荐stable。v005独立导出helper f2a0e546…两动作preview/final/stop与29成员/实际worker退出通过；v004原CRT状态读取失败保留，使用同源审核的protocol/filesystem共享reader修复。额外Gemini JSON超时不算AI验收；不从字节/机器时间推算agent token省幅。范围与当前精确代码映射见validation。
