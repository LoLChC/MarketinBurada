from django.db import models
from markets.models import Market
from django.contrib.gis.db import models as location_models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from account.models import User, Address
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta, date
import calendar
import uuid

# Create your models here.

class Branch(models.Model): #Şubeler
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=255, verbose_name="Şube Adı")
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

    def get_day_turnover(self, date):
        turnover = self.packages.filter(
            status='delivered',
            delivered_at__date=date
        ).aggregate(
            total_turnover=Sum('total_amount')
        )['total_turnover']

        return turnover or 0.00
    
    def get_weekly_turnover(self, target_date):
        """
        Belirtilen tarihin bulunduğu haftanın (Pazartesi'den Pazar'a) cirosunu hesaplar.
        Framework'e bağımlı kalmamak için hafta aralığı Python ile hesaplanır.
        """
        # weekday() Pazartesi için 0, Pazar için 6 döner. 
        # Hedef tarihten bu değeri çıkararak haftanın ilk günü olan Pazartesi'yi buluyoruz.
        start_of_week = target_date - timedelta(days=target_date.weekday())
        
        # Pazartesi'ye 6 gün ekleyerek Pazar gününü buluyoruz.
        end_of_week = start_of_week + timedelta(days=6)

        turnover = self.packages.filter(
            status='delivered',
            delivered_at__date__range=(start_of_week, end_of_week)
        ).aggregate(
            total_turnover=Sum('total_amount')
        )['total_turnover']

        return turnover or 0.00
    
    def get_monthly_turnover(self, year, month):
        """
        Belirtilen yıl ve aydaki toplam ciroyu hesaplar.
        Veritabanına özel ay/yıl fonksiyonları yerine Python'un takvim modülü kullanılır.
        """
        # calendar.monthrange, belirtilen ayın kaç gün çektiğini döner (örn: Şubat için 28 veya 29).
        _, last_day = calendar.monthrange(year, month)
        
        # Ayın ilk günü ve son gününü net bir tarih objesi olarak oluşturuyoruz.
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        turnover = self.packages.filter(
            status='delivered',
            delivered_at__date__range=(start_date, end_date)
        ).aggregate(
            total_turnover=Sum('total_amount')
        )['total_turnover']

        return turnover or 0.00
    
class Courier(models.Model): #Kuryeler
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
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default='motorcycle', verbose_name="Araç Tipi")
    status = models.CharField(max_length=15, choices=COURIER_STATUS, default='offline', verbose_name="Durumu")
    
    # REVİZE EDİLDİ: current_package alanı tamamen kaldırıldı. Bir kuryenin birden fazla paket alabilmesi için 
    # Package modelindeki "courier" ForeignKey ilişkisi üzerinden işlem yapılacak.
    
    monthly_delivery_count = models.PositiveIntegerField(default=0, verbose_name="Bu Ayki Teslimat Sayısı")
    
    # Konum Takibi
    current_location = location_models.PointField(srid=4326, null=True, geography=True, blank=True, verbose_name="Anlık Konum")

    class Meta:
        verbose_name = "Kurye"
        verbose_name_plural = "Kuryeler"

    def __str__(self):
        return f"{self.name} {self.surname} ({self.branch.name} Şubesi)"

    # Kuryenin adını ve soyadını ayırmak için yardımcı metotlar:
    @staticmethod
    def get_name(index):
        index = index.strip()
        index_parts = index.split()
        
        if not index_parts:
            return "İsimsiz"
            
        if len(index_parts) == 1:
            return index_parts[0]
            
        return " ".join(index_parts[:-1])

    @staticmethod
    def get_surname(index):
        index = index.strip()
        index_parts = index.split()
        
        if not index_parts:
            return "-"
            
        if len(index_parts) == 1:
            return "-"
            
        return index_parts[-1]

    # ==========================================================================
    # OTOMATİZASYON VE HELPER METOTLAR
    # ==========================================================================

    def get_completed_packages_last_30_days(self):
        """
        Kuryenin son 30 gün içerisinde başarıyla teslim ettiği paketleri döndürür.
        """
        # YENİ EKLENDİ: Framework bağımlılığını azaltmak için zaman aralığı Python'un yerleşik timedelta modülüyle hesaplandı.
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # REVİZE EDİLDİ: Sadece ID'leri veren 'values_list' kaldırıldı. 
        # Kurye sayfasında paket detaylarını gösterebilmen için direkt filtrelenmiş QuerySet döndürüldü.
        return self.packages.filter(
            status='delivered',
            delivered_at__gte=thirty_days_ago
        ).order_by('-delivered_at') # YENİ EKLENDİ: Sayfada en son teslim edilen paket en üstte görünsün diye sıralama eklendi.

    def get_active_packages(self):
        """
        Kuryenin şu anda dağıtımda olduğu (üstüne aldığı) tüm paketleri getirir.
        """
        # YENİ EKLENDİ: Kurye sayfasında kuryenin anlık taşıdığı tüm paketleri filtreleyip gösterebilmen için eklendi.
        return self.packages.filter(status='on_the_way')

    def complete_delivery(self, package):
        """
        Kurye, üzerinde bulunan spesifik bir paketi teslim ettiğinde çalışır.
        """
        # REVİZE EDİLDİ: Kuryenin üstünde birden fazla paket olabileceği için parametre olarak dışarıdan 'package' objesi alındı.
        if package.courier == self and package.status == 'on_the_way':
            package.status = 'delivered'
            package.delivered_at = timezone.now()
            package.save(update_fields=['status', 'delivered_at'])

            self.monthly_delivery_count += 1
            
            # YENİ EKLENDİ: Kuryenin üzerinde başka aktif paket kalıp kalmadığı kontrol ediliyor.
            if not self.get_active_packages().exists():
                self.status = 'available'
            
            self.save(update_fields=['monthly_delivery_count', 'status'])

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
    ailes = models.ForeignKey(
        Aisles,
        on_delete=models.CASCADE,
        related_name="stocks"
    )
    stock = models.PositiveIntegerField(default=0)

    @classmethod
    def get_branch_stock_details(cls, branch):
        """
        Belirli bir şubedeki tüm ürünlerin stok miktarını ve reyon (ailes) bilgisini döndürür.

        Branch saygasında göstermek için kullanılacak. 

        Args:
            branch (Branch): 
                Stok sorgulanacak şube nesnesi.

        Returns:
            dict: 
                Ürün adı anahtarına (key) sahip, stok ve reyon detaylarını içeren sözlük.
                Örnek Çıktı:
                {
                    "Ürün Adı 1": {"stock": 15, "ailes": "Meyve Sebze"},
                    "Ürün Adı 2": {"stock": 8, "ailes": "Süt Ürünleri"},
                    "Ürün Adı 3": {"stock": 0, "ailes": None}
                }
        """
        # Veritabanı sorgusunu optimize etmek için hem product hem de ailes 
        # ilişkilerini select_related içerisine alıyoruz (N+1 problemini önlemek için).
        queryset = cls.objects.filter(
            branch=branch,
            product__is_active=True
        ).select_related("product", "ailes")

        return {
            stock.product.title: {
                "stock": stock.stock,
                "ailes": stock.ailes.name if stock.ailes else None
            }
            for stock in queryset
        }

    @classmethod
    # def get

    @classmethod
    def get_all(cls, market):
        """
        Merchant sayfası için tüm verileri döndürür.

        Dönen veriler: 
        - Tüm aktif ürünler (stoku sıfır olsa bile)
        - Ürünlerin reyon bilgileri ve fiyatları
        - Ürünlerin tüm şubelerdeki toplam stok miktarı
        - Ürünlerin tek tek hangi şubede ne kadar stoka sahip olduğu
        """
        
        # 1. AŞAMA: İlgili marketin tüm aktif ürünlerini reyoniyle birlikte çek.
        # Products modeli Models.py içinde olduğu için doğrudan import edebiliyoruz.
        
        products = Products.objects.filter(
            market=market,
            is_active=True
        ).select_related('aisles')

        # Ürün ID'lerini anahtar (key) olarak kullanacağımız ana iskeleti oluşturuyoruz.
        # Stoku olmayan ürünler de raporda sıfır olarak çıksın diye yapıyı baştan kuruyoruz.
        products_dict = {}
        for product in products:
            products_dict[product.id] = {
                "product_id": product.id,
                "product_title": product.title,
                "price": float(product.price),
                "image_url": product.images.url,
                "aisle_name": product.aisles.title,
                "total_stock": 0,
                "branch_stocks": {} # Örnek: { "Merkez Şube": 15, "Atakum Şube": 10 }
            }

        # 2. AŞAMA: İlgili markete bağlı tüm şubelerdeki stok kayıtlarını çek.
        stocks = cls.objects.filter(
            branch__market=market,
            product__is_active=True
        ).select_related('branch')

        # 3. AŞAMA: Python üzerinde eşleştirme (Custom veri manipülasyonu)
        # Karmaşık SQL fonksiyonlarına güvenmek yerine veriyi kendi mantığımızla işliyoruz.
        for stock_obj in stocks:
            p_id = stock_obj.product_id
            
            # Ürün önceden çektiğimiz aktif ürünler sözlüğündeyse verilerini güncelle
            if p_id in products_dict:
                # 3.1. Genel market stok toplamına ekle
                products_dict[p_id]["total_stock"] += stock_obj.stock
                
                # 3.2. Şube bazlı stoku kaydet / güncelle
                branch_name = stock_obj.branch.name
                
                # Eğer aynı şube/ürün kombinasyonu birden çok kez girilmişse hata yapmamak için toplayarak gidiyoruz
                if branch_name in products_dict[p_id]["branch_stocks"]:
                    products_dict[p_id]["branch_stocks"][branch_name] += stock_obj.stock
                else:
                    products_dict[p_id]["branch_stocks"][branch_name] = stock_obj.stock

        # Sadece değerleri döndürerek liste (array of objects) formatını yakalıyoruz
        return list(products_dict.values())

    @classmethod
    def get_product_stocks_by_branch(cls, product):
        """
        Bir ürünün tüm şubelerdeki stok dağılımını döndürür.

        Products to All Branches !!!! Branch

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
                "branch_name": stock.branch.name,
                "stock_count": stock.stock
            }
            for stock in cls.objects.filter(product=product).select_related("branch")
        }

class PackageItem(models.Model):
    pass    

class Package(models.Model):
    PACKAGE_STATUS = [
        ('pending', 'Onay Bekliyor'),
        ('preparing', 'Hazırlanıyor'),
        ('ready', 'Paket Hazır / Kurye Bekliyor'),
        ('on_the_way', 'Kurye Dağıtımda'),
        ('delivered', 'Teslim Edildi'),
        ('canceled', 'İptal Edildi'),
    ]

    PAYMENT_METHODS = [
        ('cash_on_delivery', 'Kapıda Nakit'),
        ('card_on_delivery', 'Kapıda Kredi Kartı'),
        ('online_credit_card', 'Online Kredi Kartı'),
    ]

    # 1. TAKİP VE OPERASYONEL BAĞLANTILAR
    tracking_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Takip Numarası")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='packages', verbose_name="Müşteri")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='packages', verbose_name="Çıkış Şubesi")
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True, related_name='packages', verbose_name="Kurye")

    # 2. PAKET DETAYLARI VE ADRES
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='online_credit_card', verbose_name="Ödeme Yöntemi")
    status = models.CharField(max_length=15, choices=PACKAGE_STATUS, default='pending', verbose_name="Paket Durumu")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Paket Tutarı")
    
    # 2. MÜŞTERI BİLGİLERİ (SNAPSHOT)
    customer_name_snapshot = models.CharField(max_length=255, blank=True, verbose_name="Müşteri Adı Soyadı (Snapshot)")
    customer_phone_snapshot = models.CharField(max_length=20, blank=True, verbose_name="Müşteri Telefonu (Snapshot)")

    address_reference = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kayıtlı Adres Referansı")
    delivery_address = models.TextField(verbose_name="Teslimat Adresi (Snapshot)")

    package_index = models.JSONField(default=list, blank=True, verbose_name="Paketin İçeriği")
    
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
        return f"Paket #{self.id} ({self.tracking_number.hex[:8]}) - {self.customer_name_snapshot}" 

    # ==========================================================================
    # OTOMATİZASYON VE HELPER METOTLAR
    # ==========================================================================

    def save(self, *args, **kwargs):
        """ Paket durumuna göre yola çıkış ve teslim tarihlerini otomatik atar. """
        if not self.pk and self.user:                                          
            if not self.customer_name_snapshot:
                self.customer_name_snapshot = self.user.get_full_name() or self.user.username
            if not self.customer_phone_snapshot and hasattr(self.user, 'phone'):
                self.customer_phone_snapshot = self.user.phone

        if self.status == 'on_the_way' and not self.shipped_at:
            self.shipped_at = timezone.now()
        
        if self.status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
            
        super().save(*args, **kwargs)

    def assign_courier(self, courier_instance):
        """ 
        Pakete kurye atar ve kuryenin durumunu günceller.
        """
        self.courier = courier_instance
        self.status = 'on_the_way'
        self.save(update_fields=['courier', 'status'])

        if courier_instance.status != 'delivery':
            courier_instance.status = 'delivery'
            courier_instance.save(update_fields=['status'])

    def calculate_total_from_json(self):
        """ JSONField içindeki ürün fiyatlarını ve adetlerini çarparak toplam tutarı döner. """
        from decimal import Decimal
        total = Decimal('0.00')
        if isinstance(self.package_index, list):
            for item in self.package_index:
                price = Decimal(str(item.get('price_per_item', 0)))
                qty = int(item.get('quantity', 0))
                total += price * qty
        return total