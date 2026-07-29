from django.db import models
from markets.models import Market
from django.contrib.gis.db import models as location_models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from account.models import User, Address
from django.db.models import Q, Sum
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta, date
import calendar
import uuid

# Create your models here.

class Branch(models.Model):
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

        if nearest_branch and hasattr(nearest_branch, 'mesafe'):
            if nearest_branch.mesafe.km <= nearest_branch.delivery_radius_km:
                return nearest_branch

        return None

    def get_day_turnover(self, date):
        turnover = self.packages.filter(status='delivered', delivered_at__date=date).aggregate(total_turnover=Sum('total_amount'))['total_turnover']

        return turnover or 0.00
    
    def get_weekly_turnover(self, target_date):
        start_of_week = target_date - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        turnover = self.packages.filter(status='delivered',delivered_at__date__range=(start_of_week, end_of_week)).aggregate(total_turnover=Sum('total_amount'))['total_turnover']

        return turnover or 0.00
    
    def get_monthly_turnover(self, year, month):
        _, last_day = calendar.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)
        turnover = self.packages.filter(status='delivered', delivered_at__date__range=(start_date, end_date)).aggregate(total_turnover=Sum('total_amount'))['total_turnover']

        return turnover or 0.00
    
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

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='couriers', verbose_name="Bağlı Olduğu Şube")
    name = models.CharField(max_length=50, verbose_name="Adı")
    surname = models.CharField(max_length=50, verbose_name="Soyadı")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon Numarası")
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES, default='motorcycle', verbose_name="Araç Tipi")
    status = models.CharField(max_length=15, choices=COURIER_STATUS, default='offline', verbose_name="Durumu")
    monthly_delivery_count = models.PositiveIntegerField(default=0, verbose_name="Bu Ayki Teslimat Sayısı")
    current_location = location_models.PointField(srid=4326, null=True, geography=True, blank=True, verbose_name="Anlık Konum")

    @staticmethod # For get_all() and register, separate name
    def get_name(index):
        index = index.strip()
        index_parts = index.split()
        
        if not index_parts:
            return "İsimsiz"
            
        if len(index_parts) == 1:
            return index_parts[0]
            
        return " ".join(index_parts[:-1])

    @staticmethod # For get_all() and register, separate surname
    def get_surname(index):
        index = index.strip()
        index_parts = index.split()
        
        if not index_parts:
            return "-"
            
        if len(index_parts) == 1:
            return "-"
            
        return index_parts[-1]


    def get_completed_packages_last_30_days(self): # For get_all(), last 30 days packages 
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        return self.packages.filter(status='delivered',delivered_at__gte=thirty_days_ago).order_by('-delivered_at')

    def get_active_packages(self): # For get_all(), on_the_way process
        return self.packages.filter(status='on_the_way')

    def package_set_delivery(self, package): # For Views file, delivered process
        if package.courier == self and package.status == 'on_the_way':
            package.status = 'delivered'
            package.delivered_at = timezone.now()
            package.save(update_fields=['status', 'delivered_at'])

            self.monthly_delivery_count += 1
            
            if not self.get_active_packages().exists():
                self.status = 'available'
            
            self.save(update_fields=['monthly_delivery_count', 'status'])

class Aisles(models.Model): #Reyonlar
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='aisles')
    title = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    
    @staticmethod
    def get_all(market):
        market = int(market)
        aisles = Aisles.objects.filter(market=market)
        
        aisles_dict = {}
        for aisle in aisles:
            count = aisle.products.count()
            total = 0
            for product in aisle.products.all():
                total += product.price

            if count == 0:
                average = "No Products"
            else:
                average = total / count

            aisles_dict[aisle.title] = {
                "title" : aisle.title,
                "count" : count,
                "average" : average
            }

        return list(aisles_dict.values())
        

class Products(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='products')
    aisles = models.ForeignKey(Aisles, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=50)
    images = models.ImageField(upload_to='product-images/')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def get_all(market):
        market = int(market)
        products = Products.objects.filter(market=market)
        
        products_dict = {}
        for product in products:

            products_dict[product.title] = {
                "aisles" : product.aisles.title,
                "title" : product.title,
                "images" : str(product.images),
                "price" : product.price,
                "is_active" : product.is_active,
            }

        return list(products_dict.values())


class Stocks(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="stocks")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="stocks")
    ailes = models.ForeignKey(Aisles, on_delete=models.CASCADE, related_name="stocks")
    stock = models.PositiveIntegerField(default=0)

    @staticmethod
    def get_all(market):
        
        # 1. AŞAMA: İlgili marketin tüm aktif ürünlerini reyoniyle birlikte çek.
        # Products modeli Models.py içinde olduğu için doğrudan import edebiliyoruz.
        market = int(market)

        products = Products.objects.filter(market=market, is_active=True).select_related('aisles')

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
        stocks = Stocks.objects.filter(branch__market=market, product__is_active=True).select_related('branch')

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
    tracking_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Takip Numarası")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='packages', verbose_name="Müşteri")
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='packages', verbose_name="Market")
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='packages', verbose_name="Çıkış Şubesi")
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True, related_name='packages', verbose_name="Kurye")
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='online_credit_card', verbose_name="Ödeme Yöntemi")
    status = models.CharField(max_length=15, choices=PACKAGE_STATUS, default='pending', verbose_name="Paket Durumu")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Paket Tutarı")
    customer_name_snapshot = models.CharField(max_length=255, blank=True, verbose_name="Müşteri Adı Soyadı (Snapshot)")
    customer_phone_snapshot = models.CharField(max_length=20, blank=True, verbose_name="Müşteri Telefonu (Snapshot)")
    address_id = models.PositiveIntegerField(verbose_name="Addres id")
    delivery_address = models.TextField(verbose_name="Teslimat Adresi")
    package_index = models.JSONField(default=list, blank=True, verbose_name="Paketin İçeriği")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Paket Oluşturulma Zamanı")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Son Durum Güncellemesi")
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name="Yola Çıkış Zamanı")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Teslim Edilme Zamanı")


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

    def get_address(self):
        address  = Address.objects.filter(id=self.address_id)


    def pending(self):
        package_market = self.market
        user_longitude = self.address.x
        user_latitude = self.address.y

        branch = Branch.find_nearest_branch(package_market, user_latitude, user_longitude)

        self.branch = branch

    def set_on_the_way(self, courier): #For Views file, on_the_way procsess
        self.courier = courier
        self.status = 'on_the_way'
        self.save(update_fields=['courier', 'status'])

        if courier.status != 'delivery':
            courier.status = 'delivery'
            courier.save(update_fields=['status'])

    def set_delivered(self):
        self.status = 'delivered'
        self.save(update_fields=['status'])

    # set_delivery on Courier it is name is package_set_delivery

    def calculate_total_from_json(self):
        """ JSONField içindeki ürün fiyatlarını ve adetlerini çarparak toplam tutarı döner. """
        
        total = Decimal('0.00')
        if isinstance(self.package_index, list):
            for item in self.package_index:
                price = Decimal(str(item.get('price_per_item', 0)))
                qty = int(item.get('quantity', 0))
                total += price * qty
        return total
    
class Campaign(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='Campaign')
    title = models.CharField(max_length=50)
    code = models.CharField(max_length=50)
    discount_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="İndirim Oranı (%)")
    start_time = models.DateTimeField(auto_now_add=True, verbose_name="Kampanya Başlangıç Tarihi")
    end_time = models.DateTimeField(auto_now_add=True, verbose_name="Kampanya Bitiş Tarihi")
    use_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    @staticmethod
    def get_all(market):
        market = int(market)

        campaigns = Campaign.objects.filter(market=market)

        campaigns_dict = {}
        for campaign in campaigns:

            campaigns_dict[campaign.title] = {
                "title" : campaign.title,
                "code" : campaign.code,
                "discount_ratio" : campaign.discount_ratio,
                "start_time" : str(campaign.start_time),
                "end_time" : str(campaign.end_time),
                "use_count" : campaign.use_count,
                "is_active" : campaign.is_active,
            }

        return list(campaigns_dict.values())