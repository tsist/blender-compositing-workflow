# 有限深度补光 study 辅助脚本

用于已有成功深度 bundle 上的有限预览/终稿比较。它调用现有公共 `compositing.depth-session` 和 `SessionClient`，不是新 CLI 操作，不估深、不修改准入 profile，也不选择审美最佳图。入口为本技能 `scripts/session_study.py`。

## 输入与执行

由 `blenderctl.ps1` 配置的 **Blender bundled Python 直接启动 driver**。素材处理 venv 单独使用；不要由 Store-backed venv 承载 Host 编排。先核 bundled Python 路径/SHA、CLI 源身份、当前合同、已成功 bundle 和所有实际资源，再冻结 request/actions/source-index。

- request 是完整公共请求：`schema_version: "1.0"`、`command: "compositing.depth-session"`、`params`。字段用当前 `compositing describe --operation depth-session --schema` 发现。
- actions 是严格 JSON：`{"actions":[{"name":"unique-name","kind":"preview|final","config":{},"local_edits":{}}],"stop":true}`。每项 config/local_edits 须是当前合同的完整可规范化值，示意空对象不是可直接运行配方。1–12 个具名动作，预制全部后再启动。
- source-index 是审核后 CLI 根内 `tools/blenderctl` 和 `tools/compositing_workflow_addon` 的完整递归 `.py` 集合，排除 `__pycache__`：`{"schema":"relight-helper-source-index-v1","files":[{"path":"tools/...py","sha256":"..."}]}`。相对路径与每份 SHA 绑定当前同一源；源有变化先审差异，再建立新清单，不能更新旧 SHA 掩盖变化。
- helper 核8个按依赖顺序核验的stdlib模块（protocol→filesystem→既有合同/客户端闭包）的真实路径和同字节加载体、动态 depth bridge 来源，并恢复 `sys.path`；异源缓存拒绝，使用干净 driver，不驱逐全局模块。它不是 OS 沙箱。

必需参数：`--cli-root`、`--bundled-python`、`--python-sha256`、`--source-index`、`--source-index-sha256`、`--request`、`--request-sha256`、`--actions`、`--actions-sha256`、`--jobs-dir`、`--outdir`、`--intent previews_only|requires_final`。所有文件与目录用绝对路径；SHA 为64位小写十六进制。`--preflight-only`只检查/落盘，不提交公共作业，但仍占用新 outdir；正式执行另用新 jobs/outdir。

jobs/out 必须不存在、彼此独立；选择短目录。helper 估算当前已知最终/随机临时路径族，要求 UTF16 长度 <240，不改变系统长路径设置，也不承诺任意动态路径。

## 显式预算

设动作数 N、ready 等待 R、每 revision 等待 V、关闭等待 C。须同时满足：

- `max_revisions >= N`，数据代际上限覆盖不同非空局部配方；灯位/强度变化可复用同代际。
- `V >= revision_timeout_seconds + 10`；`idle_seconds >= V + 5`；`lifetime_seconds >= N*V + 10`。
- `parent_timeout >= R + N*V + C`。
- 当前已审核 runner 还要求 `parent_timeout >= lifetime_seconds + relight.budget.timeout_seconds + 90`。helper 固定兼容 runner SHA，变化时拒绝并重新审查规则。

等待参数是 `--ready-seconds`（默认180）、`--revision-seconds`（130）、`--close-seconds`（240）、`--parent-timeout`（2200），均1..3600秒。按任务显式设置；超时上限不是预期耗时。

启动放后台，一次执行完成 submit→预制动作→stop→父终态→成员读回。不要让活会话等待代理选图；closed 后查看并选择明确 immutable revision。若需选后新建 final 会话，预制动作并记为新运行，不从 closed ready 假绑定。

## 结果和恢复

成功要求父 succeeded/exit0、result.ok、report closed、complete绑定、全部预定 revision 及 generation 成员 SHA/bytes一致、actual worker exit/handle closure成立。`INDEX.json`是身份索引，`SUMMARY.json`返回父ID和完整 driver 耗时；它们不代表视觉合格。单revision、父墙钟、driver墙钟有包含关系，不相加。PNG/EXR/贡献实际解码、Alpha/保护区、100% ROI及可编辑工程 fresh 重开仍由制作验收完成。

失败保留 `FAILURE.json`、`STATE.json`、command 日志和原 job。越过 submit barrier 后绝不自动重提；先核 `recovery_job_directory` 和真实终态。`cleanup_complete=false` 必须处理现有 owned job；true 只表示相应父终态已确认，不应超出原回执声称 GPU 退出。没有 final 的正常 closed 会话不能交付终稿。

当前导出helper固定runner SHA `7556f96b80d0597edc26a945a3ef19c738ff9f4bb832e49250191ec37e66ab13`，budget规则经AST审核。v003独立解包skill的7动作preflight已通过且submitted=false；最终导出版本实际2动作preview/final/stop仍按[验证矩阵](validation.md)记录；旧0.74两动作及ready超时证据不自动覆盖本包。source-index须从最终公开树生成；源码包有`scripts/make_source_index.py`，不复用作者生产目录的递归索引。

2026-10-17状态读取修正：v004原helper在ready前直接CRT读取status遇PermissionError，原父已取消/清理且0revision，未自动重提。当前helper通过同一精确SHA/spec/源码marker loader按依赖顺序加载protocol与filesystem，在Run初始化绑定既有`filesystem.read_shared_bytes`；每次status仍对同一raw执行16MiB、strict、job_id/state/terminalcode及SHA验证。不绕guard、不放宽预算、路径或submit barrier，不对业务作业自动重试。真实Windows renameable-handle夹具原版失败、修正版成功；错误job/state、超长JSON、重复键、无integer终态码及真实独占handle仍拒绝。v005独立source/skill已真实完成两动作preview1024→final2048PNG/32fEXR→stop，父ad372df90d454da59ec178924a3a85ff succeeded/exit0，closed/complete及actualworker退出/handle关闭通过；29个唯一revision/generation成员独立完整读回，PNG标准sRGB transfer字节误差0、EXR与output NPY像素精确相等、三灯delta和误差0。未重模型/权重，427原source成员SHA保持。此为helperf2a0e546…、runtime aggregate ae89b1e8…具名资格，旧v004失败与旧0.74成功保留各自身份。
