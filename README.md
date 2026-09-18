# SYSTEM BREACH — Hacker ve Sistem Güvenliği (Prototip)

Python + Pygame ile yazılmış, hikaye tabanlı 2D algoritma/kodlama öğretim oyununun
temel mimarisi. 25 hacker, 4 bölüm, tam bir kod-düzeltme mekaniği ve çoklu son içerir.

## Klasör Yapısı

```
hacker_game/
├── main.py                  # Pygame giriş noktası (SADECE çizim + girdi)
├── build_data.py            # data/hackers.json dosyasını üreten script (kaynak veri burada)
├── data/
│   └── hackers.json         # 25 hacker'ın tüm verisi (diyalog, hatalı kod, çözüm)
└── systems/
    ├── hacker.py             # Hacker veri sınıfı (dataclass)
    ├── code_challenge.py     # Kod doğrulama / "savaş" mekaniği
    ├── dialogue_system.py    # Diyalog durum makinesi (intro/success/final)
    └── game_manager.py       # Oyunun beyni: akışı, sırayı, skoru yönetir
```

## Nasıl Çalıştırılır

```bash
pip install pygame
python3 main.py
```

**Kontroller:**
- Menü: `ENTER` başlat
- Diyalog: `ENTER` devam et
- Kod savaşı: hatalı olduğunu düşündüğün satıra **tıkla** (birden fazla satır
  için `SHIFT` + tıkla ile aralık seç), alt kutuya düzeltmeni yaz, `ENTER` gönder
- Final seçimi: `Y` = Karanlık tarafa katıl (Kötü Son) / `N` = Reddet (İyi Son)
- Her yerde `ESC` çıkış

## Mimari Kararlar (Neden Böyle Tasarlandı?)

1. **Veri / Mantık / Görsel ayrımı**: `hackers.json` sadece veri taşır,
   `systems/` klasörü pygame'den tamamen habersiz saf Python mantığıdır,
   `main.py` ise sadece çizim ve girdi. Bu sayede:
   - Arayüzü değiştirmek istersen (örn. web'e taşımak) `systems/` klasörüne
     hiç dokunmazsın.
   - `test` yazmak kolaydır (bkz. aşağıdaki test bölümü) — pygame açmadan
     tüm oyun mantığını test edebilirsin.

2. **`fix_type` sistemi**: Her hata farklı şekilde düzeltilir — bazen bir satır
   değişir (`replace`), bazen eksik bir satır eklenir (`insert_after` — örn.
   unutulmuş `count++` veya `delete`), bazen fazladan bir satır silinmelidir
   (`delete` — örn. yanlış yerdeki `return`). Bu, gerçek dünyadaki hata
   çeşitliliğini (syntax, mantık, kaynak yönetimi) yansıtır.

3. **`CodeChallenge._normalize()`**: Oyuncuyu boşluk/girinti farkından dolayı
   haksız yere cezalandırmamak için karşılaştırma öncesi metni normalize eder.
   İleride gerçek bir dil parser'ına (örn. `ast` modülü) bağlanmak istersen
   sadece bu sınıfı değiştirmen yeterli.

4. **`GameManager` tek otorite**: `main.py` hiçbir zaman `current_index`'i
   direkt değiştirmez veya JSON'u okumaz — her şey `GameManager` metodları
   üzerinden akar. Bu, ileride "seviye atlama", "ipucu hakkı", "can sistemi"
   gibi özellikler eklerken tek bir yerden yönetim sağlar.

## Test Etme (Pygame Açmadan)

```python
from systems.game_manager import GameManager

gm = GameManager()
gm.start_game()
h = gm.current_hacker
gm.player_confirms_intro()
result = gm.submit_fix(h.bug_start_line, h.bug_end_line, h.fixed_code)
print(result.success, result.message)
```

## Veri Setini Genişletme

Yeni bir hacker eklemek için `build_data.py` içindeki `HACKERS` listesine yeni
bir `dict` ekleyip scripti tekrar çalıştırman yeterli:

```bash
python3 build_data.py
```

Yeni bir hacker için AI'ya vereceğin ikinci aşama alt-prompt örneği:

> "Bana `data/hackers.json` şemasına uygun, LeetCode'daki 'Merge Intervals'
> sorusuna benzer, aralıkları birleştirirken `<` yerine `<=` kullanılması
> gereken bir sınır (boundary) hatası içeren Seviye 26 Hacker senaryosu
> Python dilinde yazar mısın? Şema alanları: id, chapter, name, company,
> language, error_type, intro_dialogue, success_dialogue, buggy_code,
> bug_start_line, bug_end_line, fix_type, fixed_code, explanation."

## Sıradaki Adımlar (Öneriler)

- **İpucu sistemi**: `Hacker` sınıfına `hints: list[str]` ekleyip, oyuncu
  3 kez yanlış denerse bir ipucu göster.
- **Can/Zaman sistemi**: `GameManager.attempts_this_hacker` zaten sayılıyor —
  buna bağlı bir "can" mekaniği eklemek kolay.
- **Görsel tema**: Matrix/terminal estetiği korunarak `pygame.freetype` ile
  daktilo (typewriter) efekti veya arka planda düşen kod animasyonu eklenebilir.
- **Ses**: Doğru/yanlış cevaplar için basit `.wav` efektleri `pygame.mixer` ile
  kolayca entegre edilir.
