# 普通Normal导入与局部深度编辑

depth-prepare1.1增加normal.method=import_geometry，旧1.0保留。先describe的depth-prepare `--param normal`。仅正axial_z/smaller_nearer/scene_unit、explicit validity、normalization none、PERSP K。同域C-order signedFLOAT32HW3NPY和独立HWbool/FLOAT32binary Normal-validity；有效长度误差≤1e-5，无效精确0、nv非空且为depth-valid子集，全图finite，无隐式normalize/翻面/采样。

normal声明encoding signed-float32-XYZ、space、proper3×3 world_to_camera、surface_relation、source、fx/fy/cx/cy、max_relative_jump和depth_edit_policy。world_Xright_Yforward_Zup为Blender世界轴，按N@R.T转相机；camera_Xright_Yup_Zbackward要求identity。R正交det+1，拒反射/scale/shear。相机看局部-Z。

declared_external_normal、K/R均caller声明，producer_verified=false。geometry_surface与shader_surface分别解释；Cycles Normal可能包括平滑、bump、贴图及样本平均。DenoisingNormal、切线纹理/显示PNG不能直接冒充几何。非unit原Pass须保留raw，上游明确处理及有效域，导入器仍拒未处理数据。

局部策略rederive_affected_from_axial_z：按最终float32scalar差异扩张cross，未affected exact保持，affected仅在原nv和合法差分域交集重建，不晋升无效。no-op/灯/遮罩/粗糙度不损失Normal；深度改变域的shader微法线会丢失，报告hybrid origin/affected/rederived/invalidated。

metric消费者K须exact一致；模型proxy与shaderNormal不同的照明比较不能直接称纯模型几何误差。源AgXPNG对应线性EXR也不是Beauty HDR恢复。2K数值/成图、GUI新bind、3+1正式作品、强换光和序列分别验收，见[矩阵](validation.md)。
