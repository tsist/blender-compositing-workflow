# Validation and limits

Status: **bounded local technical pass / experimental**. Addon 0.4.0 and compatible CLI 0.63.0 are packaged with unchanged runtime implementation `9566cec1c2a9bf6db34c3085d964806b8ce7bafed1e0ae145bbb5259d655e629`. Evidence from earlier M1–M4 keeps its exact original version/identity. This page is a public summary; full private production inputs, case images and local audit jobs are excluded.

The initial final-release staging run exposed a missing source import dependency: `compositing_workflow` imports `geometry_workflow._retain_unlinked_ids`, whose module imports `geometry_nodes_workflow_addon`. That public `compositing.run` failed with ModuleNotFoundError. The corrected checkout includes the original support package (7 Python files + manifest), separately hashed outside the 177-file compositing aggregate. The failure remains part of release evidence; the earlier M5 unpacked inspect smoke does not establish a complete independent run. The identical frozen request passed after adding the dependency, with independent saved-file reopening, four fully decoded images and the numeric checks below.

## Existing local evidence

| Area | Observed result | Boundary |
|---|---|---|
| Static cases | Product vase 2K, stylized Cycles/Eevee 2K, external AlphaOver blending 2K and native 4096² output; independently decoded images and source/output closure | Representative cases, not all node modes/materials/engines |
| CPU behavior | Explicit CPU rendering and deliberately unavailable requested GPU backend gave declared CPU fallback; Alpha matched in the selected comparison | Renderer and compositor backend are separately reported; no fair speedup or strict all-pixel backend equivalence claim |
| Display input | Standard/sRGB independent source, unchanged component recipe, regression plus new frozen held-out opaque sRGB input; bounded roundtrip gates passed | Original AgX appearance failure is retained; no all-image color certification |
| M5 templates | Complete normal producer recipe, actual new-input consumer, outer resume | Saved template existence alone is not new-consumer validation |
| Batch/study | Actual public execution, partial failure and finite static candidate outputs | Contact sheets are functional examples; no automatic artistic winner |
| M5 cancellation/timeout | Actual supervisor terminal states, successful recovery with respectively 1 reused+7 rerun and 2 reused+6 rerun | No arbitrary intermediate-render resumption or complete OS-process-descendant certification |
| Temporal template | Three-frame Movie producer→template-save→independent existing EXR consumer→outer resume; mapping/Alpha errors zero | Not another Movie, parameter-animation template or full120 requalification under the new identity |
| Schema correction | Two real report/compact schema failures preserved; fixes passed 125 independent checks and original 76 positive/negative cases | Runtime Python remained unchanged; schema checks alone are not end-to-end execution |
| Native packaging | Offline extension build/validate; exact source namespace and GPL text | Installing/registering does not establish graph/render/visual usability |
| Historical temporal/HDR | Original identities include bounded full120 numeric/movie fixtures and three 1080p/120-frame/5-second HDR10/PQ technical routes | Earlier identity is not relabeled as current whole-runtime regression; physical HDR mastering/viewing unverified |

Technical decode/protection/numeric evidence and AI visual observations are separate. The representative 4K resource observer used bounded sampling and whole-device VRAM; these are not exclusive kernel allocations or true lifetime peaks. Different scenes/engines/timings are not a controlled performance benchmark. Local Cycles noise and fixture quality limitations are retained.

## Final release-specific verification

| Check | Current status |
|---|---|
| Corrected public checkout synthetic example | Passed: original 128×128 RGBA fixture, +0.5 EV, CPU renderer and compositor, editable candidate, before/after PNG and EXR |
| Independent numeric oracle | Passed: EXR RGB equals baseline × sqrt(2), maximum absolute error 0; Alpha remains 0.75, maximum error 0; all four outputs fully decoded |
| Native GUI snapshot → CLI handoff | Passed in isolated non-background Blender: programmatic node edit and native event simulation, exposure 0.12→0.37; exact conflict detected, unadopted update rejected; explicit adopt and subsequent saturation update preserved 0.37 |
| GUI handoff protection/output | Four saved files independently reopened, protected data/root connections equal; fresh 1600×1200 PNG/EXR before/after decoded, actual PNG and node-editor screenshot visually checked |
| Extension-manager install/enable and human mouse experience | Not run; isolated module registration is a separate, narrower check |
| Independently followed public skill | Passed: separately authored 192×128 original input, +0.25 EV, public run and independently constructed inspect; five images fully decoded, RGB error 2.50e-8 (limit 1e-6), Alpha error 0, source/candidate hashes preserved |
| Public source integrity | Passed: 177 runtime files, 8 support files, 145 schemas and sanitized capability document checked by SHA; 5 skill references match their public source documents |
| Release archive execution | Passed from extracted source archive: generated fixture and request, actual public run, supervisor success, fresh saved-file and output readers, four decoded images and RGB/Alpha oracle |
| Deterministic archives and native ZIP | Repeated byte-identical builds; every ZIP entry matched source bytes; Blender extension validate accepted the native package. Released files have their own SHA256SUMS |
| User artistic acceptance of final work | Not received |
| Real calibrated HDR mastering | Not run |
| Physical target HDR-device viewing | Not run |
| Cross-machine, Linux/macOS and other Blender versions | Not run |

Physical/user conditions remain explicit open items and must not be called fully passed. A versioned experimental release represents the stated bounded software capabilities.

## Recovery, visual and manual boundaries

Missing media/channels and malformed inputs stop affected items; independent batch work can continue. Manual edits survive, conflicts are reported and explicit adopt is a deliberate new baseline. Supervisor terminal status, restored frame proof and full hash closure govern resume.

Before production delivery compare original/baseline/result with matching dimensions and color targets, check detail/highlights/noise/mask edges, and retain editable source/candidate/configuration. PNG/EXR/preview format choice does not establish an HDR display target or user visual approval. SOURCE engine does not preserve a requested device unless it is explicitly declared.

The release source excludes original acceptance media and private Wiki. Public summaries distinguish factual local evidence from runnable public fixtures. Added examples require their own clean-checkout execution evidence; new materials/scenes/modes require matching validation rather than an inherited pass label.
