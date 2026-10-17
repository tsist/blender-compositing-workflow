# RGB自动估深

`compositing.depth-estimate` 为独立experimental Host操作。先describe的 `--operation depth-estimate --param budget`，再按真实Schema写请求。只支持64..2048单张PNG8RGB/全不透明RGBA、display_sRGB_PNG8、明确domain/input_provenance/runtime_profile/derived/budget/resources。

固定DAV2 Large、官方源码与预处理518/lower_bound/multiple14、已批准14包/native Python/CUDA0 FP32；关闭autocast/TF32，无下载、安装、CPU/MPS/半精度或其它模型fallback。输入max_pixels≤4194304，native max_tensor_pixels≤1048576，必须覆盖实际预处理tensor。父timeout≥raw worker budget+90；准入与模型前向成本分列。

模型输出保留原图域float32 raw；derived仅为后续relative prepare配方，不改变模型raw键。调整派生参数重新prepare，调灯复用成功bundle。只有estimate父succeeded并完整raw读回后消费精确depth-prepare-params，再由独立prepare和cold inspect完成链。estimate本身不发布depth-bundle。

Large权重CC-BY-NC-4.0与源码Apache-2.0分别适用；项目GPL不授予权重商用权利，见[许可](licensing.md)。固定profile不随包提供，新机器不可假定准入。[依赖](dependencies.md)区分Host/GPU/GUI。数值闭环不证明metric、confidence、albedo或每张新图几何质量；正式作品与序列分别验收。
