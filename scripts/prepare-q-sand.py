"""Convert supplied Q sand photos to web assets without changing their artwork or alpha."""
import hashlib, io, json, sys, zipfile
from pathlib import Path
from PIL import Image, ImageCms, ImageOps
ROOT = Path(__file__).resolve().parents[1]
archive = Path(sys.argv[1])
output = ROOT / 'assets/web/merch-book'
records = []
with zipfile.ZipFile(archive) as source:
    for name, member in [('q-sand-front', 'Q流沙.png'), ('q-sand-back', 'Q流沙背面.png')]:
        raw = source.read(member)
        original = ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))
        alpha = original.getchannel('A')
        rgb = original.convert('RGB')
        profile = original.info.get('icc_profile')
        if profile:
            rgb = ImageCms.profileToProfile(rgb, ImageCms.ImageCmsProfile(io.BytesIO(profile)), ImageCms.createProfile('sRGB'), outputMode='RGB')
        image = rgb.convert('RGBA')
        image.putalpha(alpha)
        crop = alpha.getbbox()
        if crop:
            image = image.crop(crop)
        image.thumbnail((1100, 1100), Image.Resampling.LANCZOS)
        target = output / (name + '.webp')
        image.save(target, 'WEBP', quality=90, method=6)
        records.append(dict(source=member, sourceSha256=hashlib.sha256(raw).hexdigest(), sourceSize=original.size, crop=crop, output=str(target.relative_to(ROOT)), size=image.size, bytes=target.stat().st_size))
manifest = dict(archive=archive.name, archiveSha256=hashlib.sha256(archive.read_bytes()).hexdigest(), processing='ICC to sRGB, transparent-margin crop, max 1100px, WebP quality 90; original alpha preserved; display tone via CSS', photos=records)
(ROOT/'assets/q-sand-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(records, ensure_ascii=False))
