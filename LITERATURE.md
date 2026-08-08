# LITERATURE: アイドルグループ生存構造 日韓比較

Phase 0 (ベンチマーク論文の収集・精読) の記録。

> **書誌の確認状態を必ず区別すること**
> - ✅ **書誌確認済** = OpenAlex / CrossRef API で著者・年・掲載誌・DOI を実取得した
> - 📖 **精読済** = 本文を入手して読み、データ・手法・結果・Limitations を記録した
>
> 2026-08-08 時点で本ファイルの文献はすべて ✅ 書誌確認済だが 📖 精読済ではない。
> **精読していない論文の内容を Introduction に書いてはいけない。**

---

## 1. 本研究の位置づけ (2026-08-08 の探索で判明)

先行研究の分布を OpenAlex の引用ネットワークで辿ったところ、次の構造が見えた:

| 領域 | 分析単位 | 手法 | 代表研究 |
|---|---|---|---|
| 音楽産業の生存分析 | **楽曲・アルバム** (チャート滞留期間) | ハザードモデル / 生存分析 | Strobl & Tucker (2000), Bhattacharjee et al. (2007), Giles (2007), Im & Song (2018) |
| アイドル研究 (日本) | 表象・ファンダム・ジェンダー | **質的・文化研究** | Galbraith & Karlin (2012) 収録の各章 |
| K-pop 産業研究 | 産業構造・国家政策・ファン労働 | 記述的・事例研究 | Oh & Lee (2014), Choi & Maliangkay (2014) |
| **本研究 / Kim (2026)** | **グループ (産業からの退出)** | **全数 census + 生存分析** | Kim (2026) が韓国で実施。**日本は未実施** |

**空白**: 音楽産業に生存分析を適用した研究は蓄積があるが、**分析単位はほぼ全てが楽曲・アルバムのチャート滞留**であり、「グループという組織が産業から退出するまでの期間」を全数で測ったものは、探索した範囲では Kim (2026) 以外に見当たらない。日本については未実施。

**注意**: 「見当たらない」は網羅的検索の結果ではない。Phase 6 の執筆前に、CiNii (日本語文献) と KCI (韓国語文献) を含めた再探索が必要。→ 下記「未収集・要追加」参照。

---

## 2. 直接関連 (発端の原著)

### Kim, J-S. (2026) ★ 本研究の比較対象

- **書誌**: Kim, Jeong-Seob. "Survival and Hit Structure in the K-pop Idol Music Industry: A Full Census Analysis of 1,182 Groups Debuted Between 1996 and 2025 (Since H.O.T.)" *Journal of the Korea Entertainment Industry Association* 20(4): 71-80, 2026.
- DOI `10.21184/jkeia.2026.7.20.4.71` (**doi.org で未解決・404**) / KCI ID `ART003366423`
- 状態: ✅ 書誌確認済 (KCI) / ❌ **本文未入手 (1 ページ目のみ)** / 🚫 **本文は取得しない方針で確定 (2026-08-08 本研究の著者判断)**
- 入手済ファイル: `refs/Kim2026_JKEIA_20-4_p71-80_PREVIEW-PAGE1-ONLY.pdf` (書誌 + 英文アブストラクト全文 + キーワード)

**引用可能な値の全量** (2026-08-08 に PDF を実読して確定・これ以外は存在しない):

| 項目 | 値 |
|---|---|
| 母集団 | 1,182 idol groups (1996-2025 デビュー) |
| 3 年以内の市場退出 | approximately 45% |
| 専属契約期間比 | about 42.9% of the standard seven-year exclusive contract period |
| 生存の臨界期間 | デビュー後 1-3 年 |

- **手法**: statistical analysis, cohort analysis, **expert interviews** (混合手法)。本研究は純定量なのでインタビュー部分は再現しない
- **定性的知見 (数値なし)**: winner-take-all パターン / 中ヒット → 大ヒット → 累積メガセラーへ進むグループ数の急減
- 🚫 **引用禁止 (アブストラクトに存在しないことを実読で確認)**: 3 年生存率 55.03% / 平均活動 4.12 年 / ボーイズ 5.11 年 / ガールズ 3.13 年 / アルバム 30 万枚超 42 組 / ミリオン 19 組 / 「損益分岐点突破 4% 未満」。**すべて報道由来。本文を取得しない決定をしたので、これらは恒久的に使えない**
- Keywords: K-Pop Idols, Competition, Winner-takes-most, **Death Valley**, Cohort Analysis

---

## 3. 方法論の参照 (音楽産業 × 生存分析)

いずれも ✅ 書誌確認済 (OpenAlex)・📖 未精読。

| 文献 | 掲載 | 分析単位 | 引用被数 | DOI |
|---|---|---|---|---|
| Strobl, E. & Tucker, C. (2000) *The Dynamics of Chart Success in the U.K. Pre-Recorded Popular Music Industry* | Journal of Cultural Economics | アルバムのチャート滞留 | 86 | `10.1023/a:1007601402245` |
| Bhattacharjee, S., Gopal, R.D. & Lertwachara, K. (2007) *The Effect of Digital Sharing Technologies on Music Markets: A Survival Analysis of Albums on Ranking Charts* | Management Science | アルバムのチャート滞留 | 254 | `10.1287/mnsc.1070.0699` |
| Giles, D.E.A. (2007) *Survival of the hippest: life at the top of the hot 100* | Applied Economics | 楽曲のチャート滞留 | 39 | `10.1080/00036840600707159` |
| Im, H. & Song, H. (2018) *A survival analysis of songs on digital music platform* | Telematics and Informatics | 楽曲 (デジタル配信) | 22 | `10.1016/j.tele.2018.04.013` |

**使い方**: Methods で「音楽産業における生存分析の適用は確立しているが、分析単位が楽曲・アルバムに偏っている」ことを示し、本研究がグループ単位に拡張することを位置づける。

### 組織生態学 (産業からの退出の理論的枠組み)

| 文献 | 掲載 | 引用被数 | DOI |
|---|---|---|---|
| Peterson, R.A. & Berger, D.G. (1975) *Cycles in Symbol Production: The Case of Popular Music* | American Sociological Review | 591 | `10.2307/2094343` |
| Swaminathan, A. (2001) *Resource Partitioning and the Evolution of Specialist Organizations: The Role of Location and Identity in the U.S. Wine Industry* | Academy of Management Journal | 161 | `10.2307/3069395` |

**使い方**: Discussion で「事務所というニッチ構造が生存に効くか」の理論的背景に使う候補。**精読前は引用しない**。

---

## 4. 産業・文化研究 (日韓の文脈)

| 文献 | 掲載 | 引用被数 | DOI |
|---|---|---|---|
| Galbraith, P.W. & Karlin, J.G. (2012) *Introduction: The Mirror of Idols and Celebrity* (in *Idols and Celebrity in Japanese Media Culture*) | Palgrave Macmillan | 45 | `10.1057/9781137283788_1` |
| Galbraith, P.W. (2012) *Idols: The Image of Desire in Japanese Consumer Capitalism* | Palgrave Macmillan | 28 | `10.1057/9781137283788_10` |
| Nagaike, K. (2012) *Johnny's Idols as Icons: Female Desires to Fantasize and Consume Male Idol Images* | Palgrave Macmillan | 24 | `10.1057/9781137283788_5` |
| Oh, I. & Lee, H. (2014) *K-pop in Korea: How the Pop Music Industry Is Changing a Post-Developmental Society* | Cross-Currents | 67 | `10.1353/ach.2014.0007` |
| Choi, J. & Maliangkay, R. (2014) *K-pop: The International Rise of the Korean Music Industry* | Routledge | 62 | `10.4324/9781315773568` |

**使い方**: Introduction で「アイドル研究は質的・文化研究に偏っており、産業の定量的な生存構造は測られてこなかった」という空白を示す。

---

## 5. 引用マップ (どのパラグラフで何を引くか)

| 位置 | 内容 | 引用予定 |
|---|---|---|
| Intro ¶1 | アイドル産業の規模と社会的存在感 | Galbraith & Karlin (2012), Oh & Lee (2014) |
| Intro ¶2 | 既存研究は質的分析に偏る | Galbraith (2012), Nagaike (2012) |
| Intro ¶3 | 音楽産業の定量研究は楽曲・アルバム単位の生存分析 | Strobl & Tucker (2000), Bhattacharjee et al. (2007), Giles (2007), Im & Song (2018) |
| Intro ¶4 | グループ単位の全数生存分析は Kim (2026) が韓国で初。日本は未実施 | Kim (2026) |
| Intro ¶5 | 本研究の問い: 制度 (韓国の 7 年専属契約) は生存曲線の形を作るか | — |
| Methods | 生存分析の適用・打ち切りの扱い | Bhattacharjee et al. (2007) |
| Discussion | 事務所というニッチ構造と生存 | Swaminathan (2001) ※要精読 |
| Discussion | 産業サイクルと多様性 | Peterson & Berger (1975) ※要精読 |

---

## 6. 未収集・要追加 (Phase 6 の執筆前に必須)

- ~~Kim (2026) 本文 pp.71-80~~ → 🚫 **取得しない方針で確定 (2026-08-08 本研究の著者判断)**。アブストラクト記載の 4 項目のみで進める
- [ ] **CiNii での日本語文献探索**。日本のアイドル産業の定量研究が国内誌にある可能性 (OpenAlex は日本語誌のカバーが弱い)
- [ ] **KCI での韓国語文献探索**。Kim (2026) の先行研究 (同誌の過去論文) を辿る
- [ ] 上記 §3・§4 の**精読**とデータ・手法・結果・Limitations の記録
- [ ] 「グループ単位の生存分析が本当に存在しないか」の再確認 (現在の「見当たらない」は探索的検索の結果にすぎない)

---

## 更新履歴

- 2026-08-08: 新規作成。OpenAlex / CrossRef API で 11 件の書誌を実取得し、研究の空白を特定。精読は未着手
