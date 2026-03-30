<h1 align="center">👁️ Agent Reach</h1>

<p align="center">
  <strong>Yapay Zeka (AI) Ajanınıza Tek Tıkla İnternet Yeteneği Kazandırın</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="MIT License"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9+-green.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+"></a>
  <a href="https://github.com/Panniantong/agent-reach/stargazers"><img src="https://img.shields.io/github/stars/Panniantong/agent-reach?style=for-the-badge" alt="GitHub Stars"></a>
</p>

<p align="center">
  <a href="#hızlı-başlangıç">Hızlı Başlangıç</a> · <a href="docs/README_en.md">English</a> · <a href="#desteklenen-platformlar">Desteklenen Platformlar</a> · <a href="#tasarım-felsefesi">Tasarım Felsefesi</a>
</p>

---

## Neden Agent Reach'e İhtiyacınız Var?

Yapay Zeka Ajanınız halihazırda sizin için kod yazabilir, belge düzenleyebilir veya proje yönetebilir — ancak ondan internette bir şeyler bulmasını istediğinizde genellikle tıkanır:

- 📺 "Bu YouTube eğitim videosunun ne anlattığına bir bak" → **İzleyemez**, altyazıları çekemez.
- 🐦 "Twitter'da insanlar bu ürün hakkında ne diyor araştır" → **Arayamaz**, Twitter API'si ücretlidir.
- 📖 "Reddit'e gidip aynı sorunu (bug) yaşayan var mı bak" → **403 Hatası alır**, sunucu IP'si reddedilir.
- 📕 "Bana Pinterest/Instagram (ör. Xiaohongshu) üzerinden bu ürünün yorumlarına bak" → **Açamaz**, giriş yapılması gerekir.
- 🔍 "İnternette en son LLM framework karşılaştırmalarını araştır" → **İyi bir arama yeteneği yoktur**, ya ücretli araçlar gerekir ya da kalite düşüktür.
- 🌐 "Bana bu web sayfasında ne yazdığını oku" → **Bir yığın HTML etiketi çeker** ve okuması imkansız hale gelir.
- 📦 "Bu GitHub reposu ne işe yarıyor? Issue'larda ne yazıyor?" → Kısmen yapabilir, ancak kimlik doğrulama yapılandırmaları can sıkıcıdır.
- 📡 "Bu birkaç RSS kaynağına abone ol, güncellenirse bana haber ver" → Bunun için sizin kütüphane kurup kod yazmanız gerekir.

**Bunların yapılması zor değil, fakat sizin kurulum ve yapılandırma için çok uğraşmanız gerekir.**

Her platformun kendine has engelleri vardır — ücretli API'ler, aşılması gereken engeller, giriş yapılması gereken hesaplar, temizlenmesi gereken veriler. Sırf ajanınıza bir tweet okutabilmek için hatalarla (bug) boğuşup, araçlar kurup saatlerinizi harcayabilirsiniz.

**Agent Reach, bu işi tek bir cümleye indirger:**

```
Agent Reach kurulumunu yap: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

Bunu kopyalayıp Ajanınıza gönderin, birkaç dakika içinde agent Twitter okumaya, Reddit'te gezinmeye, YouTube videoları izlemeye ve karmaşık sayfalarda arama yapmaya başlar!

**Zaten kurdunuz mu? Güncellemek de tek cümledir:**

```
Agent Reach'i güncelle: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
```

> ⭐ **Bu projeye yıldız (Star) verin!** Çeşitli platformlardaki değişiklikleri sürekli takip ediyor ve yeni kanallar ekliyoruz. Kendiniz takip etmek zorunda değilsiniz — bir platform erişimi engellerse biz düzeltiriz, yeni bir kanal çıkarsa biz ekleriz.

### ✅ Kullanmadan Önce Bilmeniz Gerekenler

| Özellik | Açıklama |
|---|---|
| 💰 **Tamamen Ücretsiz** | Tüm araçlar açık kaynak kodludur, tüm API'ler ücretsizdir. Olası tek masrafınız (eğer yerel bilgisayar yerine sunucuda kullanıyorsanız) sunucu vekleme yöneticisi için (aylık ~1$) proxy olabilir. |
| 🔒 **Gizlilik ve Güvenlik** | Çerezler (Cookie) yalnızca yerel cihazınızda tutulur, dışarı aktarılmaz veya yüklenmez. Kod tamamen açık kaynaklıdır ve her an incelenebilir. |
| 🔄 **Sürekli Güncelleme** | Altyapı araçları (yt-dlp, bird, Jina Reader vb.) düzenli olarak en son sürümüne güncellenir. Siz güncellemeleri kendi başınıza takip etmek zorunda kalmazsınız. |
| 🤖 **Tüm Yapay Zeka Ajanlarıyla Uyumluluk** | Claude Code, OpenClaw, Cursor, Windsurf… Komut satırı (CLI) çalıştırabilen tüm ajanlarla kullanılabilir. |
| 🩺 **Dahili Tanılama (Diagnostic)** | `agent-reach doctor` komutu size hangi eklentinin çalıştığını, hangisinin çalışmadığını ve nasıl düzeltebileceğinizi söyler. |

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

## Hızlı Başlangıç

Şu ifadeyi kopyalayıp Yapay Zeka Ajanınıza (Claude Code, OpenClaw, Cursor vs.) yapıştırın:

```
Agent Reach kurulumunu yap: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
```

Hepsi bu kadar. Ajan geri kalan her şeyi kendi halledecektir.

> 🔄 **Zaten Kurdunuz mu?** Güncellemek için tek satır yeterli:
> ```
> Agent Reach güncellemesi yap: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md
> ```

> 🛡️ **Güvenlikten Endişeniz mi Var?** Güvenli modda (safe mode) yükleyebilirsiniz — Sistem paketlerini otomatik olarak kurmayacak, sadece size neye ihtiyaç duyduğunu önerecektir:
> ```
> Agent Reach (Güvenli Mod) kurulumunu yap: https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
> Kurulum sırasında --safe parametresini kullan
> ```

<details>
<summary>Agent Arka Planda Neler Gerçekleştirecek? (Detaylar için tıklayın)</summary>

1. **CLI Araçları Kurulumu** — Komut satırına `agent-reach` aracı kurulur.
2. **Sistem Gereksinimleri** — Node.js, `gh CLI`, `mcporter`, `bird` vb. algılanır ve kurulur.
3. **Arama Motorları Konfigürasyonu** — Exa.ai arama motoru MCP üzerinden ayarlanır (API anahtarı gerekmez).
4. **Çevre (Ortam) Algılama** — Yerel bir bilgisayarda mı yoksa sunucuda mı olduğunuzu algılar ve tavsiye verir.
5. **SKILL.md Eklemesi** — Ajanınızın ana dizinine "SKILL.md" dosyasını yazar, böylece bir dahaki sefere "Twitter'dan ara" dediğinizde aracı nasıl kullanması gerektiğini otomatik okur/öğrenir.

Yüklendikten sonra `agent-reach doctor` komutu ile sistemin anlık çalışabilirlik durumunu test edebilirsiniz.
</details>

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
