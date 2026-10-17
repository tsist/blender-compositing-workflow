"""Read a guarded square RGBA cutout with opaque core and derive geometric foot placement; never edit pixels."""
import argparse
import json
import math
from pathlib import Path
import sys

def inspect_layout(image, expected_sha256, canvas=2048, target_height=0.68, floor_y=0.13,
                   alpha_threshold=0.05, project_root=None):
    if not (16 <= canvas <= 2048 and 0 < target_height < 1 and 0 <= floor_y < 1
            and floor_y + target_height <= 1 and 0 < alpha_threshold < 1):
        raise ValueError('Invalid canvas, body height, floor or alpha threshold')
    if project_root is None:
        project_root=next((p for p in Path(__file__).resolve().parents if (p/'tools/blenderctl/filesystem.py').is_file()),None)
    if project_root is None or not Path(project_root).is_absolute():
        raise ValueError('Pass an absolute --project-root containing the companion CLI source')
    expected_module=(Path(project_root)/'tools/blenderctl/filesystem.py').resolve()
    prior=list(sys.path)
    try:
        sys.path.insert(0,str(expected_module.parent))
        import filesystem
        if Path(filesystem.__file__).resolve()!=expected_module:
            raise ValueError('Conflicting filesystem module origin; use a fresh driver')
        FileGuard=filesystem.FileGuard
    finally:
        sys.path[:]=prior
    import OpenImageIO as oiio
    import numpy as np
    path=Path(image).resolve()
    with FileGuard(path) as guard:
        if guard.sha256()!=expected_sha256:
            raise ValueError('Input SHA differs from declared image')
        reader=oiio.ImageInput.open(str(path))
        if not reader:
            raise ValueError('Image is not independently decodable')
        try:
            spec=reader.spec()
            if spec.width!=spec.height or spec.width<16 or spec.width>2048 or spec.alpha_channel!=3 or spec.nchannels!=4 or list(spec.channelnames)!=['R','G','B','A']:
                raise ValueError('This profile requires a square RGBA cutout no larger than 2K')
            pixels=np.asarray(reader.read_image(oiio.FLOAT))
            if pixels.shape!=(spec.height,spec.width,spec.nchannels) or not np.isfinite(pixels).all():
                raise ValueError('Incomplete or nonfinite image')
            alpha=pixels[:,:,spec.alpha_channel]
            if alpha.min()<-1e-6 or alpha.max()>1+1e-6:
                raise ValueError('Alpha outside 0..1')
            if alpha.max()<1-1e-6:
                raise ValueError('This opaque-product profile requires an opaque Alpha core; uniformly translucent inputs are unsupported')
            coords=np.argwhere(alpha>=alpha_threshold)
            if not len(coords) or not np.any(alpha<alpha_threshold):
                raise ValueError('Meaningful transparent margin and nonempty subject are required')
            ymin,xmin=map(int,coords.min(0));ymax,xmax=map(int,coords.max(0))
            width,height=int(spec.width),int(spec.height)
            bbox_height=ymax-ymin+1
            scale=target_height/(bbox_height/height)
            cx=(xmin+xmax+1)/(2*width)
            base=(height-ymax-1)/height
            x=canvas*scale*(0.5-cx)
            y=canvas*(floor_y-0.5-scale*(base-0.5))
            if not all(math.isfinite(v) for v in (scale,x,y)) or not 0<scale<=2:
                raise ValueError('Unreasonable derived fit')
            observed=guard.sha256()
            if observed!=expected_sha256:
                raise ValueError('Image changed during layout measurement')
            return {'image':str(path),'expected_sha256':observed,'size':[width,height],
                    'alpha_threshold':alpha_threshold,'bbox_top_left_inclusive':[xmin,ymin,xmax,ymax],
                    'canvas':[canvas,canvas],'target_height':target_height,'floor_y':floor_y,
                    'transform_inputs':{'Scale':scale,'X':x,'Y':y,'Interpolation':'Bicubic'},
                    'shadow_position':[0.505,floor_y+0.003],
                    'scope':'Square RGBA opaque-product cutout layout after RenderSize Fit. Opaque core presence is a technical prerequisite, not semantic recognition of glass. Metadata only; pixels unchanged. Sparse low-alpha specks below threshold are ignored for positioning, not removed from the image. Transparent glass/refraction, existing baked shadows, non-upright or multiple objects and arbitrary scene solving are unsupported. The bbox bottom is a geometric anchor; visible contact and shadow strength require image review.'}
        finally:
            reader.close()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image',required=True);p.add_argument('--expected-sha256',required=True)
    p.add_argument('--canvas',type=int,default=2048);p.add_argument('--target-height',type=float,default=.68)
    p.add_argument('--floor-y',type=float,default=.13);p.add_argument('--alpha-threshold',type=float,default=.05)
    p.add_argument('--project-root',help='Absolute companion CLI source root; inferred only from an enclosing source checkout')
    a=p.parse_args()
    try:
        result=inspect_layout(a.image,a.expected_sha256,a.canvas,a.target_height,a.floor_y,a.alpha_threshold,a.project_root)
    except Exception as e:
        print(json.dumps({'ok':False,'error':type(e).__name__,'message':str(e)}));return 2
    print(json.dumps({'ok':True,'data':result},ensure_ascii=False));return 0

if __name__=='__main__':raise SystemExit(main())
