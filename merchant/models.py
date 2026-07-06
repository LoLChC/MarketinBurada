from django.db import models
from markets.models import Market
from django.contrib.gis.db import models as location_models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from account.models import User, Address
from django.db.models import Q, Sum
from django.utils import timezone   
import uuid

# Create your models here.

class Branch(models.Model): #Şubeler
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
        # status_info'nun geçerli bir dictionary olup olmadığını manuel kontrol et
        if isinstance(status_info, dict):
            return status_info.get("status") == "open"
        
        return False

    @classmethod
    def find_nearest_branch(cls, market, latitude, longitude):
        customer_location = Point(longitude, latitude, srid=4326)
        now = timezone.localtime()
        current_day = now.weekday()
        current_time = now.time()

        active_branches = Branch.objects.filter(

            market=market, 
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

        # Bulunan en yakın şubenin, müşteriye olan mesafesi şubenin dağıtım menzilinden küçük veya eşit mi?
        if nearest_branch and hasattr(nearest_branch, 'mesafe'):
            # Distance objesi genelde .km veya .m property'lerine sahiptir.
            if nearest_branch.mesafe.km <= nearest_branch.delivery_radius_km:
                return nearest_branch

        return None

    
class Courier(models.Model): #Kuryeler
    COURIER_STATUS = [
        ('offline', 'Çevrimdışı'),
        ('available', 'Müsait (Şubede Bekliyor)'),
        ('delivery', 'Dağıtım   da / Siparişte'),
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
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default='motorcycle', verbose_name="Araç Tipi")
    status = models.CharField(max_length=15, choices=COURIER_STATUS, default='offline', verbose_name="Durumu")
    
    # Kurye şu an dağıtımda ise aktif olarak taşıdığı sepetin ID'si (Boşsa null olur)
    current_package = models.ForeignKey(
        'Package', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='active_couriers',
        verbose_name="Şu Anki Sepet"
    )
    
    monthly_delivery_count = models.PositiveIntegerField(default=0, verbose_name="Bu Ayki Teslimat Sayısı")
    
    # Konum Takibi
    current_location = location_models.PointField(srid=4326, null=True, geography=True, blank=True, verbose_name="Anlık Konum")

    class Meta:
        verbose_name = "Kurye"
        verbose_name_plural = "Kuryeler"

    def __str__(self):
        return f"{self.name} {self.surname} ({self.branch.neighborhood} Şubesi)"

    # Kuryenin adını ve soyadını ayırmak için yardımcı metotlar:
    def get_name(index):
        index = index.strip()
        index_parts = index.split()
        
        if not index_parts:
            return "İsimsiz"  # Tamamen boş gelirse veri tabanının çökmesini engeller
            
        if len(index_parts) == 1:
            return index_parts[0]  # Tek kelime girildiyse o kelime isimdir
            
        return " ".join(index_parts[:-1])  # Birden fazla kelime varsa sonuncu hariç hepsi isimdir

    def get_surname(index):
        index = index.strip()
        index_parts = index.split()
        
        if not index_parts:
            return "-"  # Tamamen boş gelirse veri tabanının çökmesini engeller
            
        if len(index_parts) == 1:
            return "-"  # Tek kelime girildiyse soyadı yoktur, veri tabanı için varsayılan değer dönülür
            
        return index_parts[-1]

    # Sipariş teslim edildiğinde listeye eklemeyi kolaylaştıracak ufak bir metot:
    def complete_delivery(self):
        """Kurye paketi teslim ettiğinde çalışacak yardımcı metot"""
        
        if self.current_cart_id:
            package = self.current_package
            package.status = 'delivered'
            package.delivered_at = timezone.now()
            package.save()


            # Eğer liste henüz yoksa boş liste oluştur, varsa mevcut listeye ekle
            self.monthly_delivery_count += 1
            self.status = 'available'
            self.current_package = None

            self.save(update_fields=['monthly_delivery_count', 'status', 'current_package'])

class Aisles(models.Model): #Reyonlar
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='aisles')
    title = models.CharField( max_length=50)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Kategorisi: {self.title}"
    
class AislesBranchSettings(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    category = models.ForeignKey(Aisles, on_delete=models.CASCADE)
    is_available_in_branch = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['branch', 'category'], 
                name='unique_branch_category_mapping'
            )
        ]

class Products(models.Model): # Ürünler
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='products')
    aisles = models.ForeignKey(Aisles, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    images = models.ImageField(upload_to='product-images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)


class Stocks(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    stock = models.PositiveIntegerField(default=0)

    @classmethod
    def get_product_stock(cls, product):
        """
        Bir ürünün tüm şubelerdeki toplam stok miktarını döndürür.

        Args:
            product (Products):
                Stoku hesaplanacak ürün nesnesi.

        Returns:
            int:
                Ürünün tüm şubelerdeki toplam stok miktarı.
                Eğer hiç stok kaydı yoksa 0 döner.
        """
        return cls.objects.filter(
            product=product
        ).aggregate(
            total=Sum("stock")
        )["total"] or 0

    @classmethod
    def get_branch_product_stock(cls, branch, product):
        """
        Belirli bir şubedeki ürün stok miktarını döndürür.

        Args:
            branch (Branch):
                Stok sorgulanacak şube nesnesi.

            product (Products):
                Stok sorgulanacak ürün nesnesi.

        Returns:
            int:
                Şubedeki ürünün stok miktarı.
                Kayıt bulunamazsa 0 döner.
        """
        stock_obj = cls.objects.filter(
            branch=branch,
            product=product
        ).first()

        return stock_obj.stock if stock_obj else 0
    

    @classmethod
    def get_product_stocks_by_branch(cls, product):
        """
        Bir ürünün tüm şubelerdeki stok dağılımını döndürür.

        Args:
            product (Products):
                Stokları sorgulanacak ürün.

        Returns:
            dict:
                {
                    "Merkez Şube": 15,
                    "Atakum Şube": 8,
                    "İlkadım Şube": 0
                }
        """
        return {
            stock.branch.id: {
                "neighborhood": stock.branch.neighborhood,
                "stock_count": stock.stock
            }
            for stock in cls.objects.filter(product=product).select_related("branch")
        }

class Package(models.Model):
    PACKAGE_STATUS = [
        ('pending', 'Onay Bekliyor'),
        ('preparing', 'Hazırlanıyor'),
        ('ready', 'Paket Hazır / Kurye Bekliyor'),
        ('on_the_way', 'Kurye Dağıtımda'),
        ('delivered', 'Teslim Edildi'),
        ('canceled', 'İptal Edildi'),
    ]

    # 1. TAKİP VE OPERASYONEL BAĞLANTILAR
    tracking_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Takip Numarası")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='packages', verbose_name="Müşteri")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='packages', verbose_name="Çıkış Şubesi")
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True, related_name='packages', verbose_name="Kurye")

    # 2. PAKET DETAYLARI VE ADRES
    status = models.CharField(max_length=15, choices=PACKAGE_STATUS, default='pending', verbose_name="Paket Durumu")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Paket Tutarı")
    
    # Kullanıcı adresini silse bile faturadaki adres kaybolmasın diye TextField kalmalı, 
    # ancak account.Address ile referans bağlantısı da kuruyoruz.
    address_reference = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kayıtlı Adres Referansı")
    delivery_address = models.TextField(verbose_name="Teslimat Adresi (Snapshot)")

    # Paketin içeriği (İleride PackageItem modeline geçebilirsin ama şimdilik JSON ideal)
    package_index = models.JSONField(verbose_name="Paketin İçeriği")

    # 3. LOJİSTİK VE ZAMAN ANALİZİ
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Paket Oluşturulma Zamanı")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Durum Güncellemesi")
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name="Yola Çıkış Zamanı")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Teslim Edilme Zamanı")

    class Meta:
        verbose_name = "Paket"
        verbose_name_plural = "Paketler"
        ordering = ['-created_at']

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else "Silinmiş Müşteri"
        return f"Paket #{self.id} ({self.tracking_number.hex[:8]}) - {user_name}"

    # ==========================================================================
    # OTOMATİZASYON VE HELPER METOTLAR
    # ==========================================================================

    def save(self, *args, **kwargs):
        """ Paket durumuna göre yola çıkış ve teslim tarihlerini otomatik atar. """
        if self.status == 'on_the_way' and not self.shipped_at:
            self.shipped_at = timezone.now()
        
        if self.status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
            
        super().save(*args, **kwargs)

    def assign_courier(self, courier_instance):
        """ 
        Pakete kurye atar ve kuryenin durumunu günceller.
        Kullanım: package.assign_courier(secilen_kurye)
        """
        self.courier = courier_instance
        self.status = 'on_the_way'
        self.save(update_fields=['courier', 'status'])

        # Kuryeyi dağıtıma çıkar
        courier_instance.current_package_id = self.id
        courier_instance.status = 'delivery'
        courier_instance.save(update_fields=['current_package', 'status'])