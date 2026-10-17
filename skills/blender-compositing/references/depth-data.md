# 深度准备与冷读

`compositing.depth-prepare` / `compositing.depth-inspect` 为独立experimental Host操作，不进DAG。先 `compositing describe --operation depth-prepare --param normal` 或 `--schema`。公共封套为schema_version1.0、command及params，连字符命名，严格JSON与运行时语义检查继续生效。

prepare消费现有RGB、NPY/EXR scalar、解释、独立validity、有序edits、normal配方和全部FILE资源。metric axial_z只允许smaller_nearer/scene_unit/none normalization；relative score只允许unitless/percentile normalization和heightfield或none。原RGB/Alpha/raw保持，派生副本及独立normal validity另存。finite/Alpha和艺术全帧声明均不是confidence，模型proxy不是物理几何。

inspect精确字段为depth_inspect_version1.0、bundle FILE和resources，不加隐式budget。冷读完整成员、输入与公共父authority，不重新准备或修正。只有父succeeded/exit0/result.ok及完整源码/产物/身份闭合才可消费；partial和文件存在不成立。

prepare父timeout≥budget.timeout_seconds+30；inspect父timeout≥30。RAM/VRAM硬限制未资格化。取消/timeout保留partial，不使它成为成功bundle。后续调灯消费已完成bundle，不重估模型。普通Normal导入见[导入合同](imported-normal.md)，RGB估深见[estimate](rgb-estimate.md)。
