"""Rebuild supplied merchandise photographs: uv run --with pillow python scripts/prepare-merch.py ZIP.
Preserves artwork/alpha; crops only reviewed surrounding space. Original ZIP stays untouched.
"""
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
# Crop coordinates refer to the EXIF-oriented source, not the resized output.
PHOTOS = [
    ('postcard-front', '明信片(1).png', None),
    ('postcard-back', '明信片.png', None),
    ('ticket-front', '雷射票.png', None),
    ('ticket-back', '雷射票背面.png', None),
    ('bookmark-front', '書籤.jpg', (620, 350, 1570, 2690)),
    ('bookmark-back', '書籤(1).jpg', (570, 180, 1550, 2660)),
    ('pvc-front', 'PVC透卡.png', (110, 0, 1920, 2847)),
    ('nfc-front', 'NFC卡片(1).jpg', (180, 330, 2600, 1940)),
    ('nfc-back', 'NFC卡片.jpg', (460, 410, 2380, 1740)),
    ('leather-front', '皮革吊飾.png', (100, 40, 605, 850)),
    ('leather-back', '皮革吊飾(1).png', (390, 330, 1980, 1260)),
    ('holder-front', '票卡夾.png', None),
    ('holder-back', '票卡夾(1).png', None),
    ('sand-front', '流沙.png', None),
    ('sand-back', '流沙背.png', None),
]

def main():
    archive = Path(sys.argv[1])
    dest = ROOT / 'assets/web/merch'
    dest.mkdir(parents=True, exist_ok=True)
    records = []
    with zipfile.ZipFile(archive) as z:
        entries = {Path(f.filename).name: f for f in z.infolist() if not f.is_dir()}
        for slug, source, crop in PHOTOS:
            data = z.read(entries[source])
            im = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
            original = im.size
            if crop:
                im = im.crop(crop)
            variants = []
            for size in (640, 1400):
                web = im.copy()
                web.thumbnail((size, size), Image.Resampling.LANCZOS)
                file = dest / f'{slug}-{size}.webp'
                web.save(file, 'WEBP', quality=88, method=6, icc_profile=im.info.get('icc_profile', b''))
                variants.append(dict(path=str(file.relative_to(ROOT)), size=web.size, bytes=file.stat().st_size))
            records.append(dict(name=slug, source=source, sha256=hashlib.sha256(data).hexdigest(), originalSize=original, crop=crop, variants=variants))
    manifest = dict(archive=archive.name, archiveSha256=hashlib.sha256(archive.read_bytes()).hexdigest(), photos=records)
    (ROOT / 'assets/merch-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print('Photos:', len(records), 'WebP bytes:', sum(v['bytes'] for r in records for v in r['variants']))

if __name__ == '__main__':
    main()
