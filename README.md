<h1 align="center">🔴 Media Research (Masaüstü Pazar İstihbarat & Sosyal Dinleme Suite)</h1>

<p align="center">
  <strong>8 Sosyal Platformdan Sıfır Token Maliyetiyle Derin Veri Kazıma, Yapay Zeka Sentezi ve Profesyonel Raporlama Suite'i</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-E2232A.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-181b22.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://tauri.app/"><img src="https://img.shields.io/badge/Tauri_2.0-Rust-E2232A.svg?style=for-the-badge&logo=tauri&logoColor=white" alt="Tauri 2.0"></a>
  <a href="https://vuejs.org/"><img src="https://img.shields.io/badge/Vue_3-Vite-42b883.svg?style=for-the-badge&logo=vue.js&logoColor=white" alt="Vue 3"></a>
  <a href="https://github.com/mehmetakarim/Media-Research/stargazers"><img src="https://img.shields.io/github/stars/mehmetakarim/Media-Research?style=for-the-badge&color=E2232A" alt="GitHub Stars"></a>
</p>

<p align="center">
  <a href="#-öne-çıkan-yetenekler">Öne Çıkan Yetenekler</a> · <a href="#-hızlı-kurulum--çalıştırma">Hızlı Kurulum</a> · <a href="#-desteklenen-8-ana-platform">Desteklenen Platformlar</a> · <a href="#-raporlama--dışa-aktarma">Raporlama Suite</a>
</p>

---

## 🌟 Neden Media Research?

Pazar araştırmacıları, ürün yöneticileri, büyüme ekipleri ve içerik üreticileri için internetteki topluluk geri bildirimlerini toplamak eskiden saatler sürerdi:

- 🐦 **Twitter/X:** Pahalı kurumsal API'ler olmadan doğrudan arama yapılamazdı.
- 📺 **YouTube:** Video başlıkları, izlenmeler ve içerikler zahmetle tek tek incelenirdi.
- 📸 **Instagram & Pinterest:** Çerezler ve oturum duvarları nedeniyle otomatik analiz zordu.
- 💬 **Reddit & LinkedIn:** IP blokları ve karmaşık arayüzler yüzünden veriler dağınıktı.

**Media Research**, tüm bu bariyerleri yerel CLI motorları (`bird`, `yt-dlp`, `jina-reader`) ve **Tauri + Rust + Vue 3** mimarisiyle sıfır token maliyetinde tek bir masaüstü kontrol merkezinde birleştirir!

---

## 🚀 Öne Çıkan Yetenekler

### 1. ⚡ 8 Platform Eşzamanlı Derin Arama (80 Post / Çoklu Sentez)
* **"Tümü"** seçildiğinde **Twitter/X, YouTube, Instagram, Pinterest, Reddit, GitHub, LinkedIn ve Web** platformları paralel iş parçacıklarıyla (`ThreadPoolExecutor`) asenkron olarak taranır.
* 3-4 saniyede **80 zengin içerik** ekranda standartlaştırılmış biçimde hazır olur.

### 2. 💬 Post Kartlarında "AI Yorum" ve Tek Tıkla Türkçe Çeviri
* Her gönderi kartında **"AI Yorum"** butonu: İlgili post için dikkat çekici, değer katan ve yüksek etkileşimli profesyonel bir yorum taslağı üretir.
* **Türkçe Çevir:** Yabancı dildeki tweet, video veya makaleleri tek tıkla doğal Türkçe dil yapısına dönüştürür.

### 3. 📊 Canlı Duygu Durumu & Pazar Trend Analitiği (Sentiment Bar)
* Toplanan verilerin **% Pozitif, % Nötr, % Negatif** dağılımını gösteren canlı duygu analiz göstergesi.
* Gelişmiş filtreleme ve sıralama: *🔥 En Çok Beğenilenler*, *💬 En Çok Yorum Alanlar*, *🎬 Videolar*, *🖼️ Görseller*, *📄 Metinler*.

### 4. 📄 Lenovo Red Temalı PDF & Excel / CSV Raporlama Suite'i
* **Tek Tıkla PDF İndir:** AI pazar analizlerini, çıkarımları ve içerik taslaklarını kurumsal Lenovo Red (`#E2232A`) kapaklı A4 PDF formatında kaydetme.
* **Excel Tablosu (.xlsx):** Akıştaki tüm içerikleri (Yazar, Metin, Metrikler, Duygu Durumu, URL) Excel tablosu olarak indirme.

### 5. 🍪 Tek Tıkla Tarayıcıdan Çerez Senkronizasyonu (Opsiyonel & Güvenli)
* Chrome, Brave, Edge, Firefox veya Opera tarayıcınızdaki aktif oturum çerezlerini tek tuşla sisteme çeker.
* Çerezlerini elle girmek isteyenler için **Manuel Düzenleyici** tamamen korunmuştur.

### 6. 🔥 "Trend ve Gündem" İlham Odası
* Yüksek gösterimli sektör trendleri, büyüme yüzdeleri (`+85%`) ve yapay zeka ile doğrudan trendlerden viral içerik fikirleri üretme köprüsü.

### 7. 🧠 Çoklu Gemini Model Zinciri (Fallback Engine)
* Seçtiğiniz modelde kota veya yoğunluk yaşandığında otomatik olarak sıradaki aktif modele geçer (`gemini-3.7-flash` ➔ `gemini-3.5-flash` ➔ `gemini-2.5-flash` ➔ `gemma-4-31b-it`). Kesinti yaşanmaz.

---

## Desteklenen Platformlar

| Platform | Kur ve Kullan | Yapılandırma Sonrası Açılan Özellikler | Nasıl Yapılandırılır? |
|------|---------|-----------|-------|
| 🌐 **Tüm Web Sayfaları** | Herhangi bir web sitesini düzgün metin formatında okuma | — | Yapılandırma gerekmez |
| 📺 **YouTube** | Altyazı çekme + Video arama | — | Yapılandırma gerekmez |
| 📡 **RSS** | Herhangi bir RSS/Atom akışını okuma | — | Yapılandırma gerekmez |
| 🔍 **Tüm İnternette Arama** | — | Tam İnternet Semantik (Anlamsal) Arama | Otomatik Yapılandırma (MCP Entegrasyonu, ücretsiz API) |
| 📦 **GitHub** | Herkese açık repoları okuma + Arama | Özel (Private) repolara erişim, Issue/PR açma, Forklama | Ajanınıza söyleyin: 「Bunu GitHub hesabıma bağla」 |
| 🐦 **Twitter/X** | Tek bir tweeti okuma | Tweet arama, anasayfa akışında gezinme, tweet atma | Ajanınıza söyleyin: 「Twitter'ı yapılandır」 |
| 📺 **Bilibili / YouTube vb.** | Yerelde: Altyazı çekme + Arama | Sunucu ortamında kullanabilme | Ajanınıza söyleyin: 「Proxy yapılandır」 |
| 📖 **Reddit** | Arama (Ücretsiz Exa araması ile) | Konuları ve Yorumları Okuma | Ajanınıza söyleyin: 「Proxy yapılandır」 |
| 💼 **LinkedIn** | Jina Reader ile genel/açık profilleri okuma | Detaylı Profiller, Şirket sayfaları, İş İlanı arama | Ajanınıza söyleyin: 「LinkedIn ayarlarını yapılandır」 |
| 💬 **Podcast / Sesli İçerikler** | — | Ses dosyalarını metne dönüştürme (Whisper ile) | Ajanınıza söyleyin: 「Podcast okumayı yapılandır」 |

> **Nasıl yapılandıracağınızı bilmiyor musunuz? Doküman okumanıza gerek yok.** Sadece Ajanınıza 「**X platformunu benim için yapılandır**」 deyin, o size ne gerektiğini bilecek ve sizi adım adım yönlendirecektir.
>
> 🍪 Çerez (Cookie) gerektiren platformlar (Twitter vb.) için, Chrome eklentisi olan [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) kullanmanız önerilir. İşlem basittir: Tarayıcıda oturum aç → Cookie-Editor ile çerezi dışa aktar → Ajanla paylaş. QR kod okutmaktan daha kolay ve güvenilirdir.
>
> 🔒 Çerezler sadece yerel makinenizde yaşar. Kimseye gönderilmez. Kod tamamen açıktır.

---

---

## 💻 Masaüstü Uygulamasını Başlatma (Media Research UI)

Media Research, hem güçlü bir Python CLI çekirdeğine hem de modern bir **Tauri + Rust + Vue 3** masaüstü arayüzüne sahiptir.

### 🛠️ Gereksinimler:
- **Node.js:** v18+
- **Rust & Cargo:** (Tauri derleyicisi için)
- **Python:** 3.10+ (sanal ortam ile)

### 🚀 Geliştirici Modunda Başlatma:
```bash
# 1. Bağımlılıkları Yükleyin
npm install

# 2. Python Sanal Ortamını Hazırlayın
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 3. Masaüstü Uygulamasını Başlatın
npm run tauri dev
```

### 📦 Masaüstü Kurulum Paketini Derleme (Release Build):
```bash
npm run tauri build
```
Derlenen `.dmg` (macOS), `.msi` (Windows) veya `.AppImage` (Linux) paketini doğrudan kurup tek tıkla kullanabilirsiniz.

---

## Kur ve Hemen Kullan (Tak-Çalıştır)

Herhangi ekstra bir yapılandırma gerekmez, yalnızca ajanınıza şöyle demeniz yeterli:

- "Bu adresteki ("URL) sayfayı incele" → Ajan arka planda `curl https://r.jina.ai/URL` çalıştırır ve temiz bir markdown okur.
- "GitHub'daki bu repo ne işe yarıyor?" → Ajan `gh repo view owner/repo` komutunu çalıştırır.
- "Bu video ne hakkında?" → Ajan arka planda `yt-dlp --dump-json URL` çalıştırıp videoyu tarar.
- "Bu tweet neyden bahsediyor?" → Ajan arka planda `bird read URL` çalıştırır.
- "Bana bu RSS kaynağına abone ol" → `feedparser` ile RSS çözer.

**Komut ezberlemenize gerek yok.** Ajanınız sisteme yüklediğimiz SKILL.md rehberini tarayıp kendi kendine hangi modülü ne zaman çağırması gerektiğini bilir.

---

## Tasarım Felsefesi

**Agent Reach, devasa bir yazılım mimarisi değil, bir 'Yapı İskelesidir (Scaffolding)'**

Yeni bir ajan kullanmaya başladığınızda ona yeniden ortam hazırlamak için daima araç yükleyip bağımlılıkları çözmeye çalışır, çerezlerle uğraşırsınız — Twitter nasıl okunur? Reddit 403 hatası nasıl aşılır? YouTube dil paketleri nasıl işlenir? vs.

İşte Agent Reach temelde şu işi yapar: **Bütün bu ortam kurma angaryasını sizin yerinize tek elde halleder.**

Kurulumdan hemen sonra yapay zekanız doğrudan üst düzey komutları (`bird CLI`, `yt-dlp`, `mcporter` vb.) Agent Reach'e sormadan çalıştırabilir seviyeye gelir.

### 🔌 Her Kanal Tak-Çıkar Sistemdir

Her platform kendi arka plan aracına bağlıdır. **Kullanılan mevcut araçtan memnun değil misiniz? Değiştirmeniz saniyeler sürer.**

```
channels/
├── web.py          → Jina Reader       ← İsterseniz Firecrawl, Crawl4AI vb. ile değiştirebilirsiniz.
├── twitter.py      → bird              ← İsterseniz resmi API'ye bağlayabilirsiniz.
├── youtube.py      → yt-dlp            ← İsterseniz resmi YT API kullanabilirsiniz.
├── github.py       → gh CLI            ← İsterseniz REST API vb. ile değiştirebilirsiniz.
├── reddit.py       → JSON API + Exa    ← İsterseniz PRAW kullanarak değiştirebilirsiniz.
├── exa_search.py   → mcporter MCP      ← İsterseniz Tavily, SerpAPI eklentisiyle değiştirebilirsiniz.
└── ...
```

`agent-reach` kanalları sistemin ayakta olduğunu kanıtlama (`doctor` komutu testleri) amacı güder, kullanım direkt asıl aracın üzerinden yürür.

---

## Güvenlik Politikası

Agent Reach veri güvenliğini çok ciddi bir öncelik olarak görür:

| Bileşen | Politika |
|------|------|
| 🔒 **Bilgi Depolama** | Tüm token, çerez veya şifreleriniz YALNIZCA cihazınızda ana `~/.agent-reach/config.yaml` veya benzeri dosyalarda 600 dosya korumasıyla şifrelenir. Asla dışarı çıkarılmaz. |
| 🛡️ **Güvenli Mod** | `agent-reach install --safe` kullanırsanız, yapay zekanız haberiniz olmadan sizden izinsiz hiçbir indirme ve kurma işlemi yapmaz. |
| 👀 **Tam Açık Kaynak** | Kodlar şeffaftır, kaynak dosyalarını 2 dakikada kendiniz dahi okuyup idrak edebilirsiniz. |
| 🧩 **Modüler Güvenlik** | Bir kanaldaki koddan şüphelenirseniz, sadece o Python dosyasını silebilir veya değiştirebilirsiniz; diğer modüller hata vermeden çalışmaya devam edecektir. |

### 🍪 Çerez (Cookie) Güvenliği ile Alakalı İpuçları!

> ⚠️ **Ban (Hesap Kısıtlama) Riski Uyarısı:** Çerez veya otomatik oturum kullanılan sistemler (Twitter gibi), yapay zekanın fazla, hızlı ve otomasyon davranışlar sergilemesi sebebiyle bazen platform tarafından "bot" algılanarak hesabınıza geçici/kalıcı ban atılmasına yol açabilir.

Gerçek çerez kullanımı gerektiren ağlarda (ör. Twitter) **kesinlikle sahte/yanıtlayıcı yedek (dummy/alt)** bir hesap kullanın, asla şahsi "Ana Hesabınızı" Agent için yetkilendirmeyin.  
Bunun iki büyük yararı vardır:
1. Ban riski olduğunda ana hesabınız güvende kalır.
2. Çerezinizin internet ortamında yanlışlıkla sızdığı olası kötü felaket senaryolarında şahsi/önemli bilgileriniz yerine sadece sahte hesabınız zarar görür.

### 🗑️ Sistemi Kaldırma (Silme)
```bash
agent-reach uninstall
```
Tüm `~/.agent-reach/` dosyalarınızı, MCP bağlantılarını ve çerez yapılandırmalarını yerelinizden tamamen kazır/siler. 
Yalnızca python komutlarına kadar silmek isterseniz üstüne `pip uninstall agent-reach` çalıştırmanız yeterlidir.

---

## Projeye Katkı Sağlama

Eğer projede yeni bir sosyal medya modülü eklenmesini veya yeni özellik yazılmasını istiyorsanız doğrudan Issue kısmına konu açabilirsiniz. Agent Reach topluluğu geliştiricilere daima sonuna kadar açıktır. Repoyu "Fork" işlemiyle yerelinize alıp ekstralar eklemek için bir sınırlandırmanız yoktur. [Pull Request (PR)](https://github.com/Panniantong/agent-reach/pulls) gönderimleriniz ekibimiz tarafından test edilerek memnuniyetle dahil edilecektir.

---

## Lisans
[MIT](LICENSE)

## Bizi Destekleyin
Bu repoya katkı sağlamak istiyorsanız yukarıdan **Yıldız (Star ⭐)** simgesine tıklamayı unutmayın.
