from django.db import models
from django.utils.text import slugify

class Market(models.Model):
    name = models.CharField(max_length=255, verbose_name="Market Adı")
    description = models.TextField(verbose_name="Market Açıklaması", blank=True, null=True)
    location = models.CharField(max_length=500, verbose_name="Market Konumu", blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Slug (URL)")
    min_price = models.IntegerField(default=0, verbose_name="Minimum Fiyat")
    status = models.BooleanField(default=True, verbose_name="Durum (Aktif/Pasif)")
    
    # Görseller için (upload_to parametresi resimlerin yükleneceği klasörü belirtir)
    logo = models.ImageField(upload_to='market_logos/', blank=True, null=True, verbose_name="Market Logosu")
    banner = models.ImageField(upload_to='market_banners/', blank=True, null=True, verbose_name="Market Afişi")

    class Meta:
        verbose_name = "Market"
        verbose_name_plural = "Marketler"

    def __str__(self):
        return self.name

    # İsteğe bağlı: Eğer slug alanının market isminden otomatik üretilmesini istersen:
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)