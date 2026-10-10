# 熙歌四週年 · 十種熙光

熙歌四週年應援咖啡廳的 10 個完整 Landing Page 設計提案。每版都有桌面與手機構圖、GSAP 動畫、活動資訊、交通、周邊拿取資格、FAQ、社群連結，以及獨立的 `DESIGN.md` 與 Git commit。

## 本機預覽

```sh
npm ci --ignore-scripts
npm run dev
```

開啟 [十版設計總覽](http://127.0.0.1:4173/)，點選實際頁面截圖進入各版。使用 Node.js 22 以上；網站採 HTML、CSS、JavaScript，GSAP 3.15.0 固定於專案相依套件，不依賴外部 CDN。

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

`dist/` 為可放在靜態伺服器的輸出，包含十版網站、網頁圖片與 GSAP，不包含約 100 MB 的原始素材。使用 HTTP 預覽，勿直接以 `file://` 開啟。

每版的 `QA.json` 記錄真實 Chromium 的 1440px 桌面、390px 手機模擬、動畫 transform 變化、動態開關、減少動態效果、FAQ、複製 TAG 與圖片載入結果。窄螢幕另檢查 320px。實際截圖位於 `artifacts/qa/`（本機保留、不納入 Git）；`preview.webp` 為納入 Git 的實際桌面首屏截圖。

可在已安裝 `agent-browser` 與 Python Pillow 的環境重跑：

```sh
python3 scripts/qa-version.py 01-autumn-letter
python3 scripts/qa-narrow.py 01-autumn-letter
python3 scripts/qa-carousel.py
python3 scripts/qa-delivery.py
```

建置後十版與 34 個相異本機檔案已透過 HTTP 讀取驗證；總覽縮圖、手機版面，以及第十版的鍵盤操作與資源失敗降級結果見 [交付檢查](docs/delivery-qa.json)。

技術檢查與使用者美術驗收分開記錄。實體手機效能、外部網站內容與正式活動資料後補尚未驗收。

## 專案技能

技能存放於 `.agents/skills/`，隨儲存庫保存，未安裝至全局目錄：`frontend-design`、`gsap-core`、`gsap-timeline`、`gsap-scrolltrigger`、`gsap-performance`。

技能來源與雜湊見 [來源清單](docs/skill-sources.json)，原始授權及網站 runtime 聲明見 [第三方聲明](THIRD_PARTY_NOTICES.md)。
