# Portal Runner

## Proje Açıklaması

Portal Runner, PyOpenGL kullanılarak geliştirilmiş 3D bir koşu oyunudur. Oyunda, sonsuz bir platforma sahip dünyada koşarken farklı temalı (çöl, buz, orman) dünyalara portallar aracılığıyla geçiş yapabilirsiniz. Ana amacınız, platformlardan düşmeden mümkün olduğunca çok altın toplamak ve ileri gitmektir. Toplanan her altın puanınızı artırır ve portallardan geçmek bonus puan kazandırır.

Oyun özellikleri:
- Farklı temalarda (çöl, buz, orman) dünyalar
- Portal animasyonu ve dünya geçişleri
- Sürekli puan gösterimi
- Her toplanan altın ile puan artışı (puan += 10)
- Yüksek skor takibi
- Rastgele oluşturulan platformlar ve engeller
- 3 şeritli oyun mekanizması
- Artan zorluk seviyesi

## Kurulum ve Çalıştırma

### Gerekli Kütüphaneler

Oyunu çalıştırmak için aşağıdaki kütüphanelere ihtiyacınız vardır:

```bash
pip install PyOpenGL PyOpenGL_accelerate numpy Pillow pygame
```

### Oyunu Çalıştırma

1. Tüm proje dosyalarını indirin
2. Terminalde proje klasörüne gidin
3. (İsteğe bağlı) Texture'ları oluşturmak için setup_textures.py dosyasını çalıştırın:
   ```bash
   python setup_textures.py
   ```
4. Müzik için, proje dizininde "music" adlı bir klasör oluşturun ve içine "background.mp3" adlı bir arka plan müziği ekleyin
5. Oyunu başlatmak için:
   ```bash
   python main.py
   ```

## Kontrol Şeması

Oyun aşağıdaki tuşlar ile kontrol edilir:

| Tuş | İşlev |
|-----|-------|
| A veya Sol Ok | Sola hareket et |
| D veya Sağ Ok | Sağa hareket et |
| W veya Yukarı Ok | Zıpla |
| S veya Aşağı Ok | Hızlıca yere in (zıplama sırasında) |
| Boşluk | Oyunu başlat/yeniden başlat |
| ESC | Oyundan çık |

## Oyun Akışı

1. Ana menüde, adınızı girin ve ENTER tuşuna basın
2. Oyuna başlamak için SPACE (Boşluk) tuşuna basın
3. 3 şerit arasında geçiş yaparak platformlarda ilerleyin
4. Boşluklarda düşmemek için W tuşu ile zıplayın
5. Altınları toplayarak puan kazanın
6. Portallardan geçerek farklı dünyalara seyahat edin ve bonus puan kazanın
7. Platformdan düştüğünüzde oyun biter ve puanınız yüksek skor listesine eklenir

