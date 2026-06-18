import os
import shutil
from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Projedeki tüm uygulamaların migration dosyalarını temizler (__init__.py hariç)"

    def handle(self, *args, **options):
        # Django projesine kayıtlı tüm uygulamaları (apps) çekiyoruz
        project_apps = apps.get_app_configs()
        
        deleted_count = 0

        for app in project_apps:
            # Django'nun kendi built-in veya pip ile kurduğun dış paketlerin
            # migration'larını silmemek için "site-packages" içeren yolları eliyoruz.
            if "site-packages" in app.path:
                continue
                
            migrations_dir = os.path.join(app.path, 'migrations')
            
            # Eğer app içinde migrations klasörü varsa işleme başla
            if os.path.exists(migrations_dir):
                for filename in os.listdir(migrations_dir):
                    # __init__.py dosyasına dokunmuyoruz, klasör yapısının bozulmaması için şart
                    if filename == '__init__.py':
                        continue
                        
                    file_path = os.path.join(migrations_dir, filename)
                    
                    try:
                        # Dosya veya sembolik link ise sil
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                            deleted_count += 1
                        # __pycache__ gibi bir klasörse içindekilerle birlikte sil
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                            deleted_count += 1
                    except Exception as e:
                        self.stderr.write(f"Hata oluştu ({file_path}): {e}")

        if deleted_count > 0:
            self.stdout.write(self.style.SUCCESS(f"Başarılı! Toplam {deleted_count} migration dosyası/klasörü uçuruldu."))
        else:
            self.stdout.write(self.style.WARNING("Temizlenecek herhangi bir migration dosyası bulunamadı."))