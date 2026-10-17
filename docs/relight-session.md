# GPU热会话与原生Relight客户端

`compositing.depth-session` 是独立Host作业，不进DAG、不重估深、不安装环境。先describe的 `--param relight`，给完整成功bundle、固定GPU profile和显式预算。preview_divisor为1/2/4且整除原域；preview最近邻采样，final返回原尺寸。父timeout≥lifetime_seconds+relight.budget.timeout_seconds+90，仍需容纳实际准入/收尾。

先用外部CLI启动一次会话，只消费真实running父的session-ready.json。原生扩展0.8提供Relight侧栏和源根偏好：选择包含tools/blenderctl的匹配根，或BLENDERCTL_ROOT，源码相邻树为最终fallback。显式非法根不会静默回退。切换根后重启Blender以避免全局模块来源冲突；已有异源模块拒绝而不驱逐。

在专用新factory GUI可运行源码包 `tools/blender/relight_preview_launch.py`：Blender参数为`--factory-startup --disable-autoexec --python <absolute-script> -- <absolute-session-ready.json> --audit-output <new-absolute-receipt.json>`。保护现有用户工程；receipt父目录须存在。启动器只建立客户端，不启动GPU。

原生setup/bind真实ready后，灯G移动，R改SPOT/AREA/SUN方向；POINT旋转锁定，高度用Z，原生Light Watts保持0。尺寸、半径、锥角/羽化、SUN角宽按当前合同；独立AREA roll未实现。final输出不可变revision，保存新工程副本须保留或打包图依赖。重开先建新session再显式rebind；closed ready不是live authority。

一个active+最新pending，session/incarnation/cache/rev/UTF8参数SHA全部匹配才显示passed。ESC/Undo产生新revision，旧图不能代表新参数。局部最多8有序椭圆/矩形，可G/S/R；显式Apply才生成新代际，待应用参数拒绝final。diffuse/highlight独立restrict/attenuate，line保护、depth weighted affine、roughness/set及receiver/caster按有版本recipe。原scalar/raw不改；relative正offset近、metric正offset远，越界拒绝。只重建实际改变cross邻域，不晋升无效Normal；见[Normal](imported-normal.md)。

局部roughness只控制新增Blinn高光；单一接收plane及可见深度半空间近似不恢复隐藏几何/旧影/GGX。先检查receiver是否跨主体，再启用projection并看signed贡献。final才由Host写scene_linear_Rec709/straight FLOAT32ZIP EXR，不裁负值/>1；preview无EXR。打包PNG不等于嵌入EXR。

停止、唯一窗口关闭或读新文件停止timer并请求stop；父正常closed且succeeded及全部成员/worker退出闭合后才作终稿authority。预制有限动作、一次执行stop、离线选immutable revision见[finite study](finite-relight-study.md)。热交互、Apply、final、冷ready与postguard成本分别记录；本机历史速度不推定新设备或人工物理响应。当前最终GUI/live验收见[矩阵](validation.md)。

2026-10-17 native0.8.0具名有限全链已通过：偏好保存/重启→真实setup→原生transform→局部Apply→匹配2048² PNG/FLOAT32 EXR final→stop→父succeeded→Host及独立保留句柄确认实际worker退出/关闭→save；fresh GUI重开无自动绑定、显式新session rebind/final通过。两次4图完整解码，PNG文件SHA相同，EXR仅DateTime头不同、float32像素完全相同。首次无合法area上下文的rebind harness崩溃保留，独立上下文探针与一次窄重试通过，产品源码未改。物理鼠标手感、全部控件、跨机、视频和人工审美不在此资格内。
