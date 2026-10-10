# Compositing contract and boundaries

Compatible baseline: addon **0.4.0**, CLI **0.63.0**, Windows Blender **5.2.1 LTS / 9e2066aef7ef**. Runtime aggregate: `9566cec1c2a9bf6db34c3085d964806b8ce7bafed1e0ae145bbb5259d655e629`. Host and encoder component identities are recorded by the release inventory. Required Geometry Nodes Workflow source support for the saved-candidate persistence import is separately inventoried; it is outside that aggregate. Live `compositing describe` and selected operation `--schema` expose current contracts; static Schema files are under the checkout's `docs/cli/schemas`.

The addon creates managed native compositor groups connected to an existing root. External nodes and unrelated scene data are protected. Explicit update changes its managed part, adopt accepts an explicitly chosen safe new baseline, and detach removes the managed bridge according to contract. Manual edits are preserved and conflicts reported rather than overwritten. Unknown/missing modes and passes require investigation or an explicit extension; they are not silently approximated.

## Files and identity

Use a saved input snapshot, complete resources and exact SHA. The CLI's saved-disk state cannot detect unsaved GUI changes. Source, candidate, resource, file SHA, runtime aggregate, workflow ID, job ID and output receipt are distinct identities. Multi-entrypoint writing must not target the same live file, scene or cache.

Each job executes on an independent candidate and records source/non-target protection, full validation and final hashes. Existing sources and private assets do not become distributable because a job passed. Complete ancestor report/output/resource closure is necessary for resume. Fresh readers recompute and independently reopen; JSON/file existence or cached summaries alone are insufficient.

## Graph and image semantics

Use actual node `bl_idname`, socket identifiers, enum values and graph/component schema. Do not index sockets by translated display text or guess version interfaces. Explicit main/extra Image bindings carry file/SHA/colorspace/alpha mode; multilayer EXR uses the actual layer and required outputs. Render Layers binds the target Scene/View Layer and actual channels. Missing passes are refused rather than created or guessed.

Baseline bypasses the managed main bridge; it does not automatically disable every additional binding. Output comparison must include the original input where display mapping matters. Scene view/display affects PNG; EXR metadata and output colorspace determine its interpretation. JPEG/contact images do not prove Alpha fidelity.

## Time

Workflow 1.2/1.3 declares a fixed `reference_frame`. Image sequences enumerate every file/SHA/source frame and explicit ONE_TO_ONE mapping; source frame, scene frame and 1-based stage index are separate. Domains are continuous and unique, at most 300 frames, with no guessed missing frame. Scene FPS and exact rational mapping/timeline FPS must match. Frames and timeline are mutually exclusive; video requires the complete contiguous timeline. Budgets include baseline and result.

Typed animation targets named animatable numeric RNA with exact dimension/range and LINEAR/CONSTANT interpolation. Driver/NLA, binding/UI/time metadata are outside that route. External tracking JSON is hash-bound, dense in the original source domain, normalized_bottom_left/radians, and currently maps BoxMask Position/Size/Rotation only. It does not solve tracking or implement Corner Pin/camera tracking.

Movie input is explicitly progressive CFR H264/yuv420p8, BT709/tv/left420, SAR1:1, complete 1..N and ONE_TO_ONE mapping. It uses explicit BT709 inverse and AS_CODED orientation with audio ignored; HDR/VFR/rotation/retime/subsets are unsupported by that declared route. Original Movie SHA, decoded opaque RGBA32f LinearRec709 EXR SHA and original PTS/source/stage/scene facts remain distinct. SDR inversion cannot recover original HDR or a baked 3D scene.

## Recovery and file guards

Output receipt starts pending reference restoration; only restored graph/config/color/non-target state can promote it to verified/reused. Same request/implementation/runtime/source/resource and successful output proof are required. Unrestored pending work is rerun. supervisor cancellation/timeout is terminal authority, regardless of a stale worker checkpoint. A failed or cancelled Movie decode is fully redecoded on a new attempt unless a complete, identity-matched EOS receipt proves reuse.

Movie/runtime/receipt/decoded EXR and ancestors are guarded before interpretation. Probe/log closure is expanded from pinned receipts, then fully validated. Binding identity includes complete declaration/mapping, not just first-match file/SHA. Directory guard does not prohibit new members, so namespace re-enumeration remains necessary.

Independent OIIO inventory and Movie caches are live-guarded, process/attempt-local, full-decode-on-first-use summaries. Unknown/failed decodes are not cached; file/ancestor/SHA identities are rechecked. They do not cache RNA/Action/frame evaluation or certify pixels visually. Guards and final hash/namespace checks are retained.

## Limits

GPU selection and CPU fallback are explicit; kernel utilization, strict OIDN backend behavior and fair performance across devices require separate evidence. Technical HDR encode, physical mastering, target-device viewing and user visual acceptance are separate. Current representative support remains experimental; all-node/all-mode/all-input/cross-platform or complete normative HDR certification is not implied.
