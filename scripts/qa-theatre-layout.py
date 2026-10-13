"""Check v11's readable content and intrinsic artwork proportions at layout breakpoints."""
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent.parent
out = root / 'artifacts/qa/11-theatre-scrapbook'
out.mkdir(parents=True, exist_ok=True)


def run(*args):
    p = subprocess.run(['agent-browser', '--session', 'cyg-theatre-layout', '--json', *args], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr + p.stdout
    result = json.loads(p.stdout)
    assert result.get('success'), result
    return result.get('data', {})


def ev(js):
    return run('eval', js).get('result')


run('set', 'media', 'light', 'reduced-motion')
results = []
for width in [320, 390, 600, 768, 820, 1024, 1440]:
    run('set', 'viewport', str(width), '1000')
    run('open', 'http://127.0.0.1:4173/versions/11-theatre-scrapbook/')
    run('wait', '--fn', 'window.__introDone === true')
    ev("""(async () => {
      for (const section of document.querySelectorAll('.section,.closing')) {
        section.scrollIntoView({behavior:'instant'});
        for (const img of section.querySelectorAll('img')) {
          img.scrollIntoView({behavior:'instant',block:'center'});
          if (img.complete && img.naturalWidth) continue;
          await new Promise((resolve, reject) => {
            const timer = setTimeout(() => reject(new Error('Image load timed out: '+img.src)), 10000);
            img.addEventListener('load', () => { clearTimeout(timer); resolve(); }, {once:true});
            img.addEventListener('error', () => { clearTimeout(timer); reject(new Error('Image failed: '+img.src)); }, {once:true});
          });
        }
      }
      window.scrollTo({top:0,behavior:'instant'});
    })()""")
    run('wait', '--fn', '[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
    checks = ev("""(() => {
      const labels = e => e.textContent.trim().slice(0, 60);
      const escapedText = [...document.querySelectorAll('.site-header a,.section h2,.section h3,.section p,.section dd,.section dt,.section summary,.section a:not(.exhibition-photo),figcaption,.closing p,.closing button,.site-footer a')].flatMap(e => {
        if (!e.getClientRects().length) return [];
        const range = document.createRange(); range.selectNodeContents(e);
        const rects = [...range.getClientRects()];
        return rects.some(r => r.left < -1 || r.right > innerWidth+1) ? [labels(e)] : [];
      });
      const intersect = (a,b) => {
        const x = a.getBoundingClientRect(), y = b.getBoundingClientRect();
        return Math.min(x.right,y.right)-Math.max(x.left,y.left)>1 && Math.min(x.bottom,y.bottom)-Math.max(x.top,y.top)>1;
      };
      const overlap = [];
      for (const selector of ['.event-grid','.exhibition-invite','.story','.gift-rules','.credits','.site-header nav']) {
        const children = [...document.querySelector(selector).children].filter(e=>e.getClientRects().length);
        for (let i=0;i<children.length;i++) for (let j=i+1;j<children.length;j++) {
          if (intersect(children[i],children[j])) overlap.push({selector,a:labels(children[i]),b:labels(children[j])});
        }
      }
      const illustrations = [...document.querySelectorAll('.exhibition-photo img,.story-album img,.gifts-mascot img')].map(i => ({
        source:i.getAttribute('src'), renderedRatio:i.clientWidth/i.clientHeight, naturalRatio:i.naturalWidth/i.naturalHeight
      }));
      return {width:innerWidth, scrollWidth:document.documentElement.scrollWidth, escapedText, overlap, illustrations};
    })()""")
    assert checks['width'] == checks['scrollWidth'], checks
    assert not checks['escapedText'], checks
    assert not checks['overlap'], checks
    assert all(abs(i['renderedRatio'] / i['naturalRatio'] - 1) < .025 for i in checks['illustrations']), checks
    run('screenshot', '--full', str(out / f'layout-{width}.png'))
    results.append(checks)
    print(f'PASS {width}px: text, column separation, artwork proportions, no horizontal overflow', flush=True)

# Native keyboard interaction must still work on the paper reminder panel.
run('focus', '.faq summary')
run('press', 'Enter')
assert ev("document.querySelector('.faq details').open")
run('press', 'Enter')
assert not ev("document.querySelector('.faq details').open")
errors = run('errors').get('errors', [])
assert not errors, errors
q = root / 'versions/11-theatre-scrapbook/QA.json'
report = json.loads(q.read_text())
report['responsiveLayout'] = {'status':'PASS', 'viewports':results, 'keyboardFAQ':True, 'pageErrors':errors, 'screenshots':'artifacts/qa/11-theatre-scrapbook/layout-{width}.png'}
q.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
run('close')
