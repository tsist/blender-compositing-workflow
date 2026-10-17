# 单批深度补光

`compositing.depth-relight` 消费公共succeeded depth-prepare不可变bundle，estimate raw不能替代。describe的 `--param config|source|masks|compute|budget` 分别发现字段。POINT/SPOT/AREA/SUN为2.5D后期相对贡献，不是Blender瓦数/物理再渲染。

config.frame须与父bundle的metric perspective K或relative heightfield精确匹配，不通过换frame把艺术深度变米制。只消费父已资格化Normal。bundle_RGB读取PNG显式UnassociatedAlpha和inverse-sRGB；scene_linear_straight_override为同域float32RGBA NPY/EXR、Rec709、parent_RGB和来源，不自动转换其它色域/resize/反演albedo。原影保持。

light/highlight/line为独立同域float32[0,1]mask，null分别全1/全1/全0；没有自动材质/线稿识别。line只保护新增贡献。CPU_NUMPY或固定CUDA0_FP32显式选择，无fallback。父timeout≥worker预算+90；冷GPU准入成本与内核分列。

产物包含线性straight RGBA NPY、ZIP FLOAT32 EXR、总及逐灯diffuse/specular/visibility/delta；显示PNG末端Standard/sRGB裁切，浮点负值/>1和Alpha保持。完成后核父终态、全部member SHA/数值与实际图像。单批enabled projection明确UNSUPPORTED，受控plane/热局部编辑使用[session](relight-session.md)。
