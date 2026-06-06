from dotenv import load_dotenv
from django.core.mail import send_mail
from MarketinBurada import settings
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

load_dotenv()

def send_mail_text(subject, message, to_email):
    if isinstance(to_email, str):
        to_email = [to_email]
        
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER, # settings.py'dan otomatik alır
        recipient_list=to_email,
        fail_silently=False, # Hata alırsanız detayını görmek için False kalsın
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