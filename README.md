Pardus Server 23.4 ve Pardus ETAP arasında NFS (Network File System) kullanmak, Linux dünyasının kendi doğal protokolü olduğu için Samba'dan (SMB) çok daha hızlı, kararlı ve sorunsuzdur. Ayrıca kullanıcı adı ve şifre karmaşası yoktur; yetkilendirme IP tabanlı yapılır.

Bu işlem iki aşamadan oluşur:

#### Sunucu Tarafı: Pardus Server'da klasörün paylaşıma açılması.

İstemci Tarafı: Hazırladığımız uygulamanın NFS protokolüne göre sadeleştirilmesi.

İşte tam rehber ve yeni kodlar.

A. Sunucu Tarafı Ayarları (Pardus Server 23.4)

Uygulamanın çalışması için önce sunucuda klasörü NFS olarak "dışarı aktarmanız" (export) gerekir.

NFS Servisini Kurun:

Bash

sudo apt update

sudo apt install nfs-kernel-server

Klasörü Oluşturun ve İzin Verin: (Örneğin /home/nfs_paylasim olsun)

Bash

sudo mkdir -p /srv/nfs/duvar

sudo chown nobody:nogroup /srv/nfs/duvar

sudo chmod 777 /srv/nfs/duvar

(Not: chmod 777 verdik ki öğretmen uygulamasından rahatça resim yükleyebilsin.)

Paylaşım Ayarını Yapın (/etc/exports):

Bash

sudo nano /etc/exports

Dosyanın en altına şu satırı ekleyin (Okuldaki tahta IP bloğuna göre düzenleyin, örneğin 192.168.1.0/24):

Plaintext

/srv/nfs/duvar 192.168.1.0/24(rw,sync,no_subtree_check,no_root_squash)

Servisi Başlatın:

Bash

sudo exportfs -a

sudo systemctl restart nfs-kernel-server


#### B. İstemci (Tahta) Tarafı: Yeni Uygulama Kodu
Artık tahtalarda çalışacak uygulamayı NFS'e göre uyarlayabiliriz.

Ön Gereksinim: Tahtalarda nfs-common paketi yüklü olmalıdır.

Bash

sudo apt update

sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 dconf-cli nfs-common  -y

### Çalıştırma:

sudo chmod +x etap_duvar_nfs.py

sudo python3 etap_duvar_nfs.py

<img width="505" height="654" alt="Ekran Görüntüsü - 2025-12-14 19-39-46" src="https://github.com/user-attachments/assets/c864ca89-2631-4049-89d9-65e09859ed6f" />
