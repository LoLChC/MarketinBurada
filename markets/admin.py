from django import forms
from django.contrib import admin
from .models import Market, MarketBusinessHour

class MarketBusinessHourForm(forms.ModelForm):
    class Meta:
        model = MarketBusinessHour
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Gün seçebileceğimiz o açılır kutuyu (Select) tamamen devre dışı (disabled) bırakıyoruz.
        # Böylece kullanıcı günün adını görür ama tıklayıp değiştiremez, kilitli bir text gibi davranır.
        self.fields['day'].disabled = True
        self.fields['day'].required = False


class MarketBusinessHourInline(admin.TabularInline):
    model = MarketBusinessHour
    form = MarketBusinessHourForm
    
    # Yeni satır ekleme ve silme butonlarını tamamen kapatıyoruz kanka
    extra = 7
    min_num = 7
    max_num = 7
    can_delete = False

    # Formda doğrudan orijinal 'day' alanını ve saatleri gösteriyoruz
    fields = ('day', 'open_time', 'close_time', 'is_closed')
    
    def get_formset(self, request, obj=None, **kwargs):
        """
        Market ilk kez eklenirken veya saatleri yoksa, 
        Haftanın 7 gününü (0'dan 6'ya) form satırlarına tıkır tıkır önceden tanımlar.
        """
        formset = super().get_formset(request, obj, **kwargs)
        old_init = formset.__init__
        
        def new_init(self, *args, **kwargs):
            old_init(self, *args, **kwargs)
            # Eğer bu markete ait çalışma saati kaydı henüz yoksa (yeni marketse)
            if not obj or not obj.hours.exists():
                for i, form in enumerate(self.forms):
                    if i < 7:
                        form.initial['day'] = i
                        
        formset.__init__ = new_init
        return formset


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_price', 'status', 'slug')
    list_display_links = ('name',)
    list_filter = ['status']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MarketBusinessHourInline]