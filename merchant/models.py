from django.db import models
from markets.models import Market
from django.contrib.gis.db import models as location_models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from account.models import User
from django.db.models import Q
import datetime

# Create your models here.

class Branch(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='branches')
    neighborhood = models.CharField(max_length=255, verbose_name="Mahalle İsmi")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon")

    district = models.CharField(max_length=50, blank=True, verbose_name="İlçe")
    address = models.TextField(blank=True, verbose_name="Tam Adres")

    location = location_models.PointField(srid=4326, null=True, geography=True, blank=True, verbose_name="Tam konum")
    delivery_radius_km = models.PositiveIntegerField(default=5, verbose_name="Teslimat Menzili (KM)")

    
    
    @property
    def is_active(self):
        status_info = self.market.current_status_info
        return status_info.get("status") == "open"

    
    def find_nearest_branch(self, latitude, longitude):
        customer_location = Point(longitude, latitude, srid=4326)
        now = datetime.datetime.now()
        current_day = now.weekday()
        current_time = now.time()

        active_branches = Branch.objects.filter(

            market=self.market, 
            market__status=True, 
            market__hours__day=current_day, 
            market__hours__is_closed=False).filter(

            Q(market__hours__close_time__gt=models.F('market__hours__open_time'), 
              market__hours__open_time__lte=current_time, 
              market__hours__close_time__gte=current_time) |
            Q(market__hours__close_time__lte=models.F('market__hours__open_time'),
              market__hours__open_time__lte=current_time) |
            Q(market__hours__close_time__lte=models.F('market__hours__open_time'),
              market__hours__close_time__gte=current_time)
        )

        

        nearest_branch = active_branches.annotate(
            mesafe=Distance('location', customer_location)
        ).order_by('mesafe').first()

        return nearest_branch
    
class Courier(models.Model):
    COURIER_STATUS = [
        ('offline', 'Çevrimdışı'),
        ('available', 'Müsait (Şubede Bekliyor)'),
        ('delivery', 'Dağıtımda / Siparişte'),
    ]

    VEHICLE_TYPES = [
        ('motorcycle', 'Motosiklet'),
        ('car', 'Araba'),
    ]

    # Şube Bağlantısı
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='couriers', verbose_name="Bağlı Olduğu Şube")
    
    # Kimlik ve İletişim Bilgileri
    name = models.CharField(max_length=50, verbose_name="Adı")
    surname = models.CharField(max_length=50, verbose_name="Soyadı")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon Numarası")
    
    # Operasyonel Durumlar
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default='moto', verbose_name="Araç Tipi")
    status = models.CharField(max_length=15, choices=COURIER_STATUS, default='offline', verbose_name="Durumu")
    
    # Kurye şu an dağıtımda ise aktif olarak taşıdığı sepetin ID'si (Boşsa null olur)
    current_cart_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="Şu Anki Sepet ID")
    
    # Bu ay attığı tüm paketlerin ID'lerini bir liste olarak tutar: Örn: [12, 45, 89, 112]
    monthly_delivered_cart_ids = models.JSONField(default=list, blank=True, verbose_name="Bu Ay Teslim Edilen Sepet ID'leri")
    
    # Konum Takibi
    current_location = location_models.PointField(srid=4326, null=True, geography=True, blank=True, verbose_name="Anlık Konum")

    class Meta:
        verbose_name = "Kurye"
        verbose_name_plural = "Kuryeler"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.branch.neighborhood} Şubesi)"

    # Sipariş teslim edildiğinde listeye eklemeyi kolaylaştıracak ufak bir metot:
    def complete_delivery(self):
        """Kurye paketi teslim ettiğinde çalışacak yardımcı metot"""
        if self.current_cart_id:
            # Eğer liste henüz yoksa boş liste oluştur, varsa mevcut listeye ekle
            if not isinstance(self.monthly_delivered_cart_ids, list):
                self.monthly_delivered_cart_ids = []
                
            self.monthly_delivered_cart_ids.append(self.current_cart_id)
            self.current_cart_id = None
            self.status = 'available'
            self.save()

class Cart(models.Model):
    pass     