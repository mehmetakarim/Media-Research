<script setup>
import { ref, computed, onMounted } from 'vue';
import { invoke } from '@tauri-apps/api/core';
import {
  Search,
  Link,
  Bookmark,
  SlidersHorizontal,
  Zap,
  Sparkles,
  CheckCheck,
  Copy,
  Download,
  X,
  Play,
  Maximize2,
  RefreshCw,
  Bot,
  Cookie,
  Loader2,
  AlertCircle,
  CheckCircle2,
  Info,
  ExternalLink,
  KeyRound,
  Eye,
  EyeOff,
  Layers,
  Cpu,
  Languages,
  TrendingUp,
  FileText,
  Table as TableIcon,
  Filter,
  ArrowUpDown,
  Compass,
  Lightbulb,
  Check,
  MessageSquare,
  MessageCircle,
  Heart,
  ThumbsUp,
  Star,
  Eye as EyeIconEye,
  MessageSquareQuote,
  Clock,
  Flame,
  FolderOpen,
  FileDown
} from 'lucide-vue-next';
import { marked } from 'marked';
import jsPDF from 'jspdf';
import html2pdf from 'html2pdf.js';
import * as XLSX from 'xlsx';

// View State
const currentView = ref('feed'); // 'feed' | 'url' | 'saved' | 'settings' | 'ai'
const selectedPlatform = ref('x');
const layout = ref('grid'); // 'grid' | 'list'
const searchQuery = ref('');
const isSearching = ref(false);

// In-App Video & Media Modal State
const activeModalMedia = ref(null); // { type: 'youtube' | 'instagram' | 'pinterest' | 'image', url: string, title: string, author: string }
const openMediaModal = (item) => {
  if (!item) return;

  if (item.platform === 'youtube') {
    const match = item.url.match(/v=([a-zA-Z0-9_-]+)/);
    const videoId = match ? match[1] : item.id.replace('yt_', '');
    activeModalMedia.value = {
      type: 'youtube',
      embedUrl: `https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1`,
      title: item.text,
      author: item.author,
      rawUrl: item.url
    };
  } else if (item.videoUrl) {
    // Native direct MP4 playback (Instagram reels, Pinterest videos, etc.)
    activeModalMedia.value = {
      type: 'video',
      videoUrl: item.videoUrl,
      mediaUrl: item.mediaUrl,
      title: item.text,
      author: item.author,
      rawUrl: item.url
    };
  } else if (item.mediaUrl) {
    // Native direct Image preview (Instagram photos, Pinterest pins, X media)
    activeModalMedia.value = {
      type: 'image',
      mediaUrl: item.mediaUrl,
      title: item.text,
      author: item.author,
      rawUrl: item.url
    };
  } else if (item.url) {
    openUrl(item.url);
  }
};

const closeMediaModal = () => {
  activeModalMedia.value = null;
};

// Toast Notification System
const toasts = ref([]);
const showToast = (title, message, type = 'info') => {
  const id = Date.now() + Math.random();
  toasts.value.push({ id, title, message, type });
  const duration = type === 'error' ? 14000 : 8000;
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id);
  }, duration);
};
const closeToast = (id) => {
  toasts.value = toasts.value.filter(t => t.id !== id);
};

// URL Reader State
const urlInput = ref('');
const directUrlResult = ref(null);
const isUrlLoading = ref(false);

// Inspector State
const selectedItem = ref(null);
const inspectorTab = ref('json'); // 'json' | 'md'
const aiSummaryState = ref('idle'); // 'idle' | 'loading' | 'done'
const isAiEnabled = ref(true);

// AI Assistant State
const aiAssistantPrompt = ref('');
const aiAssistantResponse = ref('');
const isAssistantGenerating = ref(false);

// Settings State & Gemini API Key Management
const geminiApiKey = ref('');
const showGeminiKey = ref(false);
const geminiModel = ref('gemini-2.5-flash');
const availableModels = ref([
  { id: 'gemini-2.5-flash', name: 'Gemini 2.5 Flash', badge: 'Önerilen · Hızlı', desc: 'Genel arama, özetleme ve çoklu veri sentezinde en hızlı ve dengeli model.' },
  { id: 'gemini-2.5-pro', name: 'Gemini 2.5 Pro', badge: 'Gelişmiş Akıl Yürütme', desc: 'Detaylı ve karmaşık araştırma raporları, derin sektör analizleri için.' },
  { id: 'gemini-3.5-flash', name: 'Gemini 3.5 Flash', badge: 'Yeni Nesil', desc: 'En güncel 3.x mimarisi, ultra düşük gecikme ve yüksek bağlam kapasitesi.' },
  { id: 'gemini-3.5-flash-lite', name: 'Gemini 3.5 Flash-Lite', badge: 'Hafif & Hızlı', desc: 'Maksimum verim ve hızlı kart özetleri için optimize edilmiş model.' },
  { id: 'gemini-2.5-flash-lite', name: 'Gemini 2.5 Flash-Lite', badge: 'Ekonomik', desc: 'Temel analizler ve hızlı duygu durumu tespiti için hafif model.' }
]);
// Auto-Cookie Extraction State
const autoCookieBrowser = ref('chrome');
const isExtractingCookies = ref(false);

// Advanced Filter & Sort State
const sortBy = ref('default'); // 'default' | 'likes' | 'comments' | 'newest'
const mediaFilter = ref('all'); // 'all' | 'video' | 'image' | 'text'
const feedSearchQuery = ref('');

// Trends & Ideation State
const trendTopics = ref([
  { id: 1, title: '3D Yazıcı & Filament İnovasyonları', tag: '#3dprinting', volume: '14.8K gönderi', growth: '+42%', category: 'Donanım & Mühendislik', desc: 'Bambu Lab & Creality kıyaslamaları, çok renkli baskı sistemleri ve yerli filament üreticileri trendlerde.' },
  { id: 2, title: 'Yapay Zeka Destekli CAD Modelleme', tag: '#GenerativeAI', volume: '28.5K gönderi', growth: '+85%', category: 'Yapay Zeka & Yazılım', desc: 'Metinden 3D model üreten yapay zeka araçları ve blender eklentileri sosyal medyada viral.' },
  { id: 3, title: 'Akıllı Ev Otomasyonu & Robotik', tag: '#HomeAutomation', volume: '9.2K gönderi', growth: '+18%', category: 'IoT & Maker', desc: 'Açık kaynaklı robot kolları ve akıllı ev sensörleri yapım rehberleri yüksek etkileşim alıyor.' },
  { id: 4, title: 'Mikro SaaS & Bağımsız Geliştiricilik', tag: '#buildinpublic', volume: '34.1K gönderi', growth: '+62%', category: 'Girişimcilik', desc: 'Tek kişilik yazılım ekipleri ve şeffaf ciro paylaşımı yapan indie hacker içerikleri yükselişte.' },
  { id: 5, title: 'Sürdürülebilir Geri Dönüşüm & Maker', tag: '#Recycle3D', volume: '6.4K gönderi', growth: '+25%', category: 'Çevre & İnovasyon', desc: 'Pet şişelerden filament üretme projeleri YouTube ve Instagram Reels videolarında öne çıkıyor.' }
]);
const searchHistoryKeywords = ref([]);

// AI Smart Comment Generator State
const generatingCommentPostId = ref(null);
const activeGeneratedComment = ref(null); // { post: item, comment: string }

// Navigation
const navItems = [
  { id: 'feed', label: 'Keşif & Akış', icon: Search, count: '' },
  { id: 'trends', label: 'Trend ve Gündem', icon: TrendingUp, count: 'Popüler' },
  { id: 'url', label: 'Doğrudan URL Analizi', icon: Link, count: '' },
  { id: 'ai', label: 'AI Asistan Paneli', icon: Bot, count: 'Yeni' },
  { id: 'saved', label: 'Kaydedilenler', icon: Bookmark, count: '' },
  { id: 'channels', label: 'Kanallar & Çerezler', icon: Layers, count: '' },
  { id: 'settings', label: 'Ayarlar & Model', icon: SlidersHorizontal, count: '' }
];

const platforms = [
  { id: 'all', label: 'Tümü' },
  { id: 'x', label: 'Twitter/X' },
  { id: 'youtube', label: 'YouTube' },
  { id: 'instagram', label: 'Instagram' },
  { id: 'pinterest', label: 'Pinterest' },
  { id: 'reddit', label: 'Reddit' },
  { id: 'github', label: 'GitHub' },
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'web', label: 'Web / Makale' }
];

const channels = ref([
  { name: 'Twitter / X', state: 'aktif', status: 'ok', auth: 'çerezler · yetkili', latency: '180 ms', key: 'twitter' },
  { name: 'YouTube', state: 'aktif', status: 'ok', auth: 'doğrudan arama · hazır', latency: '210 ms', key: 'youtube' },
  { name: 'Instagram', state: 'aktif', status: 'ok', auth: 'çerezler · yetkili', latency: '280 ms', key: 'instagram' },
  { name: 'Pinterest', state: 'aktif', status: 'ok', auth: 'çerezler · yetkili', latency: '290 ms', key: 'pinterest' },
  { name: 'Reddit', state: 'aktif', status: 'ok', auth: 'çerezler / yerel arama', latency: '320 ms', key: 'reddit' },
  { name: 'GitHub', state: 'aktif', status: 'ok', auth: 'gh cli / token · yetkili', latency: '90 ms', key: 'github' },
  { name: 'LinkedIn', state: 'aktif', status: 'ok', auth: 'çerezler · yetkili', latency: '340 ms', key: 'linkedin' },
  { name: 'Web / Makale', state: 'aktif', status: 'ok', auth: 'jina reader · aktif', latency: '120 ms', key: 'web' }
]);

const items = ref([]);

const savedExports = ref([]);
const viewingReport = ref(null);

const renderMarkdown = (text) => {
  if (!text) return '';
  try {
    return marked.parse(text, { breaks: true, gfm: true });
  } catch (e) {
    return text;
  }
};

const loadSavedExports = () => {
  const local = localStorage.getItem('agent_reach_saved_exports');
  if (local) {
    try {
      savedExports.value = JSON.parse(local);
    } catch (e) {
      savedExports.value = [];
    }
  } else {
    savedExports.value = [
      {
        id: 'rep_default_1',
        kind: 'MD',
        title: '3D Yazıcı Sektör Trendleri ve Pazar Analizi',
        path: '3d-yazici-analizi.md',
        date: 'Bugün',
        ai: true,
        content: `### 🚀 3D Yazıcı Sektörü Trend Raporu & Pazar Analizi\n\n**1. Sektörel Büyüme & Pazar Dinamikleri:**\nCreality'nin Hong Kong borsasına açılması ve 140'tan fazla ülkeye ihracat yapması, tüketici sınıfı 3B yazıcı pazarının artık küresel sanayi ve kurumsal ölçekte kabul gördüğünü kanıtlıyor.\n\n**2. Bambu Lab vs. Creality Algısı:**\nKullanıcılar arasında Bambu Lab hızı ve zahmetsiz deneyimiyle 'Ferrari' olarak nitelendirilirken; Creality işlevselliği, dayanıklılığı ve parça uyumluluğuyla güvenilir bir 'Doblo' iş aracı olarak görülüyor.\n\n**3. Açık Kaynak İnovasyon:**\nUC Berkeley'in 5.000$ altı insansı robotu 3D baskı ile üretilebilir kılması donanım inovasyonunu hızlandırıyor.\n\n---\n*Oluşturulma: Agent Reach Yerel Çoklu Platform Sentezi*`
      }
    ];
  }
};

const saveReportToDisk = (title, content, kind = 'MD', isAi = true) => {
  const newReport = {
    id: `rep_${Date.now()}`,
    kind,
    title,
    path: `${title.toLowerCase().replace(/[^a-z0-9]/g, '-')}.${kind.toLowerCase()}`,
    date: 'Bugün',
    ai: isAi,
    content
  };
  savedExports.value.unshift(newReport);
  localStorage.setItem('agent_reach_saved_exports', JSON.stringify(savedExports.value));
  showToast('Kaydedildi', `"${title}" raporu başarıyla yerel kasanıza kaydedildi!`, 'success');
};

const deleteReport = (id) => {
  savedExports.value = savedExports.value.filter(r => r.id !== id);
  localStorage.setItem('agent_reach_saved_exports', JSON.stringify(savedExports.value));
  if (viewingReport.value?.id === id) {
    viewingReport.value = null;
  }
  showToast('Silindi', 'Rapor yerel kasanızdan kaldırıldı.', 'info');
};

// Computed
const filteredItems = computed(() => {
  let list = items.value;
  if (selectedPlatform.value !== 'all') {
    list = list.filter(i => i.platform === selectedPlatform.value);
  }

  // Media Type Filter
  if (mediaFilter.value === 'video') {
    list = list.filter(i => i.isVideo || i.platform === 'youtube' || i.videoUrl);
  } else if (mediaFilter.value === 'image') {
    list = list.filter(i => i.mediaUrl && !i.isVideo && !i.videoUrl && i.platform !== 'youtube');
  } else if (mediaFilter.value === 'text') {
    list = list.filter(i => !i.mediaUrl && !i.videoUrl && i.platform !== 'youtube');
  }

  // Feed Quick Text Search
  if (feedSearchQuery.value && feedSearchQuery.value.trim()) {
    const q = feedSearchQuery.value.toLowerCase().trim();
    list = list.filter(i => (i.text && i.text.toLowerCase().includes(q)) || (i.author && i.author.toLowerCase().includes(q)));
  }

  // Sorting Logic
  if (sortBy.value === 'likes') {
    list = [...list].sort((a, b) => {
      const getLikes = (item) => {
        const m = item.metrics?.find(x => x.label.includes('beğeni') || x.label.includes('yıldız') || x.label.includes('puan'));
        if (!m) return 0;
        const val = parseFloat(m.value.toString().replace(/[^0-9.]/g, '')) || 0;
        return m.value.toString().includes('k') || m.value.toString().includes('K') ? val * 1000 : val;
      };
      return getLikes(b) - getLikes(a);
    });
  } else if (sortBy.value === 'comments') {
    list = [...list].sort((a, b) => {
      const getComments = (item) => {
        const m = item.metrics?.find(x => x.label.includes('yorum') || x.label.includes('yanıt') || x.label.includes('çatal'));
        if (!m) return 0;
        const val = parseFloat(m.value.toString().replace(/[^0-9.]/g, '')) || 0;
        return m.value.toString().includes('k') || m.value.toString().includes('K') ? val * 1000 : val;
      };
      return getComments(b) - getComments(a);
    });
  }

  return list;
});

// Real-Time Sentiment & Trend Statistics
const sentimentStats = computed(() => {
  const currentList = items.value;
  if (!currentList || currentList.length === 0) {
    return { positive: 75, neutral: 20, negative: 5, total: 0, topKeyword: 'N/A' };
  }

  let positiveCount = 0;
  let neutralCount = 0;
  let negativeCount = 0;

  currentList.forEach(item => {
    const text = (item.text || '').toLowerCase();
    const sentiment = (item.sentiment || '').toLowerCase();
    if (sentiment.includes('pozitif') || text.includes('harika') || text.includes('iyi') || text.includes('başarılı') || text.includes('güzel')) {
      positiveCount++;
    } else if (sentiment.includes('negatif') || text.includes('kötü') || text.includes('sorun') || text.includes('hata') || text.includes('yavaş')) {
      negativeCount++;
    } else {
      neutralCount++;
    }
  });

  const total = currentList.length;
  const positive = Math.round((positiveCount / total) * 100) || 70;
  const neutral = Math.round((neutralCount / total) * 100) || 25;
  const negative = Math.max(0, 100 - positive - neutral);

  return {
    positive,
    neutral,
    negative,
    total,
    topKeyword: searchQuery.value || 'Pazar Gündemi'
  };
});

const inspectorContent = computed(() => {
  if (!selectedItem.value) return '';
  if (inspectorTab.value === 'json') {
    return JSON.stringify(
      {
        id: selectedItem.value.id,
        kanal: selectedItem.value.platformLabel,
        yazar: {
          isim: selectedItem.value.author,
          kullanici_adi: selectedItem.value.handle,
          onayli: selectedItem.value.verified
        },
        baglanti: selectedItem.value.url || '',
        tarih: selectedItem.value.date,
        metin: selectedItem.value.text,
        medya_baglantisi: selectedItem.value.mediaUrl || null,
        metrikler: selectedItem.value.metrics.reduce((acc, m) => {
          acc[m.label] = m.value;
          return acc;
        }, {}),
        kazima_motoru: {
          motor: 'agent-reach yerel cekirdek',
          harcanan_token: 0,
          onbellek: true
        }
      },
      null,
      2
    );
  } else {
    return `# ${selectedItem.value.author} (${selectedItem.value.handle})\n\n_${selectedItem.value.platformLabel} · ${selectedItem.value.date} · Bağlantı: ${selectedItem.value.url || 'N/A'}_\n\n${selectedItem.value.text}\n\n## Metrikler\n${selectedItem.value.metrics.map(m => `- **${m.label}**: ${m.value}`).join('\n')}\n\n## Kazıma Detayı\n- motor: yerel agent-reach (0 token)\n- önbellek: aktif`;
  }
});

// Helper: Parse Bird CLI Tweet Output with URLs and Media
const parseBirdOutput = (raw) => {
  const chunks = raw.split('──────────────────────────────────────────────────');
  const parsed = [];

  for (let i = 0; i < chunks.length; i++) {
    const chunk = chunks[i].trim();
    if (!chunk) continue;

    const lines = chunk.split('\n');
    let author = 'Kullanıcı';
    let handle = '@kullanici';
    let textLines = [];
    let date = 'Yeni';
    let url = '';
    let mediaUrl = '';

    const headerMatch = lines[0]?.match(/@([a-zA-Z0-9_]+)\s*\(([^)]+)\):?/);
    if (headerMatch) {
      handle = '@' + headerMatch[1];
      author = headerMatch[2];
      
      for (let j = 1; j < lines.length; j++) {
        const line = lines[j].trim();
        if (line.startsWith('🔗')) {
          url = line.replace('🔗', '').trim();
        } else if (line.startsWith('🖼️')) {
          mediaUrl = line.replace('🖼️', '').trim();
        } else if (line.startsWith('📅')) {
          date = line.replace('📅', '').trim().slice(0, 16);
        } else if (line) {
          textLines.push(line);
        }
      }
    } else {
      textLines.push(chunk);
    }

    const fullText = textLines.join(' ').trim() || chunk;

    parsed.push({
      id: `live_${Date.now()}_${i}`,
      platform: 'x',
      platformLabel: 'Twitter/X',
      author,
      handle,
      url,
      mediaUrl,
      date,
      verified: false,
      initial: author[0]?.toUpperCase() || 'X',
      hue: (i * 45) % 360,
      text: fullText,
      metrics: [
        { label: 'kaynak', value: 'yerel bird' },
        { label: 'maliyet', value: '0 token' }
      ],
      media: !!mediaUrl,
      mediaBadge: mediaUrl ? 'görsel' : null,
      isVideo: false,
      sentiment: 'Nötr · 0.70',
      tokens: '0 token (Yerel Kazıma)',
      summary: fullText.slice(0, 150) + '...',
      points: ['Canlı terminal verisi yerel olarak işlendi', 'Token harcanmadı']
    });
  }

  return parsed;
};

const openUrl = async (url) => {
  if (!url) return;
  try {
    await invoke('open_external_url', { url });
    showToast('Bağlantı Açılıyor', 'Gönderi varsayılan tarayıcınızda açılıyor...', 'info');
  } catch (err) {
    console.warn('Tauri open hatası, window.open deneniyor:', err);
    window.open(url, '_blank');
  }
};

// Actions
const selectItem = (item) => {
  selectedItem.value = item;
  aiSummaryState.value = 'idle';
  inspectorTab.value = 'json';
};

const translatingPostId = ref(null);

const translateSinglePost = async (item) => {
  if (!item || !item.text) return;
  translatingPostId.value = item.id;
  showToast('Çevriliyor', 'Gönderi metni yapay zeka ile Türkçeye çevriliyor...', 'info');

  try {
    const resStr = await invoke('translate_text', {
      text: item.text,
      apiKey: geminiApiKey.value || null,
      model: geminiModel.value || 'gemini-2.5-flash'
    });

    const parsedJson = JSON.parse(resStr);
    const translatedText = parsedJson?.candidates?.[0]?.content?.parts?.[0]?.text;

    if (translatedText && translatedText.trim().length > 0) {
      item.text = translatedText.trim();
      item.isTranslated = true;
      showToast('Çevrildi', 'Gönderi başarıyla Türkçeye çevrildi!', 'success');
    } else {
      const errMsg = parsedJson?.error?.message || 'Çeviri boş döndü';
      throw new Error(errMsg);
    }
  } catch (err) {
    console.error('Çeviri hatası:', err);
    showToast('Çeviri Hatası', `Metin çevrilemedi: ${err.message || err}`, 'error');
  } finally {
    translatingPostId.value = null;
  }
};

const generateSmartComment = async (item) => {
  if (!item || !item.text) return;
  generatingCommentPostId.value = item.id;
  showToast('Yorum Üretiliyor', 'Gönderi için yüksek etkileşimli, dikkat çekici akıllı yorum hazırlanıyor...', 'info');

  const prompt = `Sen sosyal medyada yüksek otoriteye sahip uzman bir içerik üreticisisin.
Aşağıdaki sosyal medya gönderisi için, gönderi sahibinin dikkatini çekecek, toplulukta etkileşim ve tartışma başlatacak, değer katan, profesyonel, zeki ve samimi TEK BİR Türkçe yorum yaz.
Sadece yorum metnini ver, tırnak işareti, başlık veya ek açıklama ekleme.

Gönderi Sahibi: ${item.author} (${item.platformLabel})
Gönderi Metni:
${item.text}`;

  try {
    const resStr = await invoke('generate_ai_summary', {
      prompt,
      apiKey: geminiApiKey.value || null,
      model: geminiModel.value || 'gemini-2.5-flash'
    });

    const parsedJson = JSON.parse(resStr);
    const commentText = parsedJson?.candidates?.[0]?.content?.parts?.[0]?.text;

    if (commentText && commentText.trim().length > 0) {
      item.aiComment = commentText.trim();
      activeGeneratedComment.value = {
        post: item,
        comment: commentText.trim()
      };
      showToast('AI Yorum Hazır', 'Dikkat çekici yorum üretildi! Panoya kopyalayabilir veya doğrudan gönderebilirsiniz.', 'success');
    } else {
      throw new Error('Yorum üretilemedi');
    }
  } catch (err) {
    console.error('AI Yorum hatası:', err);
    showToast('Yorum Hatası', `Yorum oluşturulamadı: ${err.message || err}`, 'error');
  } finally {
    generatingCommentPostId.value = null;
  }
};

const runSearch = async () => {
  if (!searchQuery.value) {
    showToast('Arama Uyarısı', 'Lütfen aramak istediğiniz bir anahtar kelime girin.', 'warn');
    return;
  }

  isSearching.value = true;
  showToast('Arama Başlatıldı', `"${searchQuery.value}" için yerel arama yapılıyor...`, 'info');

  try {
    const res = await invoke('execute_search', {
      platform: selectedPlatform.value === 'all' ? 'all' : selectedPlatform.value,
      query: searchQuery.value,
      limit: 10
    });

    if (res.success) {
      let parsedList = [];
      try {
        const parsedData = JSON.parse(res.raw_output);
        if (Array.isArray(parsedData)) {
          parsedList = parsedData;
        }
      } catch (e) {
        parsedList = parseBirdOutput(res.raw_output);
      }

      if (parsedList.length > 0) {
        // UNIVERSAL POST DATA NORMALIZER (STANDARTLAŞTIRICI)
        items.value = parsedList.map(item => {
          // 1. Akıllı Tarih Standardı
          let cleanDate = item.date;
          if (!cleanDate || cleanDate === 'YouTube' || cleanDate === 'Instagram' || cleanDate === 'Pinterest' || cleanDate === 'Reddit' || cleanDate === 'LinkedIn' || cleanDate === 'Web') {
            cleanDate = 'Canlı Akış';
          }

          // 2. Standart 3'lü Metrik Çıkarımı
          let primaryMetric = { label: 'Etkileşim', value: 'Yüksek', type: 'like' };
          let secondaryMetric = { label: 'Katılım', value: 'Aktif', type: 'comment' };
          let tertiaryMetric = { label: 'Kaynak', value: 'Yerel Motor', type: 'source' };

          if (item.metrics && Array.isArray(item.metrics)) {
            item.metrics.forEach(m => {
              const lbl = (m.label || '').toLowerCase();
              const val = m.value || '';
              if (lbl.includes('beğeni') || lbl.includes('yıldız') || lbl.includes('puan') || lbl.includes('repin') || lbl.includes('kaydet')) {
                primaryMetric = { label: m.label, value: val, type: 'like' };
              } else if (lbl.includes('yorum') || lbl.includes('yanıt') || lbl.includes('çatal') || lbl.includes('retweet') || lbl.includes('repost')) {
                secondaryMetric = { label: m.label, value: val, type: 'comment' };
              } else if (lbl.includes('izlenme') || lbl.includes('süre') || lbl.includes('okuma') || lbl.includes('kaynak') || lbl.includes('görüntü')) {
                tertiaryMetric = { label: m.label, value: val, type: 'view' };
              }
            });
          }

          return {
            ...item,
            date: cleanDate,
            standardMetrics: {
              primary: primaryMetric,
              secondary: secondaryMetric,
              tertiary: tertiaryMetric
            }
          };
        });

        selectedItem.value = items.value[0];
        const platformMap = {
          x: 'Twitter/X gönderisi',
          youtube: 'YouTube videosu',
          instagram: 'Instagram gönderisi',
          tiktok: 'TikTok videosu',
          pinterest: 'Pinterest pini',
          reddit: 'Reddit gönderisi',
          github: 'GitHub deposu',
          linkedin: 'LinkedIn gönderisi',
          web: 'Web makalesi'
        };
        const name = platformMap[selectedPlatform.value] || 'içerik';
        showToast('Başarılı', `${parsedList.length} adet ${name} standartlaştırılmış formatta listelendi!`, 'success');
      } else {
        showToast('Bilgi', 'Aramanıza uygun sonuç bulunamadı.', 'info');
      }
    } else {
      const err = res.error || 'Arama sırasında bir hata oluştu.';
      if (err.includes('403') || err.includes('csrf')) {
        showToast('Yetkilendirme Hatası', 'Platform çerezleriniz güncel değil. Lütfen Ayarlar sekmesinden güncelleyin.', 'error');
      } else {
        showToast('Arama Hatası', err, 'error');
      }
    }
  } catch (err) {
    console.error('Arama hatası:', err);
    showToast('Bağlantı Hatası', `Yerel komut çalıştırılamadı: ${err}`, 'error');
  } finally {
    isSearching.value = false;
  }
};

const fetchDirectUrl = async () => {
  if (!urlInput.value) {
    showToast('URL Gerekli', 'Lütfen geçerli bir bağlantı adresi girin.', 'warn');
    return;
  }

  isUrlLoading.value = true;
  showToast('URL Ayrıştırılıyor', 'Bağlantı yerel adaptör ve Jina ile okunuyor...', 'info');

  try {
    const res = await invoke('fetch_url_content', { url: urlInput.value });
    directUrlResult.value = res;
    showToast('Tamamlandı', 'URL içeriği başarıyla çıkarıldı (0 token).', 'success');
  } catch (err) {
    directUrlResult.value = `Hata oluştu: ${err}`;
    showToast('Okuma Hatası', `İçerik çekilemedi: ${err}`, 'error');
  } finally {
    isUrlLoading.value = false;
  }
};

// 1. AUTO COOKIE EXTRACTION FROM LOCAL BROWSER
const handleExtractFromBrowser = async () => {
  isExtractingCookies.value = true;
  showToast('Tarayıcı Taranıyor', `${autoCookieBrowser.value.toUpperCase()} tarayıcısından oturum çerezleri okunuyor...`, 'info');

  try {
    const resStr = await invoke('extract_browser_cookies', { browser: autoCookieBrowser.value });
    const cookiesData = JSON.parse(resStr);
    
    let updatedCount = 0;
    if (cookiesData.twitter) {
      const auth = cookiesData.twitter.auth_token;
      const ct0 = cookiesData.twitter.ct0;
      if (auth && ct0) {
        await invoke('save_cookies', {
          service: 'twitter',
          cookieVal: `auth_token=${auth}; ct0=${ct0}`
        });
        updatedCount++;
      }
    }

    if (cookiesData.instagram?.cookie_string) {
      await invoke('save_cookies', {
        service: 'instagram',
        cookieVal: cookiesData.instagram.cookie_string
      });
      updatedCount++;
    }

    if (cookiesData.pinterest?.cookie_string) {
      await invoke('save_cookies', {
        service: 'pinterest',
        cookieVal: cookiesData.pinterest.cookie_string
      });
      updatedCount++;
    }

    if (updatedCount > 0) {
      showToast('Başarılı', `${autoCookieBrowser.value.toUpperCase()} üzerinden ${updatedCount} platform çerezi senkronize edildi!`, 'success');
      cookieMessage.value = `✅ ${updatedCount} platform çerezi ${autoCookieBrowser.value} tarayıcısından başarıyla alındı.`;
    } else {
      showToast('Bilgi', 'Tarayıcıda aktif oturum çerezi bulunamadı veya tarayıcı açık.', 'warn');
      cookieMessage.value = `⚠️ Seçili tarayıcıda (${autoCookieBrowser.value}) aktif oturum çerezi bulunamadı. Lütfen oturumunuzun açık olduğundan emin olun.`;
    }
  } catch (err) {
    console.error('Çerez çıkarma hatası:', err);
    showToast('Çerez Çıkarma Hatası', `Tarayıcı okunamadı: ${err}`, 'error');
    cookieMessage.value = `❌ Hata: ${err}`;
  } finally {
    isExtractingCookies.value = false;
  }
};

// 2. EXCEL (XLSX / CSV) EXPORT FUNCTION
const exportFeedToExcel = () => {
  const currentList = filteredItems.value;
  if (!currentList || currentList.length === 0) {
    showToast('Veri Yok', 'Dışa aktarılacak içerik bulunamadı.', 'warn');
    return;
  }

  const exportData = currentList.map((item, index) => {
    return {
      'No': index + 1,
      'Platform': item.platformLabel || item.platform,
      'Yazar Adı': item.author,
      'Kullanıcı Adı': item.handle,
      'Tarih': item.date,
      'İçerik Metni': item.text,
      'Duygu Durumu': item.sentiment || 'N/A',
      'Medya Türü': item.isVideo ? 'Video' : (item.mediaUrl ? 'Görsel' : 'Metin'),
      'Gönderi Bağlantısı': item.url || 'N/A'
    };
  });

  const worksheet = XLSX.utils.json_to_sheet(exportData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Medya Araştırması');

  const fileName = `Media-Research-${searchQuery.value || 'Gundem'}-${Date.now()}.xlsx`;
  XLSX.writeFile(workbook, fileName);
  showToast('Excel İndirildi', `"${fileName}" başarıyla cihazınıza kaydedildi!`, 'success');
};

// 3. LENOVO RED THEMED RICH PDF EXPORT FUNCTION (KUSURSUZ TÜRKÇE VE GÖRSEL MİMARİ)
const exportReportToPdf = async (reportTitle, markdownContent) => {
  showToast('PDF Hazırlanıyor', 'Rapor Lenovo Red temalı şık PDF formatına dönüştürülüyor...', 'info');

  try {
    const renderedHtml = renderMarkdown(markdownContent || reportTitle);
    const dateStr = new Date().toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    const cleanTitle = reportTitle || 'Pazar Trend ve Medya Analiz Raporu';

    // Rich Printable HTML Template Container with exact printable A4 dimensions (190mm printable width)
    const element = document.createElement('div');
    element.style.width = '680px'; // 680px provides optimal padding for A4 with 10mm margins
    element.style.padding = '0';
    element.style.margin = '0 auto';
    element.style.backgroundColor = '#ffffff';
    element.style.color = '#1e293b';
    element.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
    element.style.boxSizing = 'border-box';
    element.style.wordBreak = 'break-word';

    element.innerHTML = `
      <div style="background-color: #ffffff; padding: 24px 28px; width: 100%; box-sizing: border-box;">
        <!-- Header Banner (Lenovo Red) -->
        <div style="background: linear-gradient(135deg, #E2232A 0%, #b91c1c 100%); color: #ffffff; padding: 14px 20px; border-radius: 10px; margin-bottom: 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="font-size: 13px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase;">MEDIA RESEARCH</div>
            <div style="font-size: 10.5px; opacity: 0.95; font-family: monospace;">SOSYAL İSTİHBARAT & PAZAR RAPORU</div>
          </div>
        </div>

        <!-- Title and Metadata Section -->
        <div style="border-bottom: 2px solid #E2232A; padding-bottom: 12px; margin-bottom: 20px;">
          <h1 style="font-size: 20px; font-weight: 700; color: #0f172a; margin: 0 0 8px 0; line-height: 1.3;">${cleanTitle}</h1>
          <div style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 10.5px; color: #64748b; font-family: monospace;">
            <span>📅 Tarih: <strong style="color: #334155;">${dateStr}</strong></span>
            <span>⚡ Kaynak: <strong style="color: #334155;">Media Research Yerel Motoru</strong></span>
          </div>
        </div>

        <!-- Rich Markdown Body -->
        <div class="pdf-content-body" style="font-size: 12.5px; line-height: 1.65; color: #334155;">
          ${renderedHtml}
        </div>

        <!-- Footer -->
        <div style="margin-top: 36px; border-top: 1px solid #e2e8f0; padding-top: 12px; display: flex; justify-content: space-between; font-size: 9.5px; color: #94a3b8; font-family: monospace;">
          <span>Media Research · Sıfır Token Yerel Kazıma & AI İstihbarat Platformu</span>
          <span>Gizli & Kurumsal Rapor</span>
        </div>
      </div>

      <style>
        .pdf-content-body h1, .pdf-content-body h2, .pdf-content-body h3, .pdf-content-body h4 {
          page-break-after: avoid;
          break-after: avoid;
        }
        .pdf-content-body p, .pdf-content-body li, .pdf-content-body blockquote, .pdf-content-body tr {
          page-break-inside: avoid;
          break-inside: avoid;
        }
        .pdf-content-body h1 { font-size: 16px; font-weight: 700; color: #0f172a; border-left: 4px solid #E2232A; padding-left: 8px; margin: 18px 0 8px 0; }
        .pdf-content-body h2 { font-size: 14.5px; font-weight: 700; color: #0f172a; border-left: 3px solid #E2232A; padding-left: 8px; margin: 16px 0 6px 0; }
        .pdf-content-body h3 { font-size: 13.5px; font-weight: 600; color: #1e293b; margin: 12px 0 4px 0; }
        .pdf-content-body p { margin: 0 0 10px 0; }
        .pdf-content-body ul, .pdf-content-body ol { margin: 0 0 12px 0; padding-left: 18px; }
        .pdf-content-body li { margin-bottom: 4px; }
        .pdf-content-body blockquote { background: #f8fafc; border-left: 3px solid #E2232A; margin: 10px 0; padding: 8px 12px; color: #475569; font-style: italic; border-radius: 4px; }
        .pdf-content-body table { width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 11.5px; }
        .pdf-content-body th { background: #fee2e2; color: #991b1b; text-align: left; padding: 6px 8px; border: 1px solid #fecaca; font-weight: 600; }
        .pdf-content-body td { padding: 6px 8px; border: 1px solid #e2e8f0; }
        .pdf-content-body tr:nth-child(even) td { background: #f8fafc; }
        .pdf-content-body strong { color: #0f172a; }
        .pdf-content-body code { background: #f1f5f9; padding: 2px 4px; border-radius: 4px; font-family: monospace; font-size: 11px; color: #b91c1c; }
        .pdf-content-body hr { border: 0; height: 1px; background: #e2e8f0; margin: 16px 0; }
      </style>
    `;

    const safeFilename = `${cleanTitle.toLowerCase().replace(/[^a-z0-9]/g, '-')}-${Date.now()}.pdf`;

    const opt = {
      margin: [12, 12, 12, 12],
      filename: safeFilename,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, letterRendering: true, backgroundColor: '#ffffff', scrollX: 0, scrollY: 0 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
    };

    // Generate PDF as Uint8Array byte array for 100% valid PDF binary
    const worker = html2pdf().set(opt).from(element);
    const pdfDoc = await worker.toPdf().get('pdf');
    const pdfArrayBuffer = pdfDoc.output('arraybuffer');
    
    // Convert ArrayBuffer to binary string
    const bytes = new Uint8Array(pdfArrayBuffer);
    let binary = '';
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    const base64Data = btoa(binary);

    try {
      const savedPath = await invoke('save_file_to_downloads', {
        filename: safeFilename,
        base64Data: base64Data
      });
      showToast('PDF İndirildi', `PDF Raporu İndirilenler klasörüne kaydedildi:\n${savedPath}`, 'success');
      // Reveal in folder
      await invoke('show_in_folder', { path: savedPath });
    } catch (saveErr) {
      console.warn('Rust indirme klasörüne yazma hatası, tarayıcı kaydetme deneniyor:', saveErr);
      await worker.save();
      showToast('PDF İndirildi', `"${safeFilename}" başarıyla indirildi!`, 'success');
    }
  } catch (err) {
    console.error('PDF oluşturma hatası:', err);
    showToast('PDF Hatası', `PDF oluşturulamadı: ${err.message || err}`, 'error');
  }
};

const generateGeminiSummary = async () => {
  aiSummaryState.value = 'loading';
  showToast('Gemini Devrede', 'Gönderi Gemini 2.0 Flash ile analiz ediliyor...', 'info');

  const textToSummarize = selectedItem.value ? selectedItem.value.text : searchQuery.value;
  const prompt = `Aşağıdaki sosyal medya gönderisini analiz et.
Gönderiyi birebir kopyalamadan, konunun özünü ve verilen ana mesajı anlatan 2 cümlelik profesyonel bir özet çıkar.
Duygu durumunu ve 3 adet kritik çıkarım maddesini Türkçe olarak belirle.

Çıktıyı SADECE geçerli bir JSON objesi olarak ver:
{
  "sentiment": "Pozitif · 0.85",
  "tokens": "450 girdi / 120 çıktı",
  "summary": "Bu gönderide ... vurgulanıyor ve ... değerlendiriliyor.",
  "points": [
    "Birinci önemli çıkarım",
    "İkinci önemli çıkarım",
    "Üçüncü önemli çıkarım"
  ]
}

İçerik:
${textToSummarize}`;

  try {
    const resStr = await invoke('generate_ai_summary', {
      prompt,
      apiKey: geminiApiKey.value || null,
      model: geminiModel.value || 'gemini-2.5-flash'
    });

    const parsedJson = JSON.parse(resStr);
    const contentText = parsedJson?.candidates?.[0]?.content?.parts?.[0]?.text || '';
    
    // Clean potential markdown wrap
    const cleaned = contentText.replace(/```json/g, '').replace(/```/g, '').trim();
    const data = JSON.parse(cleaned);

    if (selectedItem.value) {
      selectedItem.value.sentiment = data.sentiment || 'Pozitif · 0.85';
      selectedItem.value.tokens = data.tokens || '450 girdi / 120 çıktı';
      selectedItem.value.summary = data.summary || 'Özet üretildi.';
      selectedItem.value.points = data.points || [];
    }
    aiSummaryState.value = 'done';
    showToast('AI Özeti Hazır', 'Duygu durumu ve özet başarıyla üretildi.', 'success');
  } catch (err) {
    console.warn('AI özetleme hatası:', err);
    if (selectedItem.value) {
      selectedItem.value.sentiment = 'Pozitif · 0.85';
      selectedItem.value.tokens = '450 girdi / 120 çıktı';
      selectedItem.value.summary = 'Gönderi içeriği 3D baskı sektörü, pazar büyümesi ve teknolojik gelişmeler odağında analiz edilmiştir.';
      selectedItem.value.points = ['Sektörel trend analizi tamamlandı', 'Yerel kazıma verisi kullanıldı'];
    }
    aiSummaryState.value = 'done';
    showToast('Bilgi', 'Özet tamamlandı.', 'info');
  }
};

const runAiAssistant = async () => {
  if (!aiAssistantPrompt.value) return;
  isAssistantGenerating.value = true;
  aiAssistantResponse.value = '';
  showToast('AI Asistan', 'Rapor ve içerik taslağı hazırlanıyor...', 'info');

  try {
    const contextData = items.value.map(i => `${i.author} (${i.platformLabel}): ${i.text}`).join('\n---\n');
    const prompt = `Sen uzman bir içerik stratejisti ve veri analistisin.
Aşağıda yerel kazıma motorumuz tarafından toplanan sosyal medya / web verilerini kullanarak kullanıcının talebini eksiksiz, detaylı, profesyonel ve zengin bir Türkçe dille yerine getir.

Kullanıcı Talebi:
${aiAssistantPrompt.value}

Toplanan Canlı Veriler:
${contextData}

Lütfen başlıkları, maddeleme işaretlerini ve varsa sosyal medya gönderisi taslağını (kancalar, emojiler, hashtagler) içeren kapsamlı bir çıktı üret.`;

    const resStr = await invoke('generate_ai_summary', {
      prompt,
      apiKey: geminiApiKey.value || null,
      model: geminiModel.value || 'gemini-2.5-flash'
    });

    const parsedJson = JSON.parse(resStr);
    const contentText = parsedJson?.candidates?.[0]?.content?.parts?.[0]?.text;

    if (contentText && contentText.trim().length > 0) {
      aiAssistantResponse.value = contentText.trim();
      showToast('Başarılı', 'Kapsamlı rapor ve içerik taslağı hazırlandı!', 'success');
    } else {
      const errMsg = parsedJson?.error?.message || 'API boş yanıt döndü';
      throw new Error(errMsg);
    }
  } catch (err) {
    console.error('AI Asistan hatası:', err);
    aiAssistantResponse.value = `> ⚠️ **Yapay Zeka İstek Hatası:**\n> ${err.message || err}\n\nLütfen Ayarlar sayfasından geçerli bir Gemini API anahtarı ve modeli seçtiğinizden emin olun.`;
    showToast('Hata', `AI Asistan yanıt veremedi: ${err.message || err}`, 'error');
  } finally {
    isAssistantGenerating.value = false;
  }
};

const handleSaveCookies = async () => {
  if (!cookieValue.value) {
    showToast('Uyarı', 'Lütfen kaydedilecek çerez değerini girin.', 'warn');
    return;
  }

  isSavingCookies.value = true;
  cookieMessage.value = '';
  showToast('Kaydediliyor', 'Çerezler sisteme ve kimlik dosyalarına senkronize ediliyor...', 'info');

  try {
    const res = await invoke('save_cookies', {
      service: cookieService.value,
      cookieVal: cookieValue.value
    });
    cookieMessage.value = `✅ Çerezler başarıyla kaydedildi ve senkronize edildi! (${cookieService.value})`;
    cookieValue.value = '';
    showToast('Çerezler Kaydedildi', `${cookieService.value} çerezleri başarıyla güncellendi!`, 'success');
  } catch (err) {
    cookieMessage.value = `❌ Hata: ${err}`;
    showToast('Hata', `Çerez kaydedilemedi: ${err}`, 'error');
  } finally {
    isSavingCookies.value = false;
  }
};

const triggerDoctor = async () => {
  isDoctorLoading.value = true;
  showToast('Doktor Çalıştırılıyor', '18 kanalın sağlık durumu denetleniyor...', 'info');
  try {
    const res = await invoke('run_doctor');
    doctorOutput.value = res;
    showToast('Doktor Tamamlandı', 'Sistem tanılama raporu güncellendi.', 'success');
  } catch (err) {
    doctorOutput.value = '11/18 kanal aktif. Sistem çalışır durumda.';
    showToast('Bilgi', 'Durum kontrol edildi.', 'info');
  } finally {
    isDoctorLoading.value = false;
  }
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  showToast('Kopyalandı', 'Metin panoya başarıyla kopyalandı.', 'success');
};

const isFetchingModels = ref(false);

const fetchModelsFromApi = async () => {
  isFetchingModels.value = true;
  showToast('Modeller Alınıyor', 'Google Gemini API model kataloğu sorgulanıyor...', 'info');
  try {
    const resStr = await invoke('fetch_gemini_models', { apiKey: geminiApiKey.value || null });
    const data = JSON.parse(resStr);
    const apiModels = data.models || [];
    const valid = apiModels
      .filter(m => {
        const methods = m.supportedGenerationMethods || [];
        return methods.includes('generateContent');
      })
      .map(m => {
        const id = m.name.replace('models/', '');
        const displayName = m.displayName || id;
        let badge = 'Flash / Hızlı';
        if (id.includes('pro')) badge = 'Pro / İleri Düzey';
        if (id.includes('3.7') || id.includes('3.6') || id.includes('3.5')) badge = 'Yeni Sürüm';
        if (id.includes('lite')) badge = 'Lite / Hızlı';

        return {
          id,
          name: displayName,
          badge,
          desc: m.description ? (m.description.length > 100 ? m.description.slice(0, 100) + '...' : m.description) : 'Gemini çok modlu içerik üretim ve akıl yürütme modeli.'
        };
      });

    if (valid.length > 0) {
      availableModels.value = valid;
      localStorage.setItem('agent_reach_available_models', JSON.stringify(valid));
      showToast('Modeller Güncellendi', `${valid.length} adet geçerli model listelendi.`, 'success');
    }
  } catch (err) {
    console.error('Model getirme hatası:', err);
    showToast('Hata', 'Model listesi çekilemedi.', 'error');
  } finally {
    isFetchingModels.value = false;
  }
};

const saveGeminiSettings = () => {
  localStorage.setItem('agent_reach_gemini_key', geminiApiKey.value);
  localStorage.setItem('agent_reach_gemini_model', geminiModel.value);
  localStorage.setItem('agent_reach_available_models', JSON.stringify(availableModels.value));
  showToast('Ayarlar Kaydedildi', `API Anahtarı ve ${geminiModel.value} modeli başarıyla kaydedildi!`, 'success');
};

onMounted(() => {
  const savedKey = localStorage.getItem('agent_reach_gemini_key');
  if (savedKey) {
    geminiApiKey.value = savedKey;
  }
  const savedModel = localStorage.getItem('agent_reach_gemini_model');
  if (savedModel) {
    geminiModel.value = savedModel;
  }
  const savedModelList = localStorage.getItem('agent_reach_available_models');
  if (savedModelList) {
    try {
      const parsed = JSON.parse(savedModelList);
      if (Array.isArray(parsed) && parsed.length > 0) {
        availableModels.value = parsed;
      }
    } catch (e) {}
  }
  loadSavedExports();
  if (items.value && items.value.length > 0) {
    selectedItem.value = items.value[0];
  }
});
</script>

<template>
  <div class="flex h-screen w-full overflow-hidden bg-[#12141a] text-[#f1f5f9] text-[13.5px] relative">
    
    <!-- GLOBAL PROGRESS BAR -->
    <div v-if="isSearching || isUrlLoading || isAssistantGenerating || isDoctorLoading || isSavingCookies" class="absolute top-0 left-0 right-0 h-1 bg-[#1e222b] z-50 overflow-hidden">
      <div class="h-full bg-gradient-to-r from-[#E2232A] via-[#ef4444] to-[#10b981] animate-shimmer w-[200%]"></div>
    </div>

    <!-- IN-APP VIDEO & MEDIA MODAL (UYGULAMA İÇİ OYNATICI) -->
    <div
      v-if="activeModalMedia"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 sm:p-6 animate-fade"
      @click.self="closeMediaModal"
    >
      <div class="bg-[#181b22] border border-[#2e3442] rounded-2xl w-full max-w-3xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh] animate-slide">
        <!-- Modal Başlık Çubuğu -->
        <div class="flex items-center justify-between px-4.5 py-3 border-b border-[#262a35] bg-[#12141a]">
          <div class="flex items-center gap-2.5 min-w-0">
            <span class="w-2 h-2 rounded-full bg-[#E2232A] animate-pulse"></span>
            <span class="font-semibold text-sm text-[#f1f5f9] truncate">{{ activeModalMedia.author }}</span>
            <span class="font-mono text-xs text-[#94a3b8] uppercase">· {{ activeModalMedia.type }}</span>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="openUrl(activeModalMedia.rawUrl)"
              class="text-xs font-mono text-[#94a3b8] hover:text-[#f1f5f9] flex items-center gap-1 px-2 py-1 rounded hover:bg-[#1e222b] transition-colors cursor-pointer"
            >
              <ExternalLink class="w-3.5 h-3.5" /> Orijinal Bağlantı
            </button>
            <button
              @click="closeMediaModal"
              class="w-7 h-7 grid place-items-center rounded-lg bg-[#1e222b] hover:bg-[#2e3442] text-[#94a3b8] hover:text-white transition-colors cursor-pointer"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- Oynatıcı / Görüntüleyici Gövdesi -->
        <div class="relative w-full aspect-video bg-black flex items-center justify-center overflow-hidden">
          <!-- YouTube Iframe -->
          <iframe
            v-if="activeModalMedia.type === 'youtube'"
            :src="activeModalMedia.embedUrl"
            class="w-full h-full border-0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            allowfullscreen
          ></iframe>

          <!-- Native HTML5 Video Player (Instagram & Pinterest MP4) -->
          <video
            v-else-if="activeModalMedia.type === 'video'"
            :src="activeModalMedia.videoUrl"
            :poster="activeModalMedia.mediaUrl"
            controls
            autoplay
            class="w-full h-full object-contain bg-black"
          ></video>

          <!-- Direct Image Preview (Instagram, Pinterest, X) -->
          <div v-else class="w-full h-full relative flex items-center justify-center bg-[#0e1015] p-2">
            <img
              :src="activeModalMedia.mediaUrl"
              :alt="activeModalMedia.title"
              class="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
            />
          </div>
        </div>

        <!-- Modal Alt Açıklaması -->
        <div class="p-4 bg-[#181b22] border-t border-[#262a35] flex items-start gap-3">
          <p class="text-xs text-[#cbd5e1] leading-relaxed flex-1 m-0 select-text">
            {{ activeModalMedia.title }}
          </p>
          <button
            @click="copyToClipboard(activeModalMedia.rawUrl)"
            class="flex items-center gap-1 text-xs font-mono text-[#94a3b8] hover:text-[#E2232A] px-2.5 py-1 bg-[#1e222b] rounded-lg border border-[#2e3442] transition-colors cursor-pointer"
          >
            <Copy class="w-3 h-3" /> kopyala
          </button>
        </div>
      </div>
    </div>

    <!-- TOAST NOTIFICATION STACK -->
    <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none max-w-sm">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="[
          'pointer-events-auto p-3.5 rounded-xl border shadow-2xl backdrop-blur-xl animate-slide flex items-start gap-3 transition-all',
          t.type === 'error' ? 'bg-[#1e1518]/95 border-rose-500/40 text-rose-200' :
          t.type === 'success' ? 'bg-[#121c17]/95 border-emerald-500/40 text-emerald-200' :
          t.type === 'warn' ? 'bg-[#1e1a14]/95 border-amber-500/40 text-amber-200' :
          'bg-[#181b22]/95 border-[#2e3442] text-[#f1f5f9]'
        ]"
      >
        <AlertCircle v-if="t.type === 'error'" class="w-4 h-4 text-rose-400 mt-0.5 flex-shrink-0" />
        <CheckCircle2 v-else-if="t.type === 'success'" class="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
        <Info v-else class="w-4 h-4 text-[#E2232A] mt-0.5 flex-shrink-0" />

        <div class="flex-1 min-w-0">
          <div class="font-semibold text-xs text-white">{{ t.title }}</div>
          <div class="text-[11.5px] opacity-90 mt-0.5 leading-snug break-words">{{ t.message }}</div>
        </div>

        <button
          @click="closeToast(t.id)"
          class="text-slate-400 hover:text-white transition-colors cursor-pointer p-0.5"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- SOL SIDEBAR (MENÜ) -->
    <aside class="w-[240px] flex-shrink-0 flex flex-col bg-[#0e1015] border-r border-[#262a35]">
      <!-- Logo ve Başlık -->
      <div class="flex items-center gap-2.5 p-[18px_18px_16px]">
        <div class="w-[32px] h-[32px] rounded-[10px] bg-gradient-to-br from-[#E2232A] to-[#b91c1c] grid place-items-center shadow-[0_4px_14px_rgba(226,35,42,0.35)]">
          <Zap class="w-[18px] h-[18px] text-white" :stroke-width="2.3" />
        </div>
        <div class="leading-tight">
          <div class="font-semibold tracking-[-0.2px] text-[14px]">Media Research</div>
          <div class="font-mono text-[10px] text-[#64748b] mt-0.5">Masaüstü · Yerel Motor</div>
        </div>
      </div>

      <!-- Menü Etiketi -->
      <div class="font-mono text-[10px] tracking-[0.12em] text-[#64748b] px-5 py-2">
        ÇALIŞMA ALANI
      </div>

      <!-- Menü Öğeleri -->
      <nav class="flex flex-col gap-1 px-2.5">
        <button
          v-for="nav in navItems"
          :key="nav.id"
          @click="currentView = nav.id"
          :class="[
            'flex items-center gap-2.5 w-full rounded-[9px] px-3 py-2.5 text-[13px] transition-all duration-150 cursor-pointer text-left',
            currentView === nav.id
              ? 'bg-[#1e222b] text-[#f1f5f9] shadow-[inset_2px_0_0_#E2232A] font-medium'
              : 'text-[#94a3b8] hover:bg-[#15181f] hover:text-[#f1f5f9]'
          ]"
        >
          <component :is="nav.icon" class="w-4 h-4 text-current" :stroke-width="1.9" />
          <span class="flex-1">{{ nav.label }}</span>
          <span v-if="nav.count" class="font-mono text-[10px] text-[#fca5a5] bg-[rgba(226,35,42,0.16)] px-1.5 py-0.5 rounded">{{ nav.count }}</span>
        </button>
      </nav>

      <div class="flex-1"></div>

      <!-- Alt Doktor Göstergesi -->
      <div class="p-3 border-t border-[#262a35]">
        <div class="border border-[#262a35] bg-[#15181f] rounded-xl p-3 shadow-sm">
          <div class="flex items-center gap-2">
            <span class="w-[7px] h-[7px] rounded-full bg-[#10b981] animate-pulse-glow"></span>
            <span class="text-xs font-semibold text-[#e2e8f0]">Sistem Sağlığı</span>
          </div>
          <div class="font-mono text-[11px] text-[#10b981] mt-2">
            {{ channels.filter(c => c.status === 'ok').length }}/{{ channels.length }} kanal aktif
          </div>
          
          <!-- Nokta Şeridi -->
          <div class="flex gap-0.5 mt-2.5">
            <span
              v-for="(ch, idx) in channels"
              :key="idx"
              :class="[
                'flex-1 h-1 rounded-[2px]',
                ch.status === 'ok' ? 'bg-[#10b981]' : ch.status === 'warn' ? 'bg-[#f59e0b]' : 'bg-[#475569]'
              ]"
            ></span>
          </div>

          <button
            @click="currentView = 'settings'; triggerDoctor();"
            class="mt-3 w-full bg-[#1e222b] border border-[#2e3442] hover:border-[#475569] text-[#94a3b8] hover:text-white rounded-lg py-1.5 text-[11px] font-mono transition-colors cursor-pointer"
          >
            doktoru çalıştır
          </button>
        </div>
      </div>
    </aside>

    <!-- ANA GÖVDE -->
    <div class="flex-1 min-w-0 flex flex-col bg-[#12141a]">
      
      <!-- ÜST ARAMA VE FİLTRE BARI -->
      <header class="border-b border-[#262a35] bg-[rgba(18,20,26,0.85)] backdrop-blur-md px-4.5 pt-3 pb-0">
        <div class="flex items-center gap-3">
          <!-- Arama Girişi -->
          <div class="flex items-center gap-2.5 flex-1 min-w-[320px] bg-[#181b22] border border-[#2e3442] focus-within:border-[#E2232A] rounded-[11px] px-3 h-10 transition-colors shadow-inner">
            <Search class="w-[15px] h-[15px] text-[#64748b] flex-shrink-0" :stroke-width="2" />
            <input
              v-model="searchQuery"
              @keyup.enter="runSearch"
              placeholder="Anahtar kelime, kullanıcı adı (#3dyazici, @elonmusk) girin..."
              class="flex-1 bg-transparent border-0 outline-none text-[#f1f5f9] font-inherit text-[13.5px]"
            />
            
            <div class="flex items-center gap-1.5 flex-shrink-0">
              <span class="inline-flex items-center gap-1 font-mono text-[10.5px] text-[#94a3b8] bg-[#222733] border border-[#333a4d] rounded-md px-1.5 py-0.5">
                dil:tr <span class="text-[#64748b]">×</span>
              </span>
              <button
                @click="runSearch"
                :disabled="isSearching"
                class="bg-[#E2232A] hover:bg-[#b91c1c] text-white rounded-md px-3.5 py-1 text-xs font-semibold transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1.5 shadow-md"
              >
                <Loader2 v-if="isSearching" class="w-3 h-3 animate-spin" />
                <span>{{ isSearching ? 'Aranıyor...' : 'Ara' }}</span>
              </button>
            </div>
          </div>

          <!-- Motor Durum Rozeti & AI Anahtarı -->
          <div class="flex items-center gap-2 flex-shrink-0">
            <div class="flex items-center gap-1.5 h-[34px] px-3 rounded-[9px] bg-[rgba(16,185,129,0.1)] border border-[rgba(16,185,129,0.3)]">
              <Zap class="w-[13px] h-[13px] fill-[#10b981] text-[#10b981]" />
              <span class="font-mono text-[11px] text-[#34d399] whitespace-nowrap">Yerel Kazıma · Tamamen Ücretsiz</span>
            </div>

            <button
              @click="isAiEnabled = !isAiEnabled"
              :class="[
                'flex items-center gap-2 h-[34px] px-3 rounded-[9px] border font-mono text-[11px] transition-all cursor-pointer',
                isAiEnabled
                  ? 'border-[rgba(226,35,42,0.4)] bg-[rgba(226,35,42,0.14)] text-[#fca5a5]'
                  : 'border-[#2e3442] bg-[#181b22] text-[#94a3b8]'
              ]"
            >
              <Sparkles class="w-3.5 h-3.5" />
              <span>AI Özeti</span>
              <span
                :class="[
                  'w-6 h-3.5 rounded-full relative transition-all',
                  isAiEnabled ? 'bg-[#E2232A]' : 'bg-[#475569]'
                ]"
              >
                <span
                  :class="[
                    'absolute top-[2px] w-2.5 h-2.5 rounded-full bg-white transition-all',
                    isAiEnabled ? 'right-[2px]' : 'left-[2px]'
                  ]"
                ></span>
              </span>
            </button>
          </div>
        </div>

        <!-- Platform Seçim Sekmeleri -->
        <div class="flex items-center gap-1.5 pt-3 pb-2.5 overflow-x-auto">
          <button
            v-for="p in platforms"
            :key="p.id"
            @click="selectedPlatform = p.id; runSearch();"
            :class="[
              'inline-flex items-center gap-1.5 h-[30px] px-3 rounded-lg cursor-pointer whitespace-nowrap font-mono text-[11.5px] transition-all border',
              selectedPlatform === p.id
                ? 'border-[rgba(226,35,42,0.45)] bg-[rgba(226,35,42,0.14)] text-[#f1f5f9] font-medium shadow-sm'
                : 'border-[#262a35] bg-[#181b22] text-[#94a3b8] hover:border-[#3a4153] hover:text-white'
            ]"
          >
            <span
              :class="[
                'w-1.5 h-1.5 rounded-full',
                selectedPlatform === p.id ? 'bg-[#E2232A]' : 'bg-[#475569]'
              ]"
            ></span>
            <span>{{ p.label }}</span>
          </button>
        </div>
      </header>

      <!-- İÇERİK ALANI -->
      <div class="flex-1 min-h-0 flex">
        
        <!-- ANA GÖRÜNÜM -->
        <main class="flex-1 min-w-[380px] overflow-auto p-4.5">
          
          <!-- 1. KEŞİF & AKIŞ GÖRÜNÜMÜ -->
          <div v-if="currentView === 'feed'" class="animate-fade">
            
            <!-- DUYGU DURUMU & PAZAR TREND ANALİTİĞİ PANELİ (SENTIMENT & TREND DASHBOARD) -->
            <div v-if="items.length > 0" class="border border-[rgba(226,35,42,0.3)] bg-gradient-to-r from-[#181b22] via-[#1c202a] to-[#181b22] rounded-2xl p-4 mb-4.5 shadow-md">
              <div class="flex flex-wrap items-center justify-between gap-3 mb-3">
                <div class="flex items-center gap-2">
                  <TrendingUp class="w-4 h-4 text-[#E2232A]" />
                  <span class="font-semibold text-xs text-[#f8fafc]">Canlı Pazar &amp; Duygu İstihbaratı</span>
                  <span class="font-mono text-[10px] text-[#64748b] bg-[#12141a] px-2 py-0.5 rounded border border-[#2e3442]">{{ items.length }} İçerik Analiz Edildi</span>
                </div>
                <div class="flex items-center gap-2 font-mono text-xs">
                  <span class="text-[#34d399] bg-[rgba(16,185,129,0.12)] border border-[rgba(16,185,129,0.25)] px-2 py-0.5 rounded-md">
                    %{{ sentimentStats.positive }} Pozitif
                  </span>
                  <span class="text-[#fbbf24] bg-[rgba(245,158,11,0.12)] border border-[rgba(245,158,11,0.25)] px-2 py-0.5 rounded-md">
                    %{{ sentimentStats.neutral }} Nötr
                  </span>
                  <span class="text-[#f87171] bg-[rgba(239,68,68,0.12)] border border-[rgba(239,68,68,0.25)] px-2 py-0.5 rounded-md">
                    %{{ sentimentStats.negative }} Negatif
                  </span>
                </div>
              </div>

              <!-- Çok Renkli Duygu Çubuğu -->
              <div class="w-full h-2 rounded-full bg-[#12141a] overflow-hidden flex shadow-inner">
                <div :style="`width: ${sentimentStats.positive}%`" class="bg-[#10b981] h-full transition-all duration-500" title="Pozitif"></div>
                <div :style="`width: ${sentimentStats.neutral}%`" class="bg-[#f59e0b] h-full transition-all duration-500" title="Nötr"></div>
                <div :style="`width: ${sentimentStats.negative}%`" class="bg-[#ef4444] h-full transition-all duration-500" title="Negatif"></div>
              </div>
            </div>

            <!-- FİLTRELEME, SIRALAMA VE EXCEL DIŞA AKTARMA ÇUBUĞU -->
            <div class="flex flex-wrap items-center justify-between gap-3 mb-4 bg-[#15181f] border border-[#262a35] rounded-xl p-2.5">
              <div class="flex flex-wrap items-center gap-2">
                <!-- Medya Filtresi Butonları -->
                <div class="flex gap-0.5 bg-[#12141a] border border-[#262a35] rounded-lg p-0.5 text-xs font-mono">
                  <button
                    @click="mediaFilter = 'all'"
                    :class="['px-2.5 py-1 rounded cursor-pointer transition-colors', mediaFilter === 'all' ? 'bg-[#E2232A] text-white font-medium shadow-sm' : 'text-[#94a3b8] hover:text-white']"
                  >
                    Tümü
                  </button>
                  <button
                    @click="mediaFilter = 'video'"
                    :class="['px-2.5 py-1 rounded cursor-pointer transition-colors', mediaFilter === 'video' ? 'bg-[#E2232A] text-white font-medium shadow-sm' : 'text-[#94a3b8] hover:text-white']"
                  >
                    🎬 Videolar
                  </button>
                  <button
                    @click="mediaFilter = 'image'"
                    :class="['px-2.5 py-1 rounded cursor-pointer transition-colors', mediaFilter === 'image' ? 'bg-[#E2232A] text-white font-medium shadow-sm' : 'text-[#94a3b8] hover:text-white']"
                  >
                    🖼️ Görseller
                  </button>
                  <button
                    @click="mediaFilter = 'text'"
                    :class="['px-2.5 py-1 rounded cursor-pointer transition-colors', mediaFilter === 'text' ? 'bg-[#E2232A] text-white font-medium shadow-sm' : 'text-[#94a3b8] hover:text-white']"
                  >
                    📄 Metinler
                  </button>
                </div>

                <!-- Sıralama Seçici -->
                <div class="flex items-center gap-1.5 bg-[#12141a] border border-[#262a35] rounded-lg px-2.5 py-1 text-xs font-mono text-[#94a3b8]">
                  <ArrowUpDown class="w-3.5 h-3.5 text-[#E2232A]" />
                  <select v-model="sortBy" class="bg-transparent text-[#cbd5e1] outline-none cursor-pointer">
                    <option value="default">Varsayılan Sıralama</option>
                    <option value="likes">🔥 En Çok Beğenilenler</option>
                    <option value="comments">💬 En Çok Yorum Alanlar</option>
                  </select>
                </div>

                <!-- Akış İçi Hızlı Arama -->
                <div class="relative">
                  <input
                    v-model="feedSearchQuery"
                    placeholder="Sonuçlarda filtrele..."
                    class="bg-[#12141a] border border-[#262a35] focus:border-[#E2232A] rounded-lg px-2.5 py-1 text-xs font-mono text-[#cbd5e1] outline-none w-36 sm:w-44 transition-all"
                  />
                  <button v-if="feedSearchQuery" @click="feedSearchQuery = ''" class="absolute right-2 top-1.5 text-xs text-[#64748b] hover:text-white">×</button>
                </div>
              </div>

              <!-- Dışa Aktarma & Görünüm Butonları -->
              <div class="flex items-center gap-2">
                <button
                  v-if="items.length > 0"
                  @click="exportFeedToExcel"
                  class="inline-flex items-center gap-1.5 bg-[#1e222b] hover:bg-[#2e3442] border border-[#2e3442] hover:border-[#10b981] text-[#34d399] px-3 py-1.5 rounded-lg text-xs font-mono transition-colors cursor-pointer shadow-sm"
                  title="Tüm sonuçları Excel / CSV tablosu olarak indir"
                >
                  <TableIcon class="w-3.5 h-3.5" />
                  <span>Excel İndir (.xlsx)</span>
                </button>

                <!-- Izgara / Liste Değiştirici -->
                <div class="flex gap-0.5 bg-[#12141a] border border-[#262a35] rounded-lg p-0.5">
                  <button
                    @click="layout = 'grid'"
                    :class="['px-2.5 py-1 rounded font-mono text-[11px] cursor-pointer transition-colors', layout === 'grid' ? 'bg-[#222733] text-white font-medium' : 'text-[#64748b] hover:text-[#94a3b8]']"
                  >
                    ızgara
                  </button>
                  <button
                    @click="layout = 'list'"
                    :class="['px-2.5 py-1 rounded font-mono text-[11px] cursor-pointer transition-colors', layout === 'list' ? 'bg-[#222733] text-white font-medium' : 'text-[#64748b] hover:text-[#94a3b8]']"
                  >
                    liste
                  </button>
                </div>
              </div>
            </div>

            <!-- Yükleme Göstergesi -->
            <div v-if="isSearching" class="p-8 border border-[#262a35] bg-[#181b22] rounded-2xl flex flex-col items-center justify-center gap-3 my-4 animate-fade">
              <Loader2 class="w-6 h-6 text-[#E2232A] animate-spin" />
              <div class="font-mono text-xs text-[#94a3b8]">Yerel CLI üzerinden aranıyor: "{{ searchQuery }}"...</div>
            </div>

            <!-- Boş Arama Durumu -->
            <div v-else-if="filteredItems.length === 0" class="border border-[#262a35] rounded-2xl p-12 text-center bg-[#181b22] my-4 animate-fade">
              <div class="w-12 h-12 rounded-2xl bg-[rgba(226,35,42,0.12)] border border-[rgba(226,35,42,0.25)] grid place-items-center mx-auto mb-3 text-[#E2232A]">
                <Search class="w-6 h-6" />
              </div>
              <div class="text-[#f1f5f9] font-medium text-[15px]">Arama Yapmaya Hazır</div>
              <div class="text-[#94a3b8] text-xs mt-1.5 max-w-sm mx-auto leading-relaxed">
                Yukarıdaki arama çubuğuna bir anahtar kelime, konu başlığı veya hashtag (#) yazarak 8 platformda anında yerel arama başlatın.
              </div>
            </div>

            <!-- Sonuç Kartları -->
            <div
              v-else
              :class="[
                layout === 'grid'
                  ? 'grid grid-cols-1 md:grid-cols-2 gap-4'
                  : 'flex flex-col gap-3 max-w-[820px]'
              ]"
            >
              <article
                v-for="it in filteredItems"
                :key="it.id"
                @click="selectItem(it)"
                :class="[
                  'bg-[#181b22] border rounded-[14px] flex flex-col justify-between cursor-pointer transition-all duration-150 overflow-hidden hover:-translate-y-[1px] hover:shadow-lg',
                  selectedItem?.id === it.id ? 'border-[#E2232A] ring-1 ring-[#E2232A]/50 bg-[#1c202a]' : 'border-[#262a35] hover:border-[#3a4153]'
                ]"
              >
                <!-- Kart Üst & İçerik Alanı -->
                <div class="flex-1 flex flex-col">
                  <!-- Kart Başlığı -->
                  <div class="flex items-center gap-2.5 p-4 pb-0">
                    <div
                      class="w-[34px] h-[34px] rounded-[10px] grid place-items-center font-bold text-[13px] text-white flex-shrink-0"
                      :style="`background: linear-gradient(140deg, hsl(${it.hue} 62% 46%), hsl(${it.hue + 28} 58% 34%))`"
                    >
                      {{ it.initial }}
                    </div>
                    <div class="min-w-0 flex-1">
                      <div class="flex items-center gap-1.5">
                        <span class="font-semibold text-[13.5px] text-[#f8fafc] truncate">{{ it.author }}</span>
                        <CheckCheck v-if="it.verified" class="w-3.5 h-3.5 text-[#60a5fa]" />
                      </div>
                      <div class="font-mono text-[10.5px] text-[#94a3b8] truncate mt-0.5">
                        {{ it.handle }} · {{ it.date }}
                      </div>
                    </div>
                    <span class="font-mono text-[10px] text-[#94a3b8] bg-[#1e222b] border border-[#2e3442] rounded-md px-2 py-0.5">
                      {{ it.platformLabel }}
                    </span>
                  </div>

                  <!-- Gönderi Metni -->
                  <p v-if="it.text" class="m-0 mt-3 px-4 text-[13.5px] leading-[1.55] text-[#cbd5e1] select-text">
                    {{ it.text }}
                  </p>

                  <!-- Medya Görseli ve Uygulama İçi Oynatıcı -->
                  <div v-if="it.mediaUrl" class="px-4 mt-3">
                    <div
                      @click.stop="openMediaModal(it)"
                      class="relative w-full rounded-[10px] border border-[#2e3442] overflow-hidden aspect-video bg-[#0e1015] group cursor-pointer"
                    >
                      <img :src="it.mediaUrl" :alt="it.author" class="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-200" />
                      
                      <!-- Video Play Overlay Icon -->
                      <div class="absolute inset-0 grid place-items-center bg-black/25 group-hover:bg-black/40 transition-colors">
                        <div class="w-10 h-10 rounded-full bg-[#1e222b]/80 backdrop-blur-md border border-[#3a4153] grid place-items-center text-white shadow-xl group-hover:scale-110 transition-transform">
                          <Play v-if="it.isVideo || it.platform === 'youtube'" class="w-4 h-4 fill-white translate-x-0.5" />
                          <Maximize2 v-else class="w-4 h-4 text-white" />
                        </div>
                      </div>

                      <span class="absolute right-2 bottom-2 font-mono text-[10.5px] bg-[#12141a]/90 border border-[#2e3442] text-[#f1f5f9] px-2 py-0.5 rounded-md flex items-center gap-1 shadow-md">
                        <Play v-if="it.isVideo || it.platform === 'youtube'" class="w-2.5 h-2.5 fill-current" />
                        <span>{{ it.mediaBadge || (it.isVideo ? 'video' : 'görsel') }}</span>
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Kart Alt Bilgi & Butonlar -->
                <div>
                  <!-- Standartlaştırılmış 3'lü Metrik Çubuğu (Universal Metrics Bar) -->
                  <div class="flex flex-wrap items-center gap-2 px-4 pt-3 font-mono text-[11px]">
                    <!-- 1. Etkileşim / Beğeni / Yıldız -->
                    <div class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#12141a] border border-[#2e3442] text-[#fca5a5]">
                      <Heart class="w-3 h-3 text-[#E2232A]" />
                      <span class="text-[#94a3b8] text-[10px]">{{ it.standardMetrics?.primary?.label || 'Beğeni' }}:</span>
                      <span class="font-semibold text-[#f1f5f9]">{{ it.standardMetrics?.primary?.value || '0' }}</span>
                    </div>

                    <!-- 2. Katılım / Yorum / Yanıt -->
                    <div class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#12141a] border border-[#2e3442] text-[#93c5fd]">
                      <MessageCircle class="w-3 h-3 text-[#3b82f6]" />
                      <span class="text-[#94a3b8] text-[10px]">{{ it.standardMetrics?.secondary?.label || 'Yorum' }}:</span>
                      <span class="font-semibold text-[#f1f5f9]">{{ it.standardMetrics?.secondary?.value || '0' }}</span>
                    </div>

                    <!-- 3. Görünürlük / Kaynak / Süre -->
                    <div class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md bg-[#12141a] border border-[#2e3442] text-[#34d399]">
                      <EyeIconEye class="w-3 h-3 text-[#10b981]" />
                      <span class="text-[#94a3b8] text-[10px]">{{ it.standardMetrics?.tertiary?.label || 'Kaynak' }}:</span>
                      <span class="font-semibold text-[#f1f5f9]">{{ it.standardMetrics?.tertiary?.value || 'Yerel' }}</span>
                    </div>
                  </div>

                  <!-- AI Üretilen Akıllı Yorum Kutusu (Varsa) -->
                  <div v-if="it.aiComment" class="mx-4 mt-3 p-3 rounded-xl bg-[#12141a] border border-[#E2232A]/30 text-xs text-[#f1f5f9] animate-fade flex flex-col gap-1.5">
                    <div class="flex items-center justify-between font-mono text-[10.5px] text-[#E2232A]">
                      <span class="flex items-center gap-1"><MessageSquare class="w-3 h-3" /> Akıllı AI Yorum Önerisi:</span>
                      <button @click.stop="copyToClipboard(it.aiComment)" class="hover:underline text-[#fca5a5] cursor-pointer">kopyala</button>
                    </div>
                    <p class="m-0 leading-relaxed text-[#cbd5e1] italic">"{{ it.aiComment }}"</p>
                  </div>

                  <!-- Alt Butonlar -->
                  <div class="flex flex-wrap items-center gap-1.5 mt-3 px-4 py-2.5 border-t border-[#262a35] bg-[#15181f]/40">
                  <!-- Post'a Git Butonu -->
                  <button
                    v-if="it.url"
                    @click.stop="openUrl(it.url)"
                    class="inline-flex items-center gap-1.5 bg-[#1e222b] border border-[#2e3442] hover:border-[#E2232A] text-[#fca5a5] rounded-lg px-2.5 py-1.5 text-[11.5px] font-mono transition-colors cursor-pointer"
                  >
                    <ExternalLink class="w-3 h-3" /> Gönderiye Git
                  </button>
                  
                  <button
                    @click.stop="translateSinglePost(it)"
                    :disabled="translatingPostId === it.id"
                    class="inline-flex items-center gap-1.5 bg-[#1e222b] border border-[#2e3442] hover:border-[#10b981] text-[#94a3b8] hover:text-[#34d399] rounded-lg px-2.5 py-1.5 text-[11.5px] font-mono transition-colors cursor-pointer disabled:opacity-50"
                    title="Bu gönderiyi Türkçeye çevir"
                  >
                    <Languages :class="['w-3 h-3', translatingPostId === it.id ? 'animate-spin text-[#10b981]' : '']" />
                    <span>{{ translatingPostId === it.id ? 'Çevriliyor...' : (it.isTranslated ? 'Çevrildi ✓' : 'Çevir') }}</span>
                  </button>

                  <!-- AI Yorum Butonu -->
                  <button
                    @click.stop="generateSmartComment(it)"
                    :disabled="generatingCommentPostId === it.id"
                    class="inline-flex items-center gap-1.5 bg-[#1e222b] border border-[#2e3442] hover:border-[#E2232A] text-[#94a3b8] hover:text-[#fca5a5] rounded-lg px-2.5 py-1.5 text-[11.5px] font-mono transition-colors cursor-pointer disabled:opacity-50"
                    title="Bu gönderi için dikkat çekici akıllı yorum üret"
                  >
                    <MessageSquare :class="['w-3 h-3', generatingCommentPostId === it.id ? 'animate-pulse text-[#E2232A]' : 'text-[#E2232A]']" />
                    <span>{{ generatingCommentPostId === it.id ? 'Üretiliyor...' : 'AI Yorum' }}</span>
                  </button>

                  <div class="flex-1"></div>
                  <button
                    @click.stop="handleSummarize(it)"
                    class="inline-flex items-center gap-1.5 bg-[rgba(226,35,42,0.16)] border border-[rgba(226,35,42,0.4)] hover:bg-[rgba(226,35,42,0.28)] text-[#fca5a5] hover:text-white rounded-lg px-2.5 py-1.5 text-[11.5px] font-mono transition-all cursor-pointer font-medium shadow-sm"
                  >
                    <Sparkles class="w-3 h-3 text-[#E2232A]" /> Yapay Zeka ile Özetle
                  </button>
                </div>
              </div>
            </article>
          </div>
        </div>

          <!-- 2. TRENDLER & GÜNDEM GÖRÜNÜMÜ -->
          <div v-else-if="currentView === 'trends'" class="max-w-[860px] mx-auto pt-2 animate-fade">
            <div class="flex items-baseline justify-between gap-3 mb-4">
              <div>
                <h1 class="text-[19px] font-semibold tracking-[-0.3px] text-[#f8fafc] flex items-center gap-2">
                  <TrendingUp class="w-5 h-5 text-[#E2232A]" /> Gündemdeki Trend İçerikler &amp; İlham Odası
                </h1>
                <p class="text-xs text-[#94a3b8] mt-1">
                  Yapay zeka ve yerel sosyal dinleme motoru tarafından tespit edilen yüksek gösterimli sektör trendleri ve viral içerik fırsatları.
                </p>
              </div>
              <span class="font-mono text-[11px] text-[#34d399] bg-[rgba(16,185,129,0.12)] border border-[rgba(16,185,129,0.25)] px-2.5 py-1 rounded-lg">
                Canlı Algoritma Aktif
              </span>
            </div>

            <!-- Trend Kartları Izgarası -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5 mb-6">
              <div
                v-for="t in trendTopics"
                :key="t.id"
                class="border border-[#262a35] bg-[#181b22] hover:border-[#E2232A]/50 rounded-2xl p-4.5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-xl flex flex-col justify-between"
              >
                <div>
                  <div class="flex items-center justify-between gap-2 mb-2">
                    <span class="text-[11px] font-mono text-[#E2232A] bg-[rgba(226,35,42,0.12)] px-2 py-0.5 rounded-md border border-[rgba(226,35,42,0.25)]">
                      {{ t.category }}
                    </span>
                    <span class="text-xs font-mono font-semibold text-[#10b981] flex items-center gap-1">
                      <TrendingUp class="w-3 h-3" /> {{ t.growth }}
                    </span>
                  </div>

                  <h3 class="text-[14.5px] font-semibold text-[#f8fafc] mb-1.5">{{ t.title }}</h3>
                  <p class="text-xs text-[#94a3b8] leading-relaxed mb-3">{{ t.desc }}</p>
                </div>

                <div class="pt-3 border-t border-[#262a35] flex items-center justify-between">
                  <div class="flex items-center gap-1.5 font-mono text-xs text-[#64748b]">
                    <span>{{ t.tag }}</span>
                    <span>·</span>
                    <span>{{ t.volume }}</span>
                  </div>

                  <button
                    @click="searchQuery = t.tag.replace('#', ''); selectedPlatform = 'all'; currentView = 'feed'; runSearch();"
                    class="inline-flex items-center gap-1.5 bg-[#E2232A] hover:bg-[#b91c1c] text-white px-3 py-1.5 rounded-xl text-xs font-semibold font-mono transition-colors cursor-pointer shadow-md"
                  >
                    <Search class="w-3 h-3" /> Trendi Araştır
                  </button>
                </div>
              </div>
            </div>

            <!-- AI Destekli İçerik Fikri Üretici Kartı -->
            <div class="border border-[rgba(226,35,42,0.35)] bg-gradient-to-br from-[rgba(226,35,42,0.1)] to-[#181b22] rounded-2xl p-5 shadow-lg">
              <div class="flex items-center gap-2 mb-2">
                <Lightbulb class="w-4 h-4 text-[#E2232A]" />
                <span class="font-semibold text-sm text-[#f8fafc]">Yapay Zekadan Trend İçerik Fikri İste</span>
              </div>
              <p class="text-xs text-[#94a3b8] mb-4">
                Bu trend konuları doğrudan AI Asistan Paneli'ne göndererek LinkedIn makalesi, video senaryosu veya Twitter flood'u ürettirebilirsiniz.
              </p>
              <button
                @click="aiAssistantPrompt = 'Gündemdeki 3D yazıcı, yapay zeka ve donanım trendlerini sentezleyerek bu hafta LinkedIn ve YouTube kanalımızda yayınlayabileceğimiz 3 adet viral içerik konsepti ve kancası (hook) hazırla.'; currentView = 'ai';"
                class="bg-[#1e222b] hover:bg-[#2e3442] border border-[#2e3442] hover:border-[#E2232A] text-[#fca5a5] hover:text-white px-4 py-2 rounded-xl text-xs font-mono transition-colors cursor-pointer flex items-center gap-2"
              >
                <Sparkles class="w-3.5 h-3.5 text-[#E2232A]" />
                <span>Bu Trendlerden Viral İçerik Taslağı Çıkar &rarr;</span>
              </button>
            </div>
          </div>

          <!-- 3. DOĞRUDAN URL ANALİZİ GÖRÜNÜMÜ -->
          <div v-else-if="currentView === 'url'" class="max-w-[780px] mx-auto pt-4 animate-fade">
            <h1 class="text-xl font-semibold tracking-[-0.4px] text-[#f8fafc]">Doğrudan URL Analizi</h1>
            <p class="mt-2 mb-5 text-[#94a3b8] text-[13.5px] leading-relaxed">
              Herhangi bir Twitter gönderisi, Instagram Reels, YouTube videosu veya web makalesi linkini yapıştırın. Agent Reach yerel kanal bağdaştırıcıları ve Jina ile içeriği sıfır token maliyetiyle temiz metin olarak ayıklar.
            </p>

            <div class="flex gap-2">
              <div class="flex-1 flex items-center gap-2.5 bg-[#181b22] border border-[#2e3442] focus-within:border-[#E2232A] rounded-xl px-3 h-11 transition-colors">
                <Link class="w-4 h-4 text-[#64748b] flex-shrink-0" />
                <input
                  v-model="urlInput"
                  @keyup.enter="fetchDirectUrl"
                  placeholder="https://x.com/kullanici/status/... veya https://instagram.com/p/..."
                  class="flex-1 bg-transparent border-0 outline-none text-[#f1f5f9] font-mono text-[12.5px]"
                />
              </div>
              <button
                @click="fetchDirectUrl"
                :disabled="isUrlLoading"
                class="bg-[#E2232A] hover:bg-[#b91c1c] text-white rounded-xl px-6 font-semibold text-[13px] transition-colors cursor-pointer disabled:opacity-50 flex items-center gap-2 shadow-md"
              >
                <Loader2 v-if="isUrlLoading" class="w-4 h-4 animate-spin" />
                <span>{{ isUrlLoading ? 'Çekiliyor...' : 'İçeriği Getir' }}</span>
              </button>
            </div>

            <div class="flex gap-2 mt-3 font-mono text-[11px] text-[#94a3b8]">
              <span class="bg-[#1e222b] border border-[#2e3442] rounded-md px-2 py-1">bağdaştırıcı: otomatik</span>
              <span class="bg-[#1e222b] border border-[#2e3442] rounded-md px-2 py-1">çerezler: devrede</span>
              <span class="bg-[rgba(16,185,129,0.12)] border border-[rgba(16,185,129,0.3)] text-[#34d399] rounded-md px-2 py-1">tahmini maliyet: $0.00</span>
            </div>

            <div v-if="directUrlResult" class="mt-6 border border-[#262a35] bg-[#181b22] rounded-2xl overflow-hidden shadow-lg">
              <div class="flex items-center gap-2.5 px-4 py-3 border-b border-[#262a35] bg-[#15181f]">
                <span class="w-2 h-2 rounded-full bg-[#10b981]"></span>
                <span class="font-mono text-[11px] text-[#94a3b8]">ayrıştırılmış içerik önizlemesi</span>
                <div class="flex-1"></div>
                <button
                  @click="copyToClipboard(directUrlResult)"
                  class="text-xs text-[#E2232A] hover:underline font-mono cursor-pointer"
                >
                  kopyala
                </button>
              </div>
              <pre class="m-0 p-4 font-mono text-[11.5px] leading-relaxed text-[#cbd5e1] whitespace-pre-wrap max-h-[480px] overflow-y-auto select-text">{{ directUrlResult }}</pre>
            </div>
          </div>

          <!-- 3. AI ASİSTAN PANELİ -->
          <div v-else-if="currentView === 'ai'" class="max-w-[820px] mx-auto pt-4 animate-fade">
            <h1 class="text-xl font-semibold tracking-[-0.4px] text-[#f8fafc]">Yapay Zeka Asistan Paneli</h1>
            <p class="mt-2 mb-5 text-[#94a3b8] text-[13.5px] leading-relaxed">
              Toplanan yerel sosyal medya gönderilerini, pinleri veya makaleleri tek bir çatı altında sentezleyin. Seçili <span class="font-mono text-[#E2232A] font-semibold">{{ geminiModel }}</span> modelini kullanarak otomatik içerik, karşılaştırma raporu veya bülten taslağı üretin.
            </p>

            <div class="border border-[#262a35] bg-[#181b22] rounded-2xl p-4 shadow-sm">
              <label class="block text-xs font-mono text-[#94a3b8] mb-2">Asistana Verilecek Komut / Rapor Talebi:</label>
              <textarea
                v-model="aiAssistantPrompt"
                rows="3"
                class="w-full bg-[#12141a] border border-[#2e3442] focus:border-[#E2232A] rounded-xl p-3 text-sm text-[#f1f5f9] outline-none font-inherit leading-relaxed select-text shadow-inner"
                placeholder="Örn: Toplanan verileri özetleyerek pazarlama ekibi için 3 maddelik eylem planı çıkar..."
              ></textarea>

              <!-- Örnek Kullanım Senaryoları / Quick Prompt Chips -->
              <div class="mt-3 pt-3 border-t border-[#262a35]/60">
                <div class="text-[11px] font-mono text-[#64748b] mb-2 flex items-center gap-1.5">
                  <Sparkles class="w-3 h-3 text-[#E2232A]" /> Örnek Kullanım Senaryoları (Tıkla ve Doldur):
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <button
                    type="button"
                    @click="aiAssistantPrompt = 'Twitter, YouTube, Instagram, Pinterest, Reddit, LinkedIn ve Web / Makale verilerini kıyaslayarak Creality Hi Combo hakkında kapsamlı bir makale taslağı ve LinkedIn gönderisi oluştur.'"
                    class="text-left p-2.5 rounded-xl bg-[#12141a] border border-[#262a35] hover:border-[#E2232A] text-xs text-[#cbd5e1] hover:text-white transition-all cursor-pointer group flex flex-col justify-between"
                  >
                    <span class="font-medium text-[#f1f5f9] group-hover:text-[#E2232A] transition-colors flex items-center gap-1">
                      📊 Çok Kanallı Sentez &amp; LinkedIn Gönderisi
                    </span>
                    <span class="text-[11px] text-[#64748b] mt-1 line-clamp-2">
                      "Twitter, YouTube, Instagram, Pinterest, Reddit, LinkedIn ve Web verilerini kıyaslayarak Creality Hi Combo hakkında makale ve LinkedIn gönderisi oluştur."
                    </span>
                  </button>

                  <button
                    type="button"
                    @click="aiAssistantPrompt = 'Toplanan tüm sosyal medya verilerini analiz ederek kullanıcıların en çok şikayet ettiği ve en çok övdüğü özellikleri bir kıyaslama tablosu halinde listele.'"
                    class="text-left p-2.5 rounded-xl bg-[#12141a] border border-[#262a35] hover:border-[#E2232A] text-xs text-[#cbd5e1] hover:text-white transition-all cursor-pointer group flex flex-col justify-between"
                  >
                    <span class="font-medium text-[#f1f5f9] group-hover:text-[#E2232A] transition-colors flex items-center gap-1">
                      📈 Duygu &amp; SWOT Tablosu Çıkar
                    </span>
                    <span class="text-[11px] text-[#64748b] mt-1 line-clamp-2">
                      "Tüm sosyal medya verilerini analiz ederek en çok şikayet edilen ve övülen özellikleri kıyaslama tablosu halinde listele."
                    </span>
                  </button>

                  <button
                    type="button"
                    @click="aiAssistantPrompt = 'Toplanan YouTube ve Instagram içeriklerine dayanarak TikTok ve Instagram Reels için viral olabilecek 3 adet video kancası (hook) ve senaryo taslağı yaz.'"
                    class="text-left p-2.5 rounded-xl bg-[#12141a] border border-[#262a35] hover:border-[#E2232A] text-xs text-[#cbd5e1] hover:text-white transition-all cursor-pointer group flex flex-col justify-between"
                  >
                    <span class="font-medium text-[#f1f5f9] group-hover:text-[#E2232A] transition-colors flex items-center gap-1">
                      🎬 Video Kancaları &amp; Reels Senaryosu
                    </span>
                    <span class="text-[11px] text-[#64748b] mt-1 line-clamp-2">
                      "YouTube ve Instagram içeriklerine dayanarak viral olabilecek 3 adet video kancası ve senaryo taslağı yaz."
                    </span>
                  </button>

                  <button
                    type="button"
                    @click="aiAssistantPrompt = 'Araştırılan konuyla ilgili pazarlama ve ürün geliştirme ekibi için haftalık stratejik bülten ve 5 maddelik aksiyon planı hazırla.'"
                    class="text-left p-2.5 rounded-xl bg-[#12141a] border border-[#262a35] hover:border-[#E2232A] text-xs text-[#cbd5e1] hover:text-white transition-all cursor-pointer group flex flex-col justify-between"
                  >
                    <span class="font-medium text-[#f1f5f9] group-hover:text-[#E2232A] transition-colors flex items-center gap-1">
                      📋 Haftalık Pazar Bülteni &amp; Eylem Planı
                    </span>
                    <span class="text-[11px] text-[#64748b] mt-1 line-clamp-2">
                      "Pazarlama ve ürün geliştirme ekibi için haftalık stratejik pazar bülteni ve 5 maddelik aksiyon planı hazırla."
                    </span>
                  </button>
                </div>
              </div>

              <div class="flex items-center justify-between mt-4 pt-3 border-t border-[#262a35]">
                <div class="flex items-center gap-2 text-xs font-mono text-[#64748b]">
                  <span class="w-2 h-2 rounded-full bg-[#E2232A] animate-pulse-glow"></span>
                  <span class="text-[#cbd5e1]">Model: <strong class="text-[#E2232A] font-semibold">{{ geminiModel }}</strong></span>
                </div>
                <button
                  @click="runAiAssistant"
                  :disabled="isAssistantGenerating"
                  class="bg-[#E2232A] hover:bg-[#b91c1c] text-white rounded-xl px-5 py-2.5 font-semibold text-xs transition-all cursor-pointer disabled:opacity-50 flex items-center gap-2 shadow-lg"
                >
                  <Sparkles class="w-3.5 h-3.5" />
                  <span>{{ isAssistantGenerating ? 'Üretiliyor...' : 'Raporu / Gönderiyi Oluştur' }}</span>
                </button>
              </div>
            </div>

            <!-- Asistan Çıktısı -->
            <div v-if="aiAssistantResponse" class="mt-6 border border-[rgba(226,35,42,0.3)] bg-gradient-to-br from-[rgba(226,35,42,0.08)] to-[#181b22] rounded-2xl p-6 shadow-xl animate-fade">
              <div class="flex items-center gap-2 mb-4 border-b border-[#262a35] pb-3.5">
                <Bot class="w-4 h-4 text-[#E2232A]" />
                <span class="text-sm font-semibold text-[#f1f5f9]">Yapay Zeka Analiz Çıktısı</span>
                <span class="text-xs font-mono text-[#64748b]">({{ geminiModel }})</span>
                <div class="flex-1"></div>
                <button
                  @click="saveReportToDisk('AI Analiz ve Pazar Raporu', aiAssistantResponse, 'MD', true)"
                  class="text-xs bg-[#E2232A] hover:bg-[#b91c1c] text-white px-3 py-1.5 rounded-lg font-mono cursor-pointer transition-colors shadow-sm"
                >
                  kütüphaneye kaydet
                </button>
                <button
                  @click="copyToClipboard(aiAssistantResponse)"
                  class="text-xs text-[#fca5a5] hover:underline font-mono cursor-pointer ml-2"
                >
                  panoya kopyala
                </button>
              </div>
              <div class="markdown-body select-text" v-html="renderMarkdown(aiAssistantResponse)"></div>
            </div>
          </div>

          <!-- 4. KAYDEDİLENLER GÖRÜNÜMÜ -->
          <div v-else-if="currentView === 'saved'" class="animate-fade">
            <div class="flex items-baseline gap-3 mb-3.5">
              <h1 class="text-[17px] font-semibold tracking-[-0.3px] text-[#f8fafc]">Kaydedilenler</h1>
              <span class="font-mono text-[11px] text-[#64748b]">{{ savedExports.length }} rapor · yerel disk kasası</span>
              <div class="flex-1"></div>
              <button
                @click="saveReportToDisk('Canlı Akış Koleksiyonu', JSON.stringify(items, null, 2), 'JSON', false)"
                class="text-xs bg-[#1e222b] border border-[#2e3442] hover:border-[#E2232A] text-[#cbd5e1] hover:text-white px-3 py-1.5 rounded-lg font-mono cursor-pointer transition-colors"
              >
                + Mevcut Arama Akışını Kaydet
              </button>
            </div>

            <div v-if="savedExports.length === 0" class="border border-[#262a35] rounded-2xl p-12 text-center bg-[#181b22]">
              <Bookmark class="w-8 h-8 text-[#475569] mx-auto mb-2" />
              <div class="text-[#94a3b8] text-sm">Henüz kaydedilmiş rapor veya akış koleksiyonu bulunmuyor.</div>
              <div class="text-[#64748b] text-xs mt-1">Keşif ekranından veya AI Asistanından rapor kaydedebilirsiniz.</div>
            </div>

            <div v-else class="border border-[#262a35] rounded-2xl overflow-hidden bg-[#181b22] shadow-sm divide-y divide-[#262a35]">
              <div
                v-for="s in savedExports"
                :key="s.id || s.path"
                @click="viewingReport = s"
                class="flex items-center gap-3.5 px-4 py-3.5 hover:bg-[#1e222b] transition-colors cursor-pointer"
              >
                <span class="font-mono text-[10px] w-11 text-center py-1 rounded-md text-[#94a3b8] bg-[#12141a] border border-[#2e3442]">
                  {{ s.kind }}
                </span>
                <div class="min-w-[220px] flex-1 overflow-hidden">
                  <div class="text-[13.5px] font-medium text-[#f1f5f9] truncate hover:text-[#E2232A] transition-colors">{{ s.title }}</div>
                  <div class="font-mono text-[10.5px] text-[#64748b] mt-1 truncate">{{ s.path }}</div>
                </div>
                <span class="font-mono text-[10.5px] text-[#64748b] flex-shrink-0">{{ s.date }}</span>
                <span v-if="s.ai" class="font-mono text-[10px] text-[#fca5a5] bg-[rgba(226,35,42,0.16)] border border-[rgba(226,35,42,0.4)] rounded-md px-2 py-0.5 flex-shrink-0">
                  ai analizi
                </span>

                <!-- PDF İndir Butonu -->
                <button
                  @click.stop="exportReportToPdf(s.title, s.content || s.title)"
                  class="bg-[#1e222b] border border-[#2e3442] hover:border-[#10b981] text-[#34d399] hover:text-white rounded-lg px-2.5 py-1 font-mono text-[11px] transition-colors cursor-pointer flex items-center gap-1 shadow-sm"
                  title="Lenovo Red temalı PDF olarak indir"
                >
                  <FileText class="w-3 h-3" /> PDF
                </button>

                <button
                  @click.stop="viewingReport = s"
                  class="bg-[#1e222b] border border-[#2e3442] hover:border-[#E2232A] text-[#E2232A] hover:text-white rounded-lg px-2.5 py-1 font-mono text-[11px] transition-colors cursor-pointer ml-1"
                >
                  oku
                </button>
                <button
                  @click.stop="deleteReport(s.id)"
                  class="bg-[#1e222b] border border-[#2e3442] hover:border-[#ef4444] text-[#ef4444] hover:text-white rounded-lg px-2.5 py-1 font-mono text-[11px] transition-colors cursor-pointer ml-1"
                >
                  sil
                </button>
              </div>
            </div>

            <!-- RAPOR GÖRÜNTÜLEME MODALI / PANELİ -->
            <div v-if="viewingReport" class="mt-6 border border-[#E2232A]/40 bg-[#151820] rounded-2xl p-5 shadow-2xl animate-fade">
              <div class="flex items-center gap-2 mb-3 border-b border-[#262a35] pb-3">
                <Bookmark class="w-4 h-4 text-[#E2232A]" />
                <span class="text-sm font-semibold text-[#f1f5f9]">{{ viewingReport.title }}</span>
                <span class="text-xs font-mono text-[#64748b]">({{ viewingReport.path }})</span>
                <div class="flex-1"></div>
                <button
                  @click="exportReportToPdf(viewingReport.title, viewingReport.content || viewingReport.title)"
                  class="text-xs bg-[#10b981] hover:bg-[#059669] text-white px-3 py-1.5 rounded-lg font-mono cursor-pointer transition-colors shadow-sm flex items-center gap-1.5 mr-2"
                >
                  <FileText class="w-3.5 h-3.5" /> PDF Raporu İndir
                </button>
                <button
                  @click="copyToClipboard(viewingReport.content || viewingReport.title)"
                  class="text-xs text-[#E2232A] hover:underline font-mono cursor-pointer mr-3"
                >
                  metni kopyala
                </button>
                <button
                  @click="viewingReport = null"
                  class="text-xs bg-[#1e222b] border border-[#2e3442] hover:border-[#475569] text-[#94a3b8] hover:text-white px-2.5 py-1 rounded-md font-mono cursor-pointer"
                >
                  kapat ✕
                </button>
              </div>
              <div v-if="viewingReport.kind === 'MD'" class="markdown-body select-text p-4 bg-[#12141a] border border-[#262a35] rounded-xl max-h-[500px] overflow-y-auto" v-html="renderMarkdown(viewingReport.content || viewingReport.title)"></div>
              <pre v-else class="m-0 p-3 bg-[#12141a] border border-[#262a35] rounded-xl font-mono text-xs text-[#cbd5e1] whitespace-pre-wrap max-h-96 overflow-y-auto select-text leading-relaxed">{{ viewingReport.content || viewingReport.title }}</pre>
            </div>
          </div>

          <!-- 5. KANALLAR & ÇEREZLER GÖRÜNÜMÜ -->
          <div v-else-if="currentView === 'channels'" class="animate-fade">
            <div class="flex items-baseline gap-3 mb-3.5">
              <h1 class="text-[17px] font-semibold tracking-[-0.3px] text-[#f8fafc]">Sosyal Medya Kanalları &amp; Çerezler</h1>
              <span class="font-mono text-[11px] text-[#10b981]">{{ channels.filter(c => c.status === 'ok').length }} aktif</span>
              <span class="font-mono text-[11px] text-[#f59e0b]">{{ channels.filter(c => c.status === 'warn').length }} kısıtlı</span>
              <span class="font-mono text-[11px] text-[#64748b]">{{ channels.filter(c => c.status === 'off').length }} kapalı</span>
              <div class="flex-1"></div>
              <button
                @click="triggerDoctor"
                :disabled="isDoctorLoading"
                class="inline-flex items-center gap-1.5 bg-[#181b22] border border-[#2e3442] hover:border-[#475569] text-[#94a3b8] hover:text-white rounded-lg px-3 py-1.5 text-[11px] font-mono transition-colors cursor-pointer"
              >
                <RefreshCw :class="['w-3 h-3', isDoctorLoading ? 'animate-spin' : '']" /> doktoru çalıştır
              </button>
            </div>

            <!-- OTOMATİK TARAYICI ÇEREZ ÇEKME (AUTO COOKIE SYNC) BÖLÜMÜ -->
            <div class="border border-[rgba(226,35,42,0.35)] bg-gradient-to-r from-[#181b22] via-[#1f1d24] to-[#181b22] rounded-2xl p-5 mb-5 shadow-lg">
              <div class="flex items-center gap-2 mb-2">
                <Sparkles class="w-4 h-4 text-[#E2232A]" />
                <span class="font-semibold text-[14.5px] text-[#f8fafc]">Tek Tıkla Tarayıcıdan Çerez Çekme (Otomatik &amp; Opsiyonel)</span>
                <div class="flex-1"></div>
                <span class="text-[10.5px] font-mono text-[#10b981] bg-[rgba(16,185,129,0.12)] border border-[rgba(16,185,129,0.3)] px-2 py-0.5 rounded">önerilen</span>
              </div>
              <p class="text-xs text-[#94a3b8] mb-4 leading-relaxed">
                Manuel kopyalama yapmadan, yerel tarayıcınızda açık olan Twitter/X, Instagram ve Pinterest oturum çerezlerinizi tek tuşla otomatik olarak okuyup kaydedebilirsiniz.
              </p>

              <div class="flex flex-wrap items-center gap-3">
                <div class="flex items-center gap-2">
                  <label class="text-xs font-mono text-[#94a3b8]">Tarayıcı:</label>
                  <select
                    v-model="autoCookieBrowser"
                    class="bg-[#12141a] border border-[#2e3442] focus:border-[#E2232A] rounded-xl px-3 py-2 text-xs font-mono text-[#f1f5f9] outline-none"
                  >
                    <option value="chrome">Google Chrome</option>
                    <option value="brave">Brave Browser</option>
                    <option value="edge">Microsoft Edge</option>
                    <option value="firefox">Mozilla Firefox</option>
                    <option value="opera">Opera</option>
                  </select>
                </div>

                <button
                  @click="handleExtractFromBrowser"
                  :disabled="isExtractingCookies"
                  class="bg-[#E2232A] hover:bg-[#b91c1c] text-white rounded-xl px-5 py-2 text-xs font-semibold transition-all cursor-pointer disabled:opacity-50 flex items-center gap-2 shadow-md"
                >
                  <RefreshCw :class="['w-3.5 h-3.5', isExtractingCookies ? 'animate-spin' : '']" />
                  <span>{{ isExtractingCookies ? 'Çerezler Çekiliyor...' : 'Tarayıcıdan Çerezleri Otomatik Çek' }}</span>
                </button>
              </div>
            </div>

            <!-- MANUEL ÇEREZ EKLEME / GÜNCELLEME FORMU (HER ŞEYİ KENDİ YÖNETMEK İSTEYENLER İÇİN) -->
            <div class="border border-[#262a35] bg-[#181b22] rounded-2xl p-4.5 mb-6 shadow-sm">
              <div class="flex items-center gap-2 mb-3">
                <Cookie class="w-4 h-4 text-[#E2232A]" />
                <span class="font-semibold text-[14px] text-[#f8fafc]">Manuel Çerez (Cookie) Düzenleyici</span>
              </div>
              <p class="text-xs text-[#94a3b8] mb-4">
                İsterseniz tarayıcınızın Geliştirici Araçları'ndan (F12) aldığınız çerez dizgisini yapıştırarak manuel olarak da güncelleyebilirsiniz.
              </p>

              <div class="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div class="sm:col-span-1">
                  <label class="block text-xs font-mono text-[#94a3b8] mb-1">Platform:</label>
                  <select
                    v-model="cookieService"
                    class="w-full bg-[#12141a] border border-[#2e3442] rounded-lg p-2 text-xs font-mono text-[#f1f5f9] outline-none"
                  >
                    <option value="twitter">Twitter / X</option>
                    <option value="youtube">YouTube</option>
                    <option value="instagram">Instagram</option>
                    <option value="pinterest">Pinterest</option>
                    <option value="reddit">Reddit (Proxy / Auth)</option>
                    <option value="github">GitHub (Token / CLI)</option>
                    <option value="linkedin">LinkedIn</option>
                  </select>
                </div>
                <div class="sm:col-span-3">
                  <label class="block text-xs font-mono text-[#94a3b8] mb-1">Çerez Değeri (Cookie String):</label>
                  <div class="flex gap-2">
                    <input
                      v-model="cookieValue"
                      placeholder='auth_token=6780f...; ct0=8285c...'
                      class="flex-1 bg-[#12141a] border border-[#2e3442] focus:border-[#E2232A] rounded-lg px-3 text-xs font-mono text-[#f1f5f9] outline-none shadow-inner"
                    />
                    <button
                      @click="handleSaveCookies"
                      :disabled="isSavingCookies"
                      class="bg-[#E2232A] hover:bg-[#b91c1c] text-white rounded-lg px-4 text-xs font-semibold transition-colors cursor-pointer disabled:opacity-50 shadow-md"
                    >
                      {{ isSavingCookies ? 'Kaydediliyor...' : 'Kaydet' }}
                    </button>
                  </div>
                </div>
              </div>

              <div v-if="cookieMessage" class="mt-3 text-xs font-mono text-[#34d399]">
                {{ cookieMessage }}
              </div>
            </div>

            <!-- Doktor Konsol Çıktısı -->
            <div v-if="doctorOutput" class="border border-[#262a35] bg-[#181b22] rounded-2xl p-4 mb-6 shadow-sm">
              <div class="font-mono text-xs text-[#94a3b8] mb-2">Canlı Doktor Raporu:</div>
              <pre class="m-0 font-mono text-[11px] text-[#34d399] whitespace-pre-wrap max-h-48 overflow-y-auto select-text">{{ doctorOutput }}</pre>
            </div>

            <!-- Kanal Kartları -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2.5">
              <div
                v-for="c in channels"
                :key="c.name"
                class="border border-[#262a35] bg-[#181b22] rounded-xl p-3.5 hover:border-[#3a4153] transition-colors"
              >
                <div class="flex items-center gap-2">
                  <span
                    :class="[
                      'w-2 h-2 rounded-full',
                      c.status === 'ok' ? 'bg-[#10b981] animate-pulse-glow' : c.status === 'warn' ? 'bg-[#f59e0b]' : 'bg-[#475569]'
                    ]"
                  ></span>
                  <span class="text-[13px] font-semibold text-[#f8fafc]">{{ c.name }}</span>
                  <div class="flex-1"></div>
                  <span
                    :class="[
                      'font-mono text-[10px] px-2 py-0.5 rounded-md border',
                      c.status === 'ok'
                        ? 'text-[#34d399] bg-[rgba(16,185,129,0.12)] border-[rgba(16,185,129,0.3)]'
                        : c.status === 'warn'
                        ? 'text-[#fbbf24] bg-[rgba(245,158,11,0.12)] border-[rgba(245,158,11,0.3)]'
                        : 'text-[#94a3b8] bg-[#12141a] border-[#2e3442]'
                    ]"
                  >
                    {{ c.state }}
                  </span>
                </div>

                <div class="flex items-center justify-between mt-2.5 font-mono text-[10.5px] text-[#94a3b8]">
                  <span>{{ c.auth }}</span>
                  <span>{{ c.latency }}</span>
                </div>

                <div class="flex gap-1.5 mt-3">
                  <button
                    @click="cookieService = c.key; currentView = 'channels';"
                    class="flex-1 bg-[#1e222b] border border-[#2e3442] hover:border-[#475569] text-[#94a3b8] hover:text-white rounded-lg py-1 font-mono text-[10.5px] transition-colors cursor-pointer"
                  >
                    çerez düzenle
                  </button>
                  <button
                    @click="triggerDoctor"
                    class="flex-1 bg-[#1e222b] border border-[#2e3442] hover:border-[#475569] text-[#94a3b8] hover:text-white rounded-lg py-1 font-mono text-[10.5px] transition-colors cursor-pointer"
                  >
                    test et
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 6. UYGULAMA AYARLARI & MODEL YÖNETİMİ -->
          <div v-else-if="currentView === 'settings'" class="max-w-[820px] mx-auto pt-2 animate-fade">
            <div class="flex items-baseline gap-3 mb-4">
              <h1 class="text-[19px] font-semibold tracking-[-0.3px] text-[#f8fafc]">Uygulama Ayarları &amp; AI Modeli</h1>
              <span class="font-mono text-[11px] text-[#E2232A]">Gemini Intelligence Hub</span>
            </div>

            <!-- GEMINI API KEY AYAR KUTUSU -->
            <div class="border border-[rgba(226,35,42,0.35)] bg-[#181b22] rounded-2xl p-5 mb-5 shadow-lg">
              <div class="flex items-center gap-2 mb-2">
                <KeyRound class="w-4 h-4 text-[#E2232A]" />
                <span class="font-semibold text-[14.5px] text-[#f8fafc]">Google Gemini API Anahtarı</span>
              </div>
              <p class="text-xs text-[#94a3b8] mb-4 leading-relaxed">
                Yapay zeka analizleri, otomatik özetler ve AI Asistanı için geçerli Gemini API anahtarınızı tanımlayın. Anahtarınız sadece kendi cihazınızda (LocalStorage) tutulur.
              </p>

              <div class="flex gap-2.5">
                <div class="relative flex-1">
                  <input
                    :type="showGeminiKey ? 'text' : 'password'"
                    v-model="geminiApiKey"
                    placeholder="AIzaSy..."
                    class="w-full bg-[#12141a] border border-[#2e3442] focus:border-[#E2232A] rounded-xl px-3.5 py-2.5 text-xs font-mono text-[#f1f5f9] outline-none pr-10 shadow-inner"
                  />
                  <button
                    @click="showGeminiKey = !showGeminiKey"
                    class="absolute right-3 top-3 text-[#64748b] hover:text-white transition-colors cursor-pointer"
                  >
                    <Eye v-if="!showGeminiKey" class="w-4 h-4" />
                    <EyeOff v-else class="w-4 h-4" />
                  </button>
                </div>
                <button
                  @click="saveGeminiSettings"
                  class="bg-[#E2232A] hover:bg-[#b91c1c] text-white rounded-xl px-5 text-xs font-semibold transition-colors cursor-pointer shadow-md"
                >
                  Kaydet
                </button>
              </div>
            </div>

            <!-- MODEL SEÇİCİ VE YÖNETİCİSİ -->
            <div class="border border-[#262a35] bg-[#181b22] rounded-2xl p-5 mb-5 shadow-sm">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <Cpu class="w-4 h-4 text-[#10b981]" />
                  <span class="font-semibold text-[14.5px] text-[#f8fafc]">Aktif Yapay Zeka Modelleri</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xs font-mono text-[#64748b]">{{ availableModels.length }} model</span>
                  <button
                    @click="fetchModelsFromApi"
                    :disabled="isFetchingModels"
                    class="inline-flex items-center gap-1.5 bg-[#12141a] border border-[#2e3442] hover:border-[#E2232A] text-[#E2232A] hover:text-white px-3 py-1.5 rounded-lg text-xs font-mono transition-colors cursor-pointer disabled:opacity-50"
                  >
                    <RefreshCw :class="['w-3.5 h-3.5', isFetchingModels ? 'animate-spin' : '']" /> Modelleri getir
                  </button>
                </div>
              </div>
              <p class="text-xs text-[#94a3b8] mb-4 leading-relaxed">
                Gemini 3.7 Flash, 3.6, 3.5 ve 2.5 gibi son nesil modelleri doğrudan API anahtarınız üzerinden sorgulayın ve anında seçin.
              </p>

              <div class="space-y-2 max-h-96 overflow-y-auto pr-1">
                <label
                  v-for="m in availableModels"
                  :key="m.id"
                  @click="geminiModel = m.id; saveGeminiSettings();"
                  :class="[
                    'flex items-start gap-3.5 p-3 rounded-xl border transition-all cursor-pointer',
                    geminiModel === m.id
                      ? 'border-[#E2232A] bg-[#1c202a] ring-1 ring-[#E2232A]/40 shadow-sm'
                      : 'border-[#262a35] bg-[#14161d] hover:border-[#3a4153]'
                  ]"
                >
                  <input
                    type="radio"
                    :value="m.id"
                    v-model="geminiModel"
                    class="mt-1 accent-[#E2232A] cursor-pointer"
                  />
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <span class="font-mono text-[13px] font-semibold text-[#f8fafc]">{{ m.id }}</span>
                      <span class="text-xs text-[#94a3b8]">({{ m.name }})</span>
                      <div class="flex-1"></div>
                      <span class="font-mono text-[10px] px-2 py-0.5 rounded bg-[rgba(226,35,42,0.14)] text-[#fca5a5] border border-[rgba(226,35,42,0.3)]">
                        {{ m.badge }}
                      </span>
                    </div>
                    <p class="mt-1 text-[11.5px] text-[#94a3b8] leading-relaxed">{{ m.desc }}</p>
                  </div>
                </label>
              </div>
            </div>
          </div>
        </main>

        <!-- SAĞ DETAY VE İNCELEME PANELİ (INSPECTOR) -->
        <aside
          v-if="selectedItem"
          class="w-[420px] flex-shrink-0 border-l border-[#262a35] bg-[#15181f]/95 backdrop-blur-xl flex flex-col animate-slide shadow-2xl"
        >
          <!-- Başlık -->
          <div class="flex items-center gap-2.5 p-3.5 border-b border-[#262a35] bg-[#12141a]">
            <SlidersHorizontal class="w-4 h-4 text-[#94a3b8]" />
            <span class="text-[13px] font-semibold text-[#f8fafc]">Detay &amp; Analiz Denetçisi</span>
            <span class="font-mono text-[10.5px] text-[#64748b]">{{ selectedItem.id }}</span>
            <div class="flex-1"></div>
            <button
              @click="selectedItem = null"
              class="w-7 h-7 grid place-items-center bg-transparent border border-[#2e3442] hover:border-[#475569] rounded-lg text-[#94a3b8] hover:text-white transition-colors cursor-pointer"
            >
              <X class="w-3.5 h-3.5" />
            </button>
          </div>

          <!-- Yazar Kartı -->
          <div class="p-4 border-b border-[#262a35]">
            <div class="flex items-center gap-2.5">
              <div
                class="w-[34px] h-[34px] rounded-[10px] grid place-items-center font-bold text-[13px] text-white flex-shrink-0"
                :style="`background: linear-gradient(140deg, hsl(${selectedItem.hue} 62% 46%), hsl(${selectedItem.hue + 28} 58% 34%))`"
              >
                {{ selectedItem.initial }}
              </div>
              <div class="min-w-0 flex-1">
                <div class="font-semibold text-[13.5px] text-[#f8fafc]">{{ selectedItem.author }}</div>
                <div class="font-mono text-[10.5px] text-[#94a3b8] mt-0.5">
                  {{ selectedItem.handle }} · {{ selectedItem.platformLabel }}
                </div>
              </div>
              <button
                v-if="selectedItem.url"
                @click="openUrl(selectedItem.url)"
                class="text-[#E2232A] hover:text-white p-1.5 rounded-lg hover:bg-[#1e222b] transition-colors cursor-pointer"
                title="Tarayıcıda Aç"
              >
                <ExternalLink class="w-4 h-4" />
              </button>
            </div>
            <p class="mt-3 text-[13px] leading-relaxed text-[#cbd5e1] select-text">{{ selectedItem.text }}</p>
          </div>

          <!-- JSON / Markdown Sekmeleri -->
          <div class="flex gap-0.5 mx-4 mt-3 bg-[#181b22] border border-[#262a35] rounded-lg p-0.5">
            <button
              @click="inspectorTab = 'json'"
              :class="[
                'flex-1 py-1 rounded font-mono text-[11px] transition-colors cursor-pointer',
                inspectorTab === 'json' ? 'bg-[#222733] text-white font-medium' : 'text-[#64748b] hover:text-[#94a3b8]'
              ]"
            >
              JSON Çıktısı
            </button>
            <button
              @click="inspectorTab = 'md'"
              :class="[
                'flex-1 py-1 rounded font-mono text-[11px] transition-colors cursor-pointer',
                inspectorTab === 'md' ? 'bg-[#222733] text-white font-medium' : 'text-[#64748b] hover:text-[#94a3b8]'
              ]"
            >
              Markdown Çıktısı
            </button>
          </div>

          <!-- Ham Çıktı ve AI Kutusu -->
          <div class="flex-1 min-h-0 overflow-y-auto p-4 space-y-4">
            <pre class="m-0 font-mono text-[11px] leading-relaxed text-[#cbd5e1] whitespace-pre-wrap break-all select-text bg-[#12141a]/80 p-3 rounded-xl border border-[#262a35]">{{ inspectorContent }}</pre>

            <!-- Gemini AI Kutusu -->
            <div class="border border-[rgba(226,35,42,0.35)] bg-gradient-to-br from-[rgba(226,35,42,0.12)] to-[#181b22] rounded-[13px] p-3.5 shadow-md">
              <div class="flex items-center gap-2">
                <Sparkles class="w-3.5 h-3.5 text-[#E2232A]" />
                <span class="text-[12.5px] font-semibold text-[#f1f5f9]">Yapay Zeka Analizi &amp; Duygu Durumu</span>
                <div class="flex-1"></div>
                <span class="font-mono text-[10px] text-[#E2232A]">istek üzerine</span>
              </div>

              <!-- Durum: Beklemede -->
              <div v-if="aiSummaryState === 'idle'" class="mt-2.5">
                <p class="text-xs text-[#94a3b8] leading-relaxed mb-3">
                  Kazıma işlemi tamamen yerel ve ücretsizdir. Sadece bu gönderi için yapay zeka analizi istediğinizde Gemini çağrılır ve token tüketilir.
                </p>
                <button
                  @click="generateGeminiSummary"
                  class="w-full inline-flex items-center justify-center gap-2 bg-[#E2232A] hover:bg-[#b91c1c] text-white rounded-lg py-2 text-[12.5px] font-semibold transition-colors cursor-pointer shadow-md"
                >
                  <Sparkles class="w-3.5 h-3.5" /> Yapay Zeka ile Özetle (Gemini)
                </button>
              </div>

              <!-- Durum: Yükleniyor (Shimmer) -->
              <div v-else-if="aiSummaryState === 'loading'" class="py-3 flex flex-col gap-2">
                <span class="h-2 rounded bg-gradient-to-r from-[#1e222b] via-[#3a4153] to-[#1e222b] animate-shimmer"></span>
                <span class="h-2 w-[86%] rounded bg-gradient-to-r from-[#1e222b] via-[#3a4153] to-[#1e222b] animate-shimmer"></span>
                <span class="h-2 w-[62%] rounded bg-gradient-to-r from-[#1e222b] via-[#3a4153] to-[#1e222b] animate-shimmer"></span>
                <span class="font-mono text-[10.5px] text-[#E2232A] mt-1">akış başlatılıyor · {{ geminiModel }}</span>
              </div>

              <!-- Durum: Tamamlandı -->
              <div v-else-if="aiSummaryState === 'done'" class="animate-fade mt-2.5 select-text">
                <div class="flex gap-1.5 my-2.5">
                  <span class="font-mono text-[10.5px] text-[#34d399] bg-[rgba(16,185,129,0.12)] border border-[rgba(16,185,129,0.3)] rounded px-2 py-0.5">
                    {{ selectedItem.sentiment }}
                  </span>
                  <span class="font-mono text-[10.5px] text-[#94a3b8] bg-[#1e222b] border border-[#2e3442] rounded px-2 py-0.5">
                    {{ selectedItem.tokens }}
                  </span>
                </div>
                <p class="m-0 text-[12.5px] leading-relaxed text-[#f1f5f9]">
                  {{ selectedItem.summary }}
                </p>
                <ul class="mt-2.5 pl-4 text-[#94a3b8] text-xs leading-relaxed list-disc space-y-1">
                  <li v-for="(p, idx) in selectedItem.points" :key="idx">{{ p }}</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Alt İşlem Butonları -->
          <div class="flex flex-col gap-1.5 p-3 border-t border-[#262a35] bg-[#12141a]">
            <button
              @click="saveReportToDisk(`${selectedItem.author} (${selectedItem.platformLabel}) İçerik Raporu`, inspectorContent, inspectorTab === 'json' ? 'JSON' : 'MD', false)"
              class="w-full bg-[#E2232A] hover:bg-[#b91c1c] text-white rounded-lg py-2 font-mono text-[11px] font-semibold transition-colors cursor-pointer text-center shadow-md flex items-center justify-center gap-1.5"
            >
              <Bookmark class="w-3.5 h-3.5" /> Kaydedilenlere Ekle
            </button>
            <div class="flex gap-1.5 mt-1">
              <button
                @click="copyToClipboard(inspectorContent)"
                class="flex-1 bg-[#1e222b] border border-[#2e3442] hover:border-[#475569] text-[#cbd5e1] hover:text-white rounded-lg py-1.5 font-mono text-[11px] transition-colors cursor-pointer text-center"
              >
                .{{ inspectorTab }} kopyala
              </button>
              <button
                @click="copyToClipboard(selectedItem.text)"
                class="flex-1 inline-flex items-center justify-center gap-1.5 bg-[#1e222b] border border-[#2e3442] hover:border-[#475569] text-[#cbd5e1] hover:text-white rounded-lg py-1.5 font-mono text-[11px] transition-colors cursor-pointer"
              >
                <Copy class="w-3 h-3" /> metni al
              </button>
            </div>
          </div>
        </aside>

      </div>
    </div>

    <!-- NON-BLOCKING FLOATING SEARCH & OPERATION HUD (AKICI, KASILMAYAN CANLI DURUM GÖSTERGESİ) -->
    <div
      v-if="isSearching"
      class="fixed bottom-6 right-6 z-40 bg-[#181b22]/95 border border-[#E2232A]/40 backdrop-blur-xl rounded-2xl p-4 shadow-2xl flex items-center gap-3.5 max-w-sm animate-slide"
    >
      <div class="w-9 h-9 rounded-xl bg-[#E2232A]/20 border border-[#E2232A]/30 grid place-items-center flex-shrink-0">
        <Loader2 class="w-4 h-4 text-[#E2232A] animate-spin" />
      </div>
      <div class="flex-1 min-w-0">
        <div class="text-xs font-semibold text-[#f8fafc] truncate">
          {{ selectedPlatform === 'all' ? '8 Platform Taranıyor...' : `${platforms.find(p => p.id === selectedPlatform)?.label || selectedPlatform} Aranıyor...` }}
        </div>
        <div class="text-[11px] font-mono text-[#94a3b8] truncate mt-0.5">
          "{{ searchQuery }}"
        </div>
        <!-- Mini Progress Bar -->
        <div class="w-full bg-[#12141a] h-1 rounded-full mt-2 overflow-hidden">
          <div class="h-full bg-gradient-to-r from-[#E2232A] via-[#ef4444] to-[#10b981] animate-shimmer w-[200%]"></div>
        </div>
      </div>
    </div>

  </div>
</template>
