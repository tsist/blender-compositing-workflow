# 深度补光序列

`compositing.depth-sequence` 是 CLI 0.75 的 experimental 公共操作，处理同一镜头的 2–120 个有序帧。create、inspect 和恢复都走该命名空间；JSON 封套固定为 `schema_version: "1.0"`、`command: "compositing.depth-sequence"`、`params`。它使用独立公共作业，不进入 pipeline 的 ALLOWED DAG。

完整 request Schema `docs/cli/schemas/compositing-depth-sequence-request.schema.json` 的 `params` 直接导出自当前合同。Schema 检查结构；`protocol.validate` / `normalize_params` 继续检查帧映射、资源覆盖、CG/RGB 组合、精确整数、工作量等语义。SHA、文件数值、模型准入、成功父作业与实际进程回收在运行时检查。仅通过 JSON Schema 不代表可以运行或消费。

## 输入、时间和预算

create 必填字段为 `depth_sequence_version`、`mode`、`shot_id`、`fps`、`domain`、`source`、`frames`、`normal_source`、`max_relative_jump`、`statistics`、`config`、`compute`、`resume`、`budget`、`resources`。首次创建用 `mode: "create"`、`resume: null`；可选 `reuse_raw` 默认 null，完整 raw 改灯复用见后文。`config` 沿用有版本的补光内核合同，最多 8 灯；当前序列拒绝启用受控投影。

| 字段 | 当前要求 |
|---|---|
| `fps` | `{"numerator":24,"denominator":1}` |
| 每帧映射 | `stage_frame=i`，从 0 连续；`source_frame`、`scene_frame` 各自连续且唯一；`time={"numerator":i,"denominator":24}` |
| 120 帧时长 | 5 秒，末帧采样时刻 119/24 秒；不能把其他帧率直接重标为 24fps |
| `domain` | width/height、`pixel_aspect:[1,1]`、`origin:"top-left"`、`pixel_center:[0.5,0.5]`、`row_direction:"down"`、`column_direction:"right"`；无隐式缩放、裁切或配准 |
| 尺寸 | CG 边长 4–2048；RGB 模型边长 64–2048；单帧最多 4194304 像素 |
| `budget` | `max_pixels`、`max_total_pixels`、`timeout_seconds`；全镜像素数必须覆盖全部帧，worker 时间为 1–7200 秒 |
| 父作业时间 | create 的全局 `--timeout` 至少为 `budget.timeout_seconds + 90`；inspect 准入最低 120 秒，实际冷读阶段沿用原镜头 worker 预算 |

父 timeout 是全作业墙钟上限，包含准入、IO、GPU、最终校验和清理。`worker+90` 只是准入下限；多阶段和大规模 IO 仍需据实提高父时间。没有已资格化的 OS 硬 RAM/VRAM 配额或断电恢复保证。

每帧都必须有 `source_frame`、`scene_frame`、`stage_frame`、`time`、`rgb`、`depth`、`normal`、`validity`、`normal_validity`、`camera_to_world`、`K`、`masks`。`K` 为 `fx/fy/cx/cy`，矩阵为 4×4；`masks` 具名为 light/highlight/line，各自为 FILE 或 null。FILE 固定为绝对本地路径 `file` 与小写 SHA-256 `expected_sha256`。`resources` 覆盖所有直接 FILE，路径不可重复、同一路径不可冲突 SHA，额外资源必须实际被权威链使用。

## create 的两条路线

| 项目 | CG 真 Pass | RGB 自动估深 |
|---|---|---|
| `source.kind` | `declared_CG_geometry_pass` | `RGB_DAV2_LARGE` |
| 原 RGB | scene-linear Rec.709、straight RGBA、float32 C-order HW4 NPY | display sRGB PNG8 RGB/RGBA；Alpha 必须全不透明 |
| Depth/Normal | Depth 为 float32 HW 轴向 Z；Normal 为 float32 HW3 相机空间；两种 validity 为独立 bool HW NPY | 四个成员都显式填 null；由同一 GPU worker 生成 raw 与派生数据 |
| `normal_source` | `import_geometry` 或 `derived_axial_z`；即使选派生，传入 Normal 及其 validity 仍须完整 | `derived_relative_heightfield` |
| `config.frame` | `metric_perspective`，fx/fy/cx/cy 与每帧 K 精确相等 | `screen_heightfield`，显式 height_scale |
| `statistics` | `{"method":"all_valid_minmax","mapping":"axial_identity"}`；保留轴向 Z 原值与单位 | `{"method":"all_valid_exact_percentile","mapping":"relative_near_one","low":2,"high":98}`；low/high 可按合同显式选择 |
| `compute` | `{"device":"CPU_NUMPY"}` 或 CUDA0_FP32 加 runtime_profile FILE | CUDA0_FP32；compute 与 source 的 runtime_profile 必须是同一 descriptor |

两条 source 都要求 `producer_evidence` FILE 与明确 `statement`。CG source 的其余真实键为：

```json
{
  "rgb_encoding": "scene_linear_Rec709_straight_RGBA_float32_NPY",
  "depth_semantics": "axial_z_scene_unit_smaller_nearer",
  "normal_space": "camera_Xright_Yup_Zbackward",
  "normal_surface": "shader_surface",
  "motion_blur": false,
  "depth_of_field": false
}
```

这是 source 的字段片段；完整 source 还包含 kind、producer_evidence、statement。normal_surface 可选 geometry_surface 或 shader_surface。传入有效 Normal 必须为单位向量，Normal-validity 是 Depth-validity 子集，失效 Normal 必须为零；消费者不静默修正它。CG 的相机旋转还接受 proper rigid 数值检查。当前固定 K，允许逐帧相机位姿，变焦不在此合同内。灯参数按明确的 camera/screen frame 解释，接口不会自动把固定 world 灯转换到每帧相机坐标。

RGB source 的其余键为 `rgb_encoding:"display_sRGB_PNG8"`、`validity:"all_frame_artistic_declared"`、`near_order:"larger_nearer"`、`model:"DAV2_Large_vitl_518_CUDA0_FP32"`、runtime_profile FILE、`max_tensor_pixels`。后者必须覆盖官方 input518 / multiple14 / lower_bound 预处理后的实际 tensor，而非只覆盖原图像素。 原生1920×1080横向帧在这条固定预处理下为518×924，即478632 tensor像素；因此 `source.max_tensor_pixels` 至少为478632。该预算与 `budget.max_pixels`、`max_total_pixels` 所覆盖的原域1920×1080及全部帧数量分别核对，不能用518×518或只填原图短边代替。

模型路线固定原已资格化 DAV2 Large、14 包、CUDA0 FP32、严格权重加载、官方预处理和恢复；关闭 autocast/TF32，不自动切 CPU、MPS、其他模型或精度。Large 权重的 CC-BY-NC-4.0 边界独立于插件许可，需按实际用途核对。本轮没有新机器、跨平台或自动安装资格；复制一个 profile 文件不会获得准入。

## 分层执行、统计和完整产物

CG CPU 使用 bundled Python 数值 worker。CUDA 路线由 owned CPU IO 阶段解码并预转 NPY，单个 no-site GPU worker 按帧上传/回读，最后由 owned CPU IO 写 PNG/EXR。RGB worker 一次加载模型，逐帧保留原域 float32 raw，再计算全镜头统计、派生 Normal 和光照；不会把 120 帧伪装成单图局部编辑代际。Host 在整批持有原输入、源码、数值 runtime、GPU 包、官方模型源码、权重与解释器的 guards，并做前后 SHA；IO 阶段只重复核实际消费的成员。

RGB 的分位是全部有效 raw 像素按像素加权的精确 linear percentile，使用磁盘映射 scratch；不做逐帧分位或 minmax 替代。raw 保持不变，工作 scalar 使用统一 low/high 映射、clip 到 [0,1]。实际有序 raw SHA 列表进一步实现为 realized statistics key，再进入每个派生 frame key；原始输入依赖 key 也保留。任一 raw/validity 变化会使全镜统计及所有依赖帧失效。CG 的轴深不做近一归一化。

完成后发布 `sequence-report.json` 与 `sequence-bundle.json`，包含每帧 raw、source RGBA、scalar、真/派生 Normal 与各 validity、具名 mask、output、delta、各灯 diffuse/specular/visibility/delta，以及 float32 straight EXR 和显示 sRGB PNG；RGB 没有传入真 Normal。每个成员绑定帧号、角色、shape/dtype、字节数与 SHA，源码、request/launch 和统计身份一并冻结。

显示 PNG 在末端执行 Standard sRGB transfer 与显示裁切；浮点 EXR 保留未裁切线性输出。显示图不能替代 raw、线性结果或数值验收。RGB 全帧有效声明、finite 数值和单位 Normal 都不构成几何置信度；全镜冻结尺度也不会修复 DAV2 自身逐帧形状/scale/shift 漂移。当前 `temporal_filter=none`。

## 从真实源清单生成并提交

1. 用 `compositing describe --operation depth-sequence --schema` 查看真实字段，按需 `--section source`、`--section compute` 或其他顶层字段。它返回 params Schema；本页链接的 JSON 文件包含完整 request 封套。
2. 生成完整源帧清单，保留真实运动、帧率/重采样链、相机/K、色彩、Pass/Normal 转换、validity 和全部源 SHA。CG上游须保留实际Pass提取与变换证据；发行物不含生产素材或私有提取审计。RGB 清单按同一个 FRAME 合同填写，四个模型产生的 Pass 成员显式为 null。
3. 写完完整 recipe，并对最终全部帧运行 normalize/protocol 预检；小段通过不代替完整规模预检。工程提供 源码包 `examples/build_sequence_request.py` 请求构建器：create 合并包含 source/frames 的清单与 recipe，自动收集直接 resources；inspect 从真实 bundle 计算 descriptor；resume 保留原 request 输入身份。
4. 异步提交，保留 job ID，在同一个 jobs-dir 用有界 wait 观察；确认实际公共终态，再读取完整 report/bundle。完整播放全部 120 帧，核对全部成员数值、真实图像、遮挡/新露出、闪烁和拖影，最后冷读。

下面是可保存为脚本的完整 create→submit→一次 wait 流程。四个数据路径和项目根由调用者传入绝对路径，输出请求不得已存在。recipe 包含 create 表列出的其余全部字段，排除 source、frames、resources；参数结构由真实 Schema 决定。

```powershell
param(
    [Parameter(Mandatory)][string]$ProjectRoot,
    [Parameter(Mandatory)][string]$FrameManifest,
    [Parameter(Mandatory)][string]$Recipe,
    [Parameter(Mandatory)][string]$RequestFile,
    [Parameter(Mandatory)][string]$JobsDirectory,
    [Parameter(Mandatory)][int]$ParentSeconds
)
$ErrorActionPreference = 'Stop'
foreach ($item in @($ProjectRoot,$FrameManifest,$Recipe,$RequestFile,$JobsDirectory)) {
    if (-not [System.IO.Path]::IsPathFullyQualified($item)) { throw 'Absolute paths required' }
}
$entry = Join-Path $ProjectRoot 'blenderctl.ps1'
$builder = Join-Path $ProjectRoot 'examples\build_sequence_request.py'
& $entry compositing describe --operation depth-sequence --schema
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $env:BLENDERCTL_PYTHON $builder --cli-root $ProjectRoot --out $RequestFile create --frames $FrameManifest --recipe $Recipe
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$request = Get-Content -LiteralPath $RequestFile -Raw | ConvertFrom-Json
if ($ParentSeconds -lt ($request.params.budget.timeout_seconds + 90)) { throw 'Parent timeout below worker+90' }
$submitted = & $entry --jobs-dir $JobsDirectory --timeout $ParentSeconds --async --compact request $RequestFile
if ($LASTEXITCODE -ne 0) { throw $submitted }
$envelope = $submitted | ConvertFrom-Json
if (-not $envelope.ok) { throw $submitted }
Write-Output $envelope.job_id
& $entry --jobs-dir $JobsDirectory --compact job wait $envelope.job_id --wait-seconds 30
exit $LASTEXITCODE
```

`wait` 返回 running 时沿同一 job ID 再做有界等待；观察超时不是作业失败，不应重复提交。默认 compact 留下完整报告及 SHA 引用；磁盘 result/report 是权威。

## inspect 与恢复

inspect 参数只有 `depth_sequence_version:"1.0"`、`mode:"inspect"`、bundle FILE、frame_order 数组、resources。120 帧可请求 `[119,0,60,119,0]`。先验证完整 inventory，再按此顺序实际重新解码选中帧，并比较重复帧的 decoded hash；没有重新估深或重打光。

bundle 必须绑定同一公共父 job：status succeeded、exit0、finished、result ok/命令/版本、request/launch 原文、完整报告、成员 SHA、源码及统计/frame keys 全部闭合。文件存在或 worker 完成不足以准入。当前 cold reader 要求精确 producer source profile；升级源码后需新资格或新验收，不能改旧 SHA 冒充兼容。

恢复继续使用 `mode:"create"`。复制原 create request 的完整输入与配方，将 `resume` 设置为旧 job 的 `sequence-resume.json` FILE，并把它纳入 resources。允许延长 worker deadline；其余 shot/source/profile/recipe、帧顺序和资源身份必须相同。构建器的 resume 子命令接收 `--request` 原 request、`--authority` 真实旧 resume 文件、可选 `--worker-seconds`，并写全新请求。

旧父必须真实终态且 owned 进程已回收。只有原子发布的完整 raw 或完整灯光阶段 checkpoint 及其全部角色/SHA 可复用；恢复在新 job 内复制、解码和验证，原 partial 保留。RGB 已完成 raw 可复用，缺失 raw 由一次新模型加载处理；全 raw 齐全后才冻结整镜统计。恢复灯光帧还必须匹配真实 raw 集合实现出的统计 key。缺帧、半写文件或残留进程均不能晋升完整 consumer。

## 改灯配方时复用完成 raw

create 可选 `reuse_raw` 为已完成 `sequence-bundle.json` 的 FILE；缺省规范化为 null。它仅用于 `RGB_DAV2_LARGE` / `CUDA0_FP32`，与 `resume` 互斥。将 descriptor 本身纳入 resources。先通过与 cold reader 相同的成功公共父、request/launch、完整成员、源码及统计身份检查；partial、失败父或只拿 raw 文件均不准入。

新旧请求须保持完全相同的 `shot_id`、source、顺序 RGB 路径/SHA、帧/time/域、camera/K、model/profile、statistics 和 compute 相同。可改变 config、执行预算、max_relative_jump、normal_source 与 masks；变更仍须通过当前 RGB 合同。新作业内逐帧复制、完整解码和验证原 raw，重新计算全镜精确统计、scalar、Normal 与灯光；不复用旧照明帧、不改原 producer。报告记录旧 authority、原 raw 与新归属；全部 raw 完整时 `model_load_count=0`，不能宣称发生新估深。源图/profile/statistics 不同须创建新的估深 producer。

## 错误定位与证据范围

| 情况 | 下一步 |
|---|---|
| INVALID_REQUEST / RESOURCE_LIMIT | 回读参数路径、连续帧/time、资源覆盖及完整规模预算；Schema 结构通过仍可能不满足语义 |
| CONFLICT | 对照原 request/launch、输入和成员 SHA、帧角色与 realized key；源已变更时新建镜头请求，保留旧证据 |
| UNSUPPORTED | 核固定 profile、模型/设备、投影和相机范围；不自动换模型、设备或降低保护 |
| CANCELLED / TIMEOUT | 读取 failure 与各阶段 lifecycle，确认实际 worker/Job 已退出；只从终态且同身份的完整 checkpoint 新建恢复 job |
| running / 观察 wait 到期 | 沿原 job ID 观察；不把它标为失败，也不因观察延迟重启业务 |

实现与资格范围见[验证矩阵](validation.md)。

当前 sequence producer 子集源身份为 `49801a5c64273a1d1d6c2b8661965448cc5da1efad6440ad36cee8ca6a5bd017`，与完整 runtime aggregate 分开。该身份的具名工程验证：120×64²人工 RGB 帧中真实取消后保留120个完整 raw、4个完整灯光帧；新 job 恢复120 raw和4完整帧，模型加载0次，完成120帧/2160成员，乱序重复 cold 通过。真实 GPU timeout 的公共父为 timed_out/exit6，compute 原因为 TIMEOUT，实际 worker 已确认退出并关闭句柄；取消/恢复同样核对真实进程回收。

同身份另有两帧改灯 `reuse_raw`：raw逐字节/SHA相同、模型加载0次，非零新照明输出最大差约0.21894；错源、错profile和partial被CONFLICT拒绝。以上证明具名人工小图的来源/缓存/生命周期，不证明真实运动画质。

历史 `a968ed3b176d654187eecb2a92621cbc3c422a9e7509ed8d445cbeeb513e84ed` 保留原身份：两张8²人工平面非零三灯 CPU/GPU 50数组最大差1.49e-8；120×64²人工 RGB 取消、3raw复用、余帧一次模型加载、2160成员及 cold；完整全镜分位/scalar独立 exact 核验。其有限 pass_with_scope 审核不重标为当前源码全部回归。

两条原创1920×1080、24fps、120帧/5秒稳定补光作品已完成：CG3240成员（3000NPY+120EXR+120PNG）、RGB动画3120成员（2880NPY+120EXR+120PNG）独立完整解码，EXR与output NPY/Alpha bits精确相等，PNG公式精确；CG保护区delta0。完整119对CG几何对齐有效覆盖最低98.158%，贡献mean_abs9e-5–1.619e-4、q90最高4.625e-4，不能据此声称零闪烁；动画119对仅screen诊断，无GT对齐或背景semantic mask。两MP4全120PTS/解码、两套离线VSE工程重开通过，用户明确连续观看认可两stable。

v004独立公开源码另行完整cold解码3240/3120成员并乱序重复访问，父终态、实际进程回收与427原source成员保护通过；对应runtimeae89b1e8…/sequence49801a5c…代码资格按最终精确SHA承接。两强实验full120技术producer通过，RGB更强配方复用120raw/model_load0；主线程实看CG新增斜带、动画白壳/背景过曝丢失细节，两实验美术拒收，仅推荐stable。Q30保留为强换光失败边界。额外Gemini完整视频读取后的JSON阶段300秒超时/partial，未算AI验收通过；本地和用户验收独立有效。

`reuse_raw`必须保持同一`shot_id`；1920×1080在固定DAV2预处理为518×924=478632tensor像素。两项原caller配方错误按guard拒绝并保留，纠正请求未改产品保护。复用使模型加载1→0是可核事实；没有同质量总agent-token基线，不能把字节或机器时间写成token节省比例。跨机、硬RAM/VRAM配额和断电恢复仍未验。
