import os
import datetime
from django.db import models
from django.utils.text import slugify

# ==========================================================================
# 1. GÖRSEL YÜKLEME YOLLARI VE DINAMIK ISIMLENDIRME
# ==========================================================================

def market_logo_path(instance, filename):
    """
    Logo görselini 'market-adi-Logo.uzanti' şeklinde temizleyerek kaydeder.
    """
    ext = filename.split('.')[-1]
    clean_name = slugify(instance.name)
    return os.path.join('market_logos/', f"{clean_name}-Logo.{ext}")

def market_banner_path(instance, filename):
    """
    Banner görselini 'market-adi-Banner.uzanti' şeklinde temizleyerek kaydeder.
    """
    ext = filename.split('.')[-1]
    clean_name = slugify(instance.name)
    return os.path.join('market_banners/', f"{clean_name}-Banner.{ext}")


# ==========================================================================
# 2. MARKET ANA MODELI
# ==========================================================================

class Market(models.Model):
    name = models.CharField(max_length=255, verbose_name="Market Adı")
    location = models.CharField(max_length=500, verbose_name="Market Konumu", blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Slug (URL Uzantısı)")
    
    # Hatanın çözümü için admin panelin aradığı min_price alanını buraya ekledik
    min_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Minimum Sepet Tutarı")
    
    logo = models.ImageField(upload_to=market_logo_path, blank=True, null=True, verbose_name="Market Logosu")
    banner = models.ImageField(upload_to=market_banner_path, blank=True, null=True, verbose_name="Market Banner Resmi")
    
    # Genel aktiflik durumu (True: Aktif/Açık sistem, False: Sistemde pasif)
    status = models.BooleanField(default=True, verbose_name="Sistemde Aktif mi?")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Market"
        verbose_name_plural = "Marketler"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def current_status_info(self):
        """
        Marketin anlık sunucu saatine ve haftalık çalışma planına göre
        açık/kapalı durumunu hesaplar. Kapalıysa bir sonraki açılış saatini verir.
        """
        if not self.status:
            return {"status": "busy", "message": "Geçici Olarak Kapalı"}

        now = datetime.datetime.now()
        current_day = now.weekday()  # 0 = Pazartesi, ..., 6 = Pazar
        current_time = now.time()

        # Bugünün saat kaydı
        today_hours = self.hours.filter(day=current_day).first()

        is_open = False
        if today_hours and not today_hours.is_closed:
            open_t = today_hours.open_time
            close_t = today_hours.close_time

            if close_t <= open_t:
                is_open = (current_time >= open_t) or (current_time <= close_t)
            else:
                is_open = (open_t <= current_time <= close_t)

        # 1. Durum: Market şu an AÇIKSA
        if is_open:
            return {"status": "open", "message": "Açık"}

        # 2. Durum: KAPALIYSA (Bir sonraki açılış vaktini dinamik bulalım)
        # Önce bugün henüz açılmadıysa bugünün açılış saatini verelim
        if today_hours and not today_hours.is_closed and current_time < today_hours.open_time:
            return {
                "status": "busy",
                "message": f"Bugün {today_hours.open_time.strftime('%H:%M')}'da Açılacak"
            }

        # Bugün kapandıysa veya bugün tamamen kapalıysa, sonraki günleri sırayla (7 gün boyunca) kontrol et
        for i in range(1, 8):
            next_day = (current_day + i) % 7
            next_hours = self.hours.filter(day=next_day).first()
            if next_hours and not next_hours.is_closed:
                day_name = next_hours.get_day_display()
                # Eğer ilk açık gün yarınsa "Yarın", daha sonraysa günün ismini yaz (Pazartesi vb.)
                day_label = "Yarın" if i == 1 else day_name
                return {
                    "status": "busy",
                    "message": f"{day_label} {next_hours.open_time.strftime('%H:%M')}'da Açılacak"
                }

        return {"status": "busy", "message": "Kapalı"}


# ==========================================================================
# 3. HAFTALIK SABIT ÇALIŞMA SAATLERI MODELI
# ==========================================================================

class MarketBusinessHour(models.Model):
    WEEKDAYS = [
        (0, 'Pazartesi'),
        (1, 'Salı'),
        (2, 'Çarşamba'),
        (3, 'Perşembe'),
        (4, 'Cuma'),
        (5, 'Cumartesi'),
        (6, 'Pazar'),
    ]
    
    market = models.ForeignKey(
        Market, 
        on_delete=models.CASCADE, 
        related_name='hours', 
        verbose_name="Market"
    )
    day = models.IntegerField(choices=WEEKDAYS, verbose_name="Gün")
    
    # Varsayılan olarak her gün 09:00 - 22:00 arası dolu gelir
    open_time = models.TimeField(default=datetime.time(9, 0), verbose_name="Açılış Saati")
    close_time = models.TimeField(default=datetime.time(22, 0), verbose_name="Kapanış Saati")
    is_closed = models.BooleanField(default=False, verbose_name="Bugün Tamamen Kapalı mı?")

    class Meta:
        verbose_name = "Çalışma Saati"
        verbose_name_plural = "Çalışma Saatleri"
        unique_together = ('market', 'day')  # Bir marketin bir günden sadece 1 tane saat kaydı olabilir
        ordering = ['day']

    def __str__(self):
        status_str = "Kapalı" if self.is_closed else f"{self.open_time.strftime('%H:%M')} - {self.close_time.strftime('%H:%M')}"
        return f"{self.market.name} - {self.get_day_display()}: {status_str}"