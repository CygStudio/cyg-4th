# 熙歌四週年 · 設計集

熙歌四週年應援咖啡廳的 11 個完整 Landing Page 設計提案。每版都有桌面與手機構圖、GSAP 動畫、活動資訊、交通、周邊拿取資格、FAQ、社群連結，以及獨立的 `DESIGN.md` 與 Git commit。

## 線上預覽

- [活動首頁：11 緋幕手帖](https://cygstudio.github.io/cyg-4th/)
- [小驢館獨立 3D 展場](https://cygstudio.github.io/cyg-4th/cafe/)
- [設計總覽：全部 11 個版本](https://cygstudio.github.io/cyg-4th/designs/)
- [GitHub 儲存庫](https://github.com/CygStudio/cyg-4th)

## 本機預覽

```sh
npm ci --ignore-scripts
npm run dev
```

開啟 [活動首頁](http://127.0.0.1:4173/)；[設計總覽](http://127.0.0.1:4173/designs/) 保留全部 11 版，可點選實際頁面截圖進入各版。使用 Node.js 22 以上；網站採 HTML、CSS、JavaScript，GSAP 3.15.0 固定於專案相依套件，不依賴外部 CDN。

| 版本 | 設計與動態特色 | 設計說明 |
| --- | --- | --- |
| [01 紅茶書簡](http://127.0.0.1:4173/versions/01-autumn-letter/) | 拱窗、信紙、封蠟與緩落花瓣 | [DESIGN.md](versions/01-autumn-letter/DESIGN.md) |
| [02 緋夜劇場](http://127.0.0.1:4173/versions/02-crimson-theatre/) | 正面舞台、紅幕揭開、追光與中央立繪 | [DESIGN.md](versions/02-crimson-theatre/DESIGN.md) |
| [03 秋日手帖](http://127.0.0.1:4173/versions/03-scrapbook/) | 拍立得、紙膠帶、角色貼紙與彈性進場 | [DESIGN.md](versions/03-scrapbook/DESIGN.md) |
| [04 熙光電波](http://127.0.0.1:4173/versions/04-signal/) | 霓虹斜切、訊號格線、頻譜與掃描光 | [DESIGN.md](versions/04-signal/DESIGN.md) |
| [05 四季花札](http://127.0.0.1:4173/versions/05-hanafuda/) | 春夏秋冬屏風、和紙紋理與卡面展開 | [DESIGN.md](versions/05-hanafuda/DESIGN.md) |
| [06 星軌祈願](http://127.0.0.1:4173/versions/06-constellation/) | 紅月、星圖、環形軌道與緩轉光環 | [DESIGN.md](versions/06-constellation/DESIGN.md) |
| [07 少女漫畫](http://127.0.0.1:4173/versions/07-manga/) | 不等分分鏡、網點、對話框與快速切入 | [DESIGN.md](versions/07-manga/DESIGN.md) |
| [08 喫茶浪漫](http://127.0.0.1:4173/versions/08-kissaten/) | 店招、遮雨棚、咖啡窗景與蒸氣 | [DESIGN.md](versions/08-kissaten/DESIGN.md) |
| [09 紅蝶標本](http://127.0.0.1:4173/versions/09-gothic/) | 哥德肖像框、紅蝶、花窗與古金格紋 | [DESIGN.md](versions/09-gothic/DESIGN.md) |
| [10 四季放映室](http://127.0.0.1:4173/versions/10-cinema/) | 寬銀幕、膠卷與可手動切換的三幕插畫 | [DESIGN.md](versions/10-cinema/DESIGN.md) |
| [11 緋幕手帖](http://127.0.0.1:4173/versions/11-theatre-scrapbook/) | 紅黑劇場貫穿全頁，中段照片與信紙拼貼，02 深色謝幕，串接獨立 3D 展場 | [DESIGN.md](versions/11-theatre-scrapbook/DESIGN.md) |

## 素材與內容

已下載雲端資料夾全部 20 個原始檔，共 105,108,087 bytes，另保存使用者提供的 3 張角色參考圖。13 張等比例縮小的 WebP 副本約 2.79 MB，保留透明背景；原始圖未重畫、去背或覆寫。各頁僅載入使用的副本，下方插畫延遲載入。

- [素材分析](docs/assets-analysis.md)：主視覺、角色設定、圖片透明度與裁切限制。
- [專案美術 brief](docs/art-direction-brief.md)：已確定需求、素材邊界與設計方向。
- [原始素材清單](assets/manifest.json)、[網頁副本對照](assets/web-manifest.json)。

活動內容依提供資訊呈現：11/23–11/29、13:00–18:00，未補年份與星期。紙類各品項 200、非紙類各品項 80，資格分別為不限與訂閱熙歌 YT。周邊照片、工作人員與繪師完整名單保留待公布文字。

## 檢查與建置

```sh
npm run check
npm run build
```

`dist/` 為可放在靜態伺服器的輸出，包含十一版網站、獨立 3D 展場、網頁圖片與 GSAP／Three.js，不包含約 100 MB 的原始素材。使用 HTTP 預覽，勿直接以 `file://` 開啟。

每版的 `QA.json` 記錄真實 Chromium 的 1440px 桌面、390px 手機模擬、動畫 transform 變化、動態開關、減少動態效果、FAQ、複製 TAG 與圖片載入結果。窄螢幕另檢查 320px。實際截圖位於 `artifacts/qa/`（本機保留、不納入 Git）；`preview.webp` 為納入 Git 的實際桌面首屏截圖。

可在已安裝 `agent-browser` 與 Python Pillow 的環境重跑：

```sh
python3 scripts/qa-version.py 01-autumn-letter
python3 scripts/qa-narrow.py 01-autumn-letter
python3 scripts/qa-carousel.py
python3 scripts/qa-theatre-layout.py
python3 scripts/qa-delivery.py
```

建置後十一版與其相異本機檔案已透過 HTTP 讀取驗證；總覽縮圖、手機版面，以及第十版的鍵盤操作與資源失敗降級結果見 [交付檢查](docs/delivery-qa.json)。

技術檢查與使用者美術驗收分開記錄。實體手機效能、外部網站內容與正式活動資料後補尚未驗收。

## 專案技能

技能存放於 `.agents/skills/`，隨儲存庫保存，未安裝至全局目錄：`frontend-design`、`gsap-core`、`gsap-timeline`、`gsap-scrolltrigger`、`gsap-performance`、`blender-image-to-3d`、`blender-web-pipeline`、`threejs-shaders`、`threejs-performance`。

技能來源與雜湊見 [來源清單](docs/skill-sources.json)，原始授權及網站 runtime 聲明見 [第三方聲明](THIRD_PARTY_NOTICES.md)。

## 小驢館 3D 空間手帖

活動首頁 `/` 採用 11 緋幕手帖，HTML 位於根目錄 `index.html`，樣式與動畫仍位於 `versions/11-theatre-scrapbook/`。舊版網址 `/versions/11-theatre-scrapbook/` 保留轉址，並保留查詢參數與錨點。`/designs/` 為獨立設計總覽；從首頁導覽列或空間照片卡可進入 `/cafe/` 獨立展場。

開啟 `/cafe/`，使用五個視角、拖曳／雙指縮放、鍵盤方向鍵與縮放按鈕探索空間。Three.js 0.186.1 在瀏覽器套用三階賽璐璐明暗及幾何描邊；模型本身保留可攜的基礎色材質。GLB 不含 Blender 專用 Shader to RGB 節點，其他檢視器不會自動呈現相同賽璐璐效果。

- [研究與來源](docs/research/little-donkey-space.md)：以 ZAPX 主座位區照片為基準，2017–2018 年照片補足歷史區域。
- [建模假設與規格](models/EN_LittleDonkey/asset-brief.md)、[Blender 原檔](models/EN_LittleDonkey/EN_LittleDonkey_master.blend)、[Web GLB](cafe/assets/little-donkey.glb)。
- [瀏覽器檢查](cafe/QA.json)、[模型清單](models/EN_LittleDonkey/asset-manifest.json)。

所有尺寸、未拍到的接合與歷史區域現況仍待確認。這是照片參考建模，沒有執行攝影測量或取得現場影片，不是實測數位分身。公開來源照片只在本機研究與 Blender 參考中保留，不隨網站建置發佈。

重新建立模型需要 Blender 4.5 LTS；腳本會重建此資產的 `.blend`、GLB 與概覽圖，編修後請先另存 Blender 原檔：

```sh
blender --background --python-exit-code 1 --python models/EN_LittleDonkey/build/01_room.py
python3 scripts/qa-cafe.py http://127.0.0.1:4173
node scripts/qa-cafe-touch.mjs http://127.0.0.1:4173/cafe/
```

網頁只在操作或尺寸改變時重繪，均衡模式限制 DPR 為 1.6，省電模式為 1。桌面與手機尺寸以 Chromium 模擬驗證；實體手機效能及現場配置尚未驗收。

## GitHub Pages 發佈

推送至 `main` 後，由 [.github/workflows/pages.yml](.github/workflows/pages.yml) 安裝固定相依套件、執行內容檢查與建置，再發佈 `dist/`。也可在 Actions 手動執行。網站資源使用相對路徑，支援 `/cyg-4th/` 專案子路徑。

公開儲存庫保留原始素材、模型與完整版本歷史；Pages 只發佈建置輸出。發佈流程依 [GitHub 官方 Pages workflow 文件](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) 設定，Actions 固定於來源 commit，建置與部署分別授予所需權限。

新版本與獨立展場的往返、3D 延遲載入和手機導覽檢查見 [組合版驗證](docs/combined-preview-qa.json)。本機建置完成且預覽伺服器啟動後可重跑：

```sh
python3 scripts/qa-combined.py
```
