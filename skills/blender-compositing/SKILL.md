---
name: blender-compositing
description: 使用 Compositing Workflow 插件与公共 Blender CLI 制作、修改和检查合成图，处理静帧、有限序列或显式 SDR Movie、技术 HDR 编码、模板、批量与静态 study；用于合成制作，不替代跟踪求解、灯光、材质或视频剪辑。
---

# Blender 合成

以真实图像和可继续编辑的工程为目标：技能负责画面判断与调参，插件与公共CLI负责执行、身份、保护和记录。当前为Blender5.2.1 LTS/build `9e2066aef7ef`、CLI0.63.0、插件0.4.0；177 runtime freeze `9566cec1c2a9bf6db34c3085d964806b8ce7bafed1e0ae145bbb5259d655e629`，10 Host `72d2e677f608afe432c0d09623a505cad51c5240ec1467e3a7e5ba9cbb56dc00`。当前具名公共模板、批量、study和恢复，以及三帧时序模板链已有实际证据；两项报告Schema修正已安装且运行代码未变。公开副本仅适配定位、导航和发布状态，保持原合成方法、guard与历史身份边界。具体版本、旧失败、独立验证、跨案例与未验范围按需回读 [公开领域合同](references/contract.md) 与 [验收范围](references/validation.md)，不把旧M1–M4身份或Schema通过认证为当前全部回归。技术、AI视觉、用户认可和目标HDR设备观看分别记录。

## 发现与工作路线

使用本仓兼容 CLI 公共入口及 [用法](references/usage.md)，宿主已有 blender-cli 技能时可协作。将 `BLENDERCTL_ROOT` 指向实际兼容 checkout 根，`BLENDERCTL_PYTHON` 指向实际 launcher Python，正式执行显式提供全局 `--blender`；不默默安装环境。

```powershell
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') --version
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe
& (Join-Path $env:BLENDERCTL_ROOT 'blenderctl.ps1') compositing describe --operation run --schema
```

describe不创建job或启动Blender。当前公开run/inspect/encode/template-save/template-run/batch/study；create/update/adopt/detach仍是manifest.operation。按所选操作读取--schema，source/graph/components/animation/tracking_imports按需发现；组件逐kind参数、socket/menu用实际identifier。Movie经run/inspect的1.3声明使用。encode独立Host后处理；M5四操作仍在一个Blender worker内同job调用正常Host，不嵌套supervisor。原生 addon 的 register/unregister 没有专用面板或操作器；完整作业由匹配 CLI 执行。原生addon包提供纯合同/持久validator；Movie转换依赖CLI host、NumPy/OIIO与显式ffmpeg/ffprobe，addon自身没有Movie解码器。

从已保存工程、图像和约定获取Scene/ViewLayer、输入Pass/色彩/Alpha、时间关系与用途；只询问无法查明的关键方向。先同条件小样看图，再按约定质量生成终稿。临时preview配置不是candidate保存的默认终稿配置。

显示编码图片先明确希望保留原外观还是重新做场景调色。当前PNG输出跟随源Scene的view/display；把已经显示编码的sRGB PNG放进AgX源会再次映射，baseline与result相近也可能同时偏离原图。若目标是保留既有sRGB PNG外观，可在独立工作快照选择Standard/sRGB、None look、view exposure0/gamma1，再按固定配方合成；不要覆盖原工程或静默改全局偏好。比较原图、baseline和result，并独立检查Alpha；EXR仍为线性数据，不能从SDR恢复已丢失HDR。当前preview没有view/display覆盖字段，可复用已明确颜色目标的源快照，必要时在授权内用精确SHA的最小公共extension工作副本脚本准备；方法和真实B02回归/B03留出见领域文档。engine=SOURCE只保留引擎，省略device仍采用当前Schema默认；明确记录实际requested/used/fallback及保存配置恢复。

## HDR、模板与有限候选

需要HDR输出时先读encode Schema与 [公开色彩/HDR指南](references/color-hdr.md)。encode固定CPU OCIO/NumPy＋CPU libx265 Main10；明确Standard100/203或精确SHA绑定AgX HDR1000、reference white/mapping、Alpha和虚拟technical Master。SDR Movie不能恢复原HDR；3%具名亮度mean/ROI门槛不是全部RGB像素误差，strict1000诊断不是所有输入硬峰保证。技术码流/metadata/decode、真实mastering、目标设备观看与用户认可分别说明；M4旧99f封存与0.63 Host证据各守原身份。

template-save只消费完整passed正常producer导出recipe与显式slots；template-run给新file/SHA、context/source/bindings/resources/preview。同条件小样后看图，不因模板落盘就认定新源通过。template-run的resume是**旧外层template-run-report.json**；worker认证精确parent request/status/result/领域报告后，解析exact parent/compositing-report.json、SHA与native signature交给正常Host。不可直接给native报告冒充外层，也不可传caller authority/runtime/callback；新attempt保留祖先完整闭包，旧SHA不手改跨实现复用。

三帧Movie完整producer→save→独立既有EXR3 consumer→外层resume已实际验证，显式source1..3至scene10..12和Alpha1/.75变化；这不是新Movie或另一blend，也未验模板参数动画tracks、full120或Movie取消窗口。复用模板时仍逐次给定source/bindings、参考帧与mapping，不据小样推定时序泛化。

batch按成员启动取guard；坏项独立失败，后项继续，成功闭包持到最终完整复核与发布，失败scope释放。succeeded/ok可以是partial，不能说all-passed；原请求不变的恢复复用实际通过成员，坏项仍失败。study只做有限静态create、显式已声明参数，基线失败不做比较但保留合法候选；parents/native/source/output/comparison持锁到发布并重查runtime。PNG/EXR是Alpha技术依据，JPEG/contact只供RGB看图；候选由用户人工选择，不自动按均值排名。

提交、status/result/wait/cancel始终用同一显式jobs-dir，全局参数在子命令前。取消用公共job cancel，timeout/cancel以supervisor终态为权威；旧checkpoint running或passed不能覆盖它。仅真实终态、原recipe/runtime/implementation与已成功闭包匹配才能恢复，未实查前不写reused，不承诺任意渲染中点续算。当前待验项目回读公开验收范围及本机匹配身份记录，不能把285个d76独立有限检查或FakeHost控制流当新公共通过。

## 不可省略的输入与时序事实

run使用UTF-8请求、源file/SHA、完整resources和单一manifest，独有audit批次/jobs-dir。输入是磁盘快照，后台不观测GUI未保存修改；手改后显式保存新快照/新SHA，再inspect或点名update，不自动覆盖手改。adopt须明确接受安全新基线；替换图用replace_graph。

主源/额外Image显式绑定file/SHA/colorspace/alpha_mode；多层EXR再给真实layer，主图为Combined。缺层/Pass/分量明确拒绝，不打开缺失Pass或猜解释。Render Layers只绑定目标Scene/ViewLayer；Camera与Cycles noisy/denoise需求按实际图核对。RNA size=[0,0]不代替独立文件解码。baseline只旁路主bridge，额外绑定不自动全部关闭。

1.2/1.3显式给固定reference_frame，预览推进用frames或timeline，不能改参考帧冒充恢复。image_sequence逐项列file/SHA/source_frame和ONE_TO_ONE mapping；原source_frame、scene_frame、1起始stage_index分开。域最多300、连续唯一，缺帧不猜；Scene FPS、mapping和timeline的rational FPS必须一致，不自动retime。frames与timeline互斥；视频需完整连续timeline。预算计入baseline/result两个role。

1.3 Movie给原file/SHA、完整1..N/ONE_TO_ONE mapping、interpretation(method=BT709_OETF_INVERSE_V1/coded_orientation=AS_CODED/audio=IGNORE)、ffmpeg/ffprobe decoder_runtime；原Movie与两个runtime在resources同SHA闭合。仅progressive H264/yuv420p8、明确BT709/tv/left420/SAR1:1/完整CFR；无HDR/VFR/rotation/retime/subset或音频合成。原MovieSHA、derived opaque RGBA32f LinearRec709 EXR SHA与原始PTS/source/stage/scene分开。显式BT709 inverse不恢复已烘焙SDR的原HDR/3D场景；SAR metadata remux的全YUV framehash相等不等于恢复原场景。

Movie四入口先guard原Movie/runtime/receipt/全部EXR及祖先，再读pinned receipt展开probe/log并guard，最后完整host validator；fresh allowed path/SHA先检查再open。collector不是完整认证。按binding key和完整declaration定位同原Movie的不同mapping，不能以file/SHA first-match代替绑定身份。partial/cancelled decode新attempt完整重解，只有complete EOS与全部身份/closure一致才复用祖先namespace。

typed轨道只写点名可动画数值RNA、实际维数/范围与LINEAR/CONSTANT；不接driver、NLA或binding/UI/time元数据。外部tracking只消费SHA绑定的严格JSON、完整稠密原source域，normalized_bottom_left/radians；当前只映射BoxMask Position/Size/Rotation，不是自动求解、Corner Pin或相机跟踪。

preview声明输出画布，输入不会自动fit。尺寸不匹配且无显式图域适配时可能center crop；匹配尺寸或明确Scale/Transform后再看整体构图。三帧320裁切小样不能当完整作品预览或1080p质量通过。

## 输出、色彩与验证

公共异步提交/有界wait后，同时核对退出码、ok/error、supervisor终态、完整hashed report、源/非目标保护、fresh和实际独立解码；compact只是有界摘要。序列超过8份输出时采样显示与count不代表只生成采样帧；详细帧绑定、Action、PTS及保护差异回读完整报告。取消/超时以supervisor为终态权威，checkpoint running不是通过。

PNG使用源display/view，32f EXR按实际output_color_space与独立metadata解释，OCIO/config/LUT身份显式记录。工作角色不直接等于EXR输出色域，EXR或SDR视频不证明HDR10。选中compositor/renderer GPU不证明OIDN backend或内核利用率；严格禁止内部CPU回退时拒绝不可证明的Denoise承诺。

SDR_MP4_H264需caller显式ffmpeg/ffprobe file/SHA，COMPOSITE_BLACK会丢Alpha并在已烘焙display域合黑底。识别sRGB才明确转换BT709并读回CICP/range；检查单流无音轨、全视频decode、尺寸/帧数/rational FPS及全部精确PTS。代表有损RGB读回不是逐像素或全片色度认证。

看同条件baseline/result，检查构图、主体/背景融合、细节、高光、噪声与遮罩边缘；数据均值变化不能代替美术验收。交付可编辑candidate、实际预览/PNG/EXR/必要视频、完整报告及恢复引用，说明技术通过、AI观察和用户认可各自状态。

## 恢复与性能边界

1.2/1.3输出先pending_reference_restoration；图、保护、源配置、色彩完整恢复后才reference_restoration=passed并晋级verified/reused。resume保持原请求/实现/runtime/源/资源/候选/输出SHA并创建新attempt；仅完整输出和已恢复帧复用，pending重做，verified/reused缺proof仍拒绝。不改旧SHA、不承诺原生render任意中点续算。格式enum不可回置时只重开自身受保护candidate，pending_owned_candidate_reopen不算通过，不重开用户GUI。

独立OIIO inventory可在同process/attempt的live不可写删除guards内复用：首完整decode，每次原handle/fresh path/ancestor/SHA与selection key核对，key区分space/Alpha/layer/required/inventory。未知full decode、失败不缓存、deepcopy、结束清空；RNA、Action、动态namespace和帧求值仍独立检查，最终完整SHA复查保留。这不是跨process缓存或视觉质量证明。

Movie strict cache与普通Image inventory分开：owned-movie-opaque-linear-v1/path/SHA/width/height首次全像素finite/opaque/interop验证后只缓存summary；每次live handle/fresh path/祖先核对，unknown/失败不缓存、结束清空，RNA/namespace/provenance仍实查。directory guard禁止祖先rename/delete，但可新增目录成员，所以完整namespace每次及最终枚举不能省略。

fresh预算仍按完整求值数/输出数：temporal=0为180秒；1–300/≤1200采用ceil(180+2×帧数+0.12×输出数)、180–1200秒。历史aecf full120 saved180/output478实际通过，额外Movie workload政策尚未实施，不承诺跨机器时间；Host整数metadata与reader canonical exact类型/计数/policy/scope比较，bool/等值float拒绝（12项纯回归），不保留旧703未严格表示为当前现状。完整逆序、全部decode、guards、RNA/Action/保护不抽样。父timeout/取消权威，job wait返回running保持原job，不重提、不高频轮询。

全120独立numeric为360真实EXR decode，mapping/Alpha误差0、完整RGB Exposure最大1.8574e-7；只证明该功能fixture。observer仅后段567samples/566.253秒，whole-device VRAM包含其它消费者，不是完整峰或job专属资源；不同图的M3/M3b耗时不作提速结论。M3b历史三张JPEG已看金属/浮雕与微抬曝光，灰栏fixture不是最终构图；该历史M3b仍未验自然motion/完整羽化/HDR/GUI/kernel；当前M4技术HDR按前述具名证据范围判断，目标HDR设备观看仍未验。

未知版本/新领域或方法被结果质疑时先回读 [公开合同](references/contract.md) 和 [依赖](references/dependencies.md)；宿主有相关 Wiki 时先检索并回读其有效原文，再补实际版本资料和最小验证；本技能不复制Wiki正文。只因复用成熟流程不例行整库检索。未验需求可在授权内研究，不隐式近似替代，也不以旧scope永久拒绝未来开发。
