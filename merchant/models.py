from django.db import models
from markets.models import Market
from account.models import User
from django.contrib.gis.db import models as location_models
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

# Create your models here.

class Branch(models.Model):
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100, verbose_name="Şube Adı")
    address = models.TextField(blank=True)
    location = location_models.PointField(srid=4326, null=True, geography=True, blank=True)

    
    def find_nearest_branch(self, latitude, longitude):
        customer_location = Point(longitude, latitude, srid=4326)

        nearest = Branch.objects.filter(market=self.market).annotate(mesafe=Distance('location', customer_location)).order_by('mesafe').first()

        return nearest