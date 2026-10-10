"""Create an original 128px linear RGBA fixture in a new output directory.

Run with a separate Blender process, --background --factory-startup --disable-autoexec.
This is a small functional example, not an artistic quality benchmark.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import bpy

parser = argparse.ArgumentParser()
parser.add_argument('--output', required=True)
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
out = Path(args.output).resolve()
if out.exists():
    raise RuntimeError('Choose a new output directory; existing fixtures are never overwritten.')
out.mkdir(parents=True)
if bpy.data.filepath:
    raise RuntimeError('Use --factory-startup without an input blend file.')
if bpy.app.version[:3] != (5, 2, 1):
    raise RuntimeError('This example was qualified with Blender 5.2.1.')
for obj in tuple(bpy.data.objects):
    bpy.data.objects.remove(obj, do_unlink=True)
scene = bpy.context.scene
scene.name = 'CompositingExample'
scene.render.engine = 'CYCLES'
scene.render.resolution_x = scene.render.resolution_y = 128
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.render.fps_base = 1.0
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'None'
scene.view_settings.exposure = 0
scene.view_settings.gamma = 1
scene.display_settings.display_device = 'sRGB'
scene.render.image_settings.file_format = 'OPEN_EXR'
scene.render.image_settings.color_mode = 'RGBA'
scene.render.image_settings.color_depth = '32'
image = bpy.data.images.new('OriginalLinearFixture', width=128, height=128, alpha=True, float_buffer=True)
image.colorspace_settings.name = 'Linear Rec.709'
image.alpha_mode = 'STRAIGHT'
pixels = []
for y in range(128):
    for x in range(128):
        pixels.extend((0.04+0.2*x/127, 0.03+0.16*y/127, 0.06+0.08*((x//16+y//16)%2), 0.75))
image.pixels.foreach_set(pixels)
image.update()
image.save_render(str(out/'input.exr'), scene=scene)
bpy.data.images.remove(image)
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_depth = '8'
bpy.ops.wm.save_as_mainfile(filepath=str(out/'source.blend'))
def desc(name):
    p = out/name
    return {'file': str(p), 'expected_sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
record = {'source': desc('source.blend'), 'image': desc('input.exr'), 'scene': scene.name, 'view_layer': scene.view_layers[0].name,
          'blender': bpy.app.version_string, 'build': bpy.app.build_hash.decode(), 'width': 128, 'height': 128,
          'colorspace': 'Linear Rec.709', 'alpha_mode': 'STRAIGHT', 'expected_alpha': 0.75,
          'scope': 'Original procedural functional fixture; no external assets.'}
(out/'fixture.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'fixture': str(out/'fixture.json'), 'status': 'created'}))
