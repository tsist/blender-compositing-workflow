# Display inputs and technical HDR

Choose the color target before graph construction. An existing display-encoded sRGB PNG and a scene-linear EXR have different provenance; loading either as “an image” without explicit interpretation can invalidate visual comparison.

## Retain a display input's appearance

Current PNG output follows the source scene's view/display. An sRGB display image processed in an AgX scene can undergo another appearance mapping; baseline/result can look similar while both differ from the original. Compare original, baseline and result.

For an explicit appearance-preservation target, prepare an independent source snapshot with Standard view, sRGB display, None look, view exposure 0/gamma 1. Preserve source color/Alpha declarations and original source SHA. Source preparation may use an owned minimal script through public `extension.run` with exact script/resource SHA and explicit local trust. This is ordinary trusted local Python, not an OS sandbox or permission to execute unknown scripts.

No preview view/display override API is introduced by this release. The saved source snapshot determines that mapping. Saved candidates can retain original dimensions/settings; the exact run request reproduces the chosen preview. SDR cannot recover already-lost HDR dynamic range.

The retained local evidence includes a display-input regression and a separately frozen held-out input, with no recipe retuning. The held-out opaque sRGB8 comparison had maximum per-channel 1 LSB error and MAE about 0.16487 LSB against fixed gates max≤2 LSB/MAE≤0.5 LSB; Alpha error was zero. This qualifies that specific route and inputs, not all images or color transforms.

## Technical HDR10/PQ encode

Read `compositing describe --operation encode --schema` before submitting. The current route uses CPU OCIO/NumPy and CPU libx265 Main10, with explicit ffmpeg/ffprobe/runtime module identities. It does not silently convert to a GPU encoder.

Choose Standard100/203 or the exact SHA-bound AgX HDR1000 route, reference-white/mapping/Alpha policy and an explicit technical mastering target. Actual config/LUT/native files must be retained in the bound closure. Report requested display/view/exposure, source/output colorspaces, reference white, encode metadata and decoded verification.

For AgX HDR1000 the known config identity and view mapping are fixed by the contract. Mastering `technical_target` is a declared target, not a measured mastering monitor. A 3% named gray/ROI brightness gate is not a full RGB pixel oracle; strict1000 diagnostics do not guarantee a universal hard peak for all possible images.

Check the encoded stream, Main10 pixel format, PQ/BT2020/range metadata, expected mastering/CLL declarations, dimensions, rational FPS/PTS and complete decode. SDR Movie/preview uses different input/output contracts and cannot serve as a substitute for scene-linear HDR input.

Real mastering, physical target HDR device viewing, artistic intent and user acceptance remain separate verification steps. Ordinary screenshots or software decoding cannot prove HDR viewing quality. When physical conditions are missing, record that status explicitly.
