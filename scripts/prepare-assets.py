"""Create web-sized copies without retouching or changing the supplied artwork."""
from PIL import Image
from pathlib import Path
import json
root=Path(__file__).resolve().parent.parent
mapping={
'keyvisual':('keyvisual/01-梓Azusa_熙歌週年委託 (1).png',2000),
'picnic':('lying/01-0612.png',2000),
'portrait':('standee/01-D.png',1400),
'portrait-clean':('standee/02-C.png',1400),
'lantern':('commission/01-CYG.png',1300),
'lantern-alt':('commission/03-CYG_2.png',1300),
'lantern-bg':('commission/02-CYG_BG.jpg',1500),
'lantern-scene':('commission/04-CYG.jpg',1500),
'chibi':('chibi/02-cygnus_4ani_chibi_com.png',650),
'chibi-autumn':('chibi/06-cygnus_4ani_chibi_com2.png',650),
'chibi-smile':('chibi/01-cygnus_4ani_chibi_com1.png',650),
'promo':('promo/01-_DSC1276 16 9.jpg',1800),
'promo-lettered':('promo/02-_DSC1276加字 16 9 修正.jpg',1800),
}
records=[]
for name,(source,maxsize) in mapping.items():
 im=Image.open(root/'assets/originals'/source)
 original_size=im.size
 im.thumbnail((maxsize,maxsize),Image.Resampling.LANCZOS)
 dest=root/'assets/web'/f'{name}.webp'
 im.save(dest,'WEBP',quality=88,method=6)
 records.append(dict(name=name,source='assets/originals/'+source,output=str(dest.relative_to(root)),originalSize=original_size,webSize=im.size,bytes=dest.stat().st_size))
(root/'assets/web-manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(f'Prepared {len(records)} WebP copies, {sum(x["bytes"] for x in records)/1e6:.2f} MB total')
