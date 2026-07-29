from dotenv import load_dotenv
from django.core.mail import send_mail
from MarketinBurada import settings
from django.core.mail import EmailMultiAlternatives
from markets.models import Market
from django.core.cache import cache
from . import tokens
from django.shortcuts import redirect
from django.utils import timezone
from datetime import timedelta

load_dotenv()

def login(request, user, go, duration_days=None):
    response = redirect(go)
    token = tokens.generate_login_token(user)

    if duration_days:
        times = timezone.now() + timedelta(days=duration_days)
        response.set_cookie(
            "login_token",
            token,
            httponly=True,
            expires=times
        )
    else:
        response.set_cookie(
            "login_token",
            token,
            httponly=True
        )
    request.session.flush()
    request.session.cycle_key()
 
    return response

def logout(request):
    user_id = request.user_obj.id
    response = redirect("account:login")
    response.delete_cookie("login_token")
    cache.delete(f"user-{user_id}")
    return response

def login_token_to_user_id(request):
    token = request.COOKIES.get('login_token')
    if token:
        decoded_token = tokens.decode_login_token(token)
        user_id = decoded_token.get("user-id")
        return user_id
    else:
        return None
    

def send_mail_text(subject, message, to_email):
    if isinstance(to_email, str):
        to_email = [to_email]
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER, 
        recipient_list=to_email,
        fail_silently=False,
    )

def send_mail_html(subject, message, to_email):
    if isinstance(to_email, str):
        to_email = [to_email]

    email = EmailMultiAlternatives(
        subject=subject,
        body=message,
        from_email=settings.EMAIL_HOST_USER,
        to=to_email
    )

    email.attach_alternative(message, "text/html")
    email.send()

def home_market_cache():
    key = "home-markets"

    market = cache.get(key)
    if market is not None:
        return market

    market = Market.objects.filter(status=True, home=True)
    cache.set(key, market, timeout=60 * 60 * 24 * 7)  # 1 hafta
    
    return market

def auth_state(request):
    return {
        "auth_state": bool(login_token_to_user_id(request))
    }

def write_header(response, header_name, header_value):
    """
    İstemciye (client) dönecek olan response objesine yeni header ekler veya
    var olan bir header'ı ezer.
    """
    # 1. HTTP protokolünde header değerleri her zaman metin (string) olmak zorundadır.
    # Ne gelirse gelsin güvenliğe ve protokole uyması için string'e çeviriyoruz.
    safe_value = str(header_value)
    
    # 2. Response objesi arka planda bir sözlük (dictionary) gibi davranır.
    # Anahtar-değer (key-value) mantığıyla header'ı doğrudan response içine yazıyoruz.
    response[header_name] = safe_value
    
    # 3. İşlemi bitmiş response objesini geri döndürüyoruz.
    return response

def read_header(request, header_name, default_value=None):
    """
    WSGI standartlarına uygun olarak gelen request üzerinden header okur.
    Framework'ün sunduğu soyutlama katmanlarını atlayarak doğrudan sunucu 
    ortam değişkenlerine (META) bakar.
    """
    # 1. Header adını WSGI formatına dönüştürüyoruz
    # Örnek: 'X-Api-Key' -> 'X_API_KEY'
    formatted_name = header_name.replace('-', '_').upper()
    
    # 2. Standart HTTP header'ları WSGI'da 'HTTP_' ön eki alır.
    # Örnek: 'X_API_KEY' -> 'HTTP_X_API_KEY'
    meta_key = f"HTTP_{formatted_name}"
    
    # 3. Content-Type ve Content-Length standart dışıdır, 'HTTP_' ön eki almazlar.
    # Bu iki istisnayı manuel olarak yakalıyoruz.
    if formatted_name in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
        meta_key = formatted_name

    # 4. Doğrudan ortam değişkenleri (META) sözlüğünden veriyi çekiyoruz. 
    # Bulamazsa varsayılan değeri (default_value) döndürüyoruz.
    return request.META.get(meta_key, default_value)

def delete_header(response, header_name):
    """
    İstemciye (client) dönecek olan response objesinden belirtilen header'ı siler.
    """
    # 1. response.has_header() ile bu başlığın gerçekten var olup olmadığını kontrol ediyoruz.
    # Bu kontrolü yapmazsak ve olmayan bir şeyi silmeye çalışırsak Python 'KeyError' hatası fırlatır.
    if response.has_header(header_name):
        
        # 2. Sözlük (dictionary) mantığı ile 'del' komutunu kullanarak header'ı siliyoruz.
        del response[header_name]
        
    # 3. İşlemi bitmiş veya zaten o başlığa sahip olmayan response objesini geri döndürüyoruz.
    return response

def delete_all_headers(response, hayati_olanlari_koru=True):
    """
    Response üzerindeki tüm header'ları siler.
    hayati_olanlari_koru=True (varsayılan) olarak ayarlandığında, 
    sistemin çökmemesi için Content-Type gibi zorunlu HTTP başlıklarını silmez.
    """
    # 1. Sözlük (dictionary) boyutunu değiştirirken hata almamak için 
    # mevcut header isimlerini önce bağımsız bir listeye alıyoruz.
    mevcut_headerlar = [header_name for header_name, deger in response.items()]
    
    # 2. HTTP protokolünün ayakta kalması için kesinlikle gereken başlıklar
    korunacak_headerlar = ['Content-Type', 'Content-Length']
    
    # 3. Listelediğimiz tüm header'ları tek tek dönüyoruz
    for header in mevcut_headerlar:
        
        # Eğer koruma aktifse ve bu header hayati listesindeyse silmeden atla
        if hayati_olanlari_koru and header in korunacak_headerlar:
            continue
            
        # Header'ı bellekten tamamen sil
        if response.has_header(header):
            del response[header]
            
    return response