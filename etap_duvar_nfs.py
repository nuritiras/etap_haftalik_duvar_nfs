#!/usr/bin/env python3
import gi
import os
import subprocess
import sys
import shutil
import json

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf

# Ayar dosyası
CONFIG_FILE = os.path.expanduser("~/.etap_nfs_config.json")

class NFSWallpaperManager(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="ETAP NFS Yönetici (Pardus Server)")
        self.set_border_width(15)
        self.set_default_size(500, 550)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        # Ana Kutu
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)

        # --- BÖLÜM 1: NFS Sunucu Ayarları ---
        frame_server = Gtk.Frame(label=" 1. NFS Sunucu Ayarları ")
        main_box.pack_start(frame_server, False, False, 0)
        
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)
        frame_server.add(grid)

        # Giriş Alanları (Sadeleştirildi)
        self.entry_ip = Gtk.Entry(placeholder_text="192.168.1.xxx")
        self.entry_path = Gtk.Entry(placeholder_text="Örn: /srv/nfs/duvar")
        
        # Etiketler
        grid.attach(Gtk.Label(label="Sunucu IP Adresi:", xalign=1), 0, 0, 1, 1)
        grid.attach(self.entry_ip, 1, 0, 1, 1)
        
        grid.attach(Gtk.Label(label="Uzak Klasör Yolu:", xalign=1), 0, 1, 1, 1)
        grid.attach(self.entry_path, 1, 1, 1, 1)
        
        # Bilgi Notu
        lbl_note = Gtk.Label(label="<small>Not: NFS'de kullanıcı adı/şifre gerekmez.\nSunucuda IP izni olduğundan emin olun.</small>")
        lbl_note.set_use_markup(True)
        grid.attach(lbl_note, 1, 2, 1, 1)

        # Yapılandır Butonu
        btn_config = Gtk.Button(label="Sistemi Yapılandır (Servis & Kilit)")
        btn_config.connect("clicked", self.on_config_clicked)
        grid.attach(btn_config, 1, 3, 1, 1)

        # --- BÖLÜM 2: Resim İşlemleri ---
        frame_img = Gtk.Frame(label=" 2. Resim Yükle & Yayınla ")
        main_box.pack_start(frame_img, True, True, 0)

        vbox_img = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox_img.set_margin_top(10)
        vbox_img.set_margin_bottom(10)
        vbox_img.set_margin_start(10)
        vbox_img.set_margin_end(10)
        frame_img.add(vbox_img)

        self.file_chooser = Gtk.FileChooserButton(title="Resim Seçiniz")
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Resim Dosyaları")
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/png")
        self.file_chooser.add_filter(filter_img)
        self.file_chooser.connect("file-set", self.on_file_selected)
        vbox_img.pack_start(self.file_chooser, False, False, 0)

        self.img_preview = Gtk.Image()
        self.img_preview.set_from_icon_name("image-x-generic", Gtk.IconSize.DIALOG)
        self.img_preview.set_pixel_size(150)
        vbox_img.pack_start(self.img_preview, True, True, 0)

        btn_upload = Gtk.Button(label="SEÇİLEN RESMİ YAYINLA")
        btn_upload.get_style_context().add_class("suggested-action")
        btn_upload.set_size_request(-1, 40)
        btn_upload.connect("clicked", self.on_upload_clicked)
        main_box.pack_start(btn_upload, False, False, 0)

        # --- BÖLÜM 3: Sıfırlama ---
        btn_reset = Gtk.Button(label="SİSTEMİ SIFIRLA (Kaldır)")
        btn_reset.get_style_context().add_class("destructive-action")
        btn_reset.connect("clicked", self.on_uninstall_clicked)
        main_box.pack_start(btn_reset, False, False, 5)

        self.lbl_status = Gtk.Label(label="Hazır. (nfs-common paketini kurmayı unutmayın)")
        main_box.pack_end(self.lbl_status, False, False, 0)

        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.entry_ip.set_text(data.get("ip", ""))
                    self.entry_path.set_text(data.get("path", ""))
            except:
                pass

    def save_config(self):
        data = {
            "ip": self.entry_ip.get_text().strip(),
            "path": self.entry_path.get_text().strip()
        }
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass

    def on_file_selected(self, widget):
        filename = widget.get_filename()
        if filename:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    filename, width=400, height=200, preserve_aspect_ratio=True
                )
                self.img_preview.set_from_pixbuf(pixbuf)
            except:
                pass

    def run_cmd(self, cmd):
        try:
            subprocess.run(cmd, shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Hata: {e}")
            return False

    def get_nfs_string(self):
        ip = self.entry_ip.get_text().strip()
        path = self.entry_path.get_text().strip()
        if not ip or not path: return None
        # NFS Formatı: 192.168.1.10:/srv/nfs/share
        return f"{ip}:{path}"

    def ensure_mount(self):
        if not os.path.exists("/media/nfs_resim"):
            os.makedirs("/media/nfs_resim")
        
        if os.path.ismount("/media/nfs_resim"):
            return True
        
        source = self.get_nfs_string()
        if not source:
            self.lbl_status.set_text("Hata: IP veya Yol eksik.")
            return False
            
        # NFS Mount Komutu
        cmd = f"mount -t nfs {source} /media/nfs_resim"
        if self.run_cmd(cmd):
            return True
        else:
            self.lbl_status.set_text("Mount Hatası! (Sunucuda /etc/exports ayarlı mı?)")
            return False

    def on_config_clicked(self, widget):
        self.save_config()
        source = self.get_nfs_string()
        ip_addr = self.entry_ip.get_text().strip()

        if not source:
            self.lbl_status.set_text("Eksik bilgi!")
            return
        
        if shutil.which("dconf") is None:
            self.lbl_status.set_text("Hata: dconf-cli yüklü değil.")
            return

        self.lbl_status.set_text("Yapılandırılıyor...")
        self.run_cmd("mkdir -p /media/nfs_resim")

        # NFS için Bash Script
        script_content = f"""#!/bin/bash
LOG="/var/log/etap_nfs.log"
echo "$(date) - NFS Servisi basladi." > $LOG
TARGET="{ip_addr}"
MAX_RETRIES=30
COUNT=0

# Ping Kontrolü
while ! ping -c 1 -W 1 $TARGET &> /dev/null; do
    echo "Bekleniyor... ($COUNT)" >> $LOG
    sleep 2
    ((COUNT++))
    if [ $COUNT -ge $MAX_RETRIES ]; then
        echo "Sunucuya ulasilamadi." >> $LOG
        exit 1
    fi
done

# Mount
umount /media/nfs_resim 2>/dev/null
mount -t nfs {source} /media/nfs_resim >> $LOG 2>&1

# Kopyala
if [ -f "/media/nfs_resim/guncel_duvar.jpg" ]; then
    cp "/media/nfs_resim/guncel_duvar.jpg" "/usr/share/backgrounds/kurumsal_arkaplan.jpg"
    chmod 644 "/usr/share/backgrounds/kurumsal_arkaplan.jpg"
    echo "Guncellendi." >> $LOG
fi
"""
        with open("/usr/local/bin/duvarkagidi_guncelle.sh", "w") as f:
            f.write(script_content)
        self.run_cmd("chmod +x /usr/local/bin/duvarkagidi_guncelle.sh")
        
        os.system('echo "@reboot /usr/local/bin/duvarkagidi_guncelle.sh" | crontab -')

        # Dconf Kilitleri (Aynı kalır)
        os.makedirs("/etc/dconf/profile", exist_ok=True)
        with open("/etc/dconf/profile/user", "w") as f:
            f.write("user-db:user\nsystem-db:local\n")
        
        os.makedirs("/etc/dconf/db/local.d/locks", exist_ok=True)
        with open("/etc/dconf/db/local.d/00-wallpaper", "w") as f:
            f.write("[org/cinnamon/desktop/background]\npicture-uri='file:///usr/share/backgrounds/kurumsal_arkaplan.jpg'\npicture-options='zoom'\n[org/gnome/desktop/background]\npicture-uri='file:///usr/share/backgrounds/kurumsal_arkaplan.jpg'\npicture-options='zoom'\n")
        with open("/etc/dconf/db/local.d/locks/wallpaper", "w") as f:
            f.write("/org/cinnamon/desktop/background/picture-uri\n/org/cinnamon/desktop/background/picture-options\n")

        if self.run_cmd("dconf update"):
            self.lbl_status.set_text("NFS Yapılandırması Tamam!")
        else:
            self.lbl_status.set_text("Hata: dconf sorunu.")

    def on_upload_clicked(self, widget):
        self.save_config()
        local_file = self.file_chooser.get_filename()
        if not local_file: return
        
        self.lbl_status.set_text("Yükleniyor...")
        if not self.ensure_mount(): return
        
        try:
            shutil.copy2(local_file, "/media/nfs_resim/guncel_duvar.jpg")
            shutil.copy2(local_file, "/usr/share/backgrounds/kurumsal_arkaplan.jpg")
            self.lbl_status.set_text("Resim NFS sunucuya yüklendi.")
        except Exception as e:
            self.lbl_status.set_text(f"Yazma Hatası: Sunucu izinlerini (rw) kontrol edin.")

    def on_uninstall_clicked(self, widget):
        if self.run_cmd("crontab -r"):
            files = ["/usr/local/bin/duvarkagidi_guncelle.sh", "/etc/dconf/profile/user", 
                     "/etc/dconf/db/local.d/00-wallpaper", "/etc/dconf/db/local.d/locks/wallpaper"]
            for f in files:
                if os.path.exists(f): os.remove(f)
            self.run_cmd("umount /media/nfs_resim || true")
            self.run_cmd("dconf update")
            self.lbl_status.set_text("Sistem temizlendi.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Sudo ile çalıştırın.")
        sys.exit(1)
    win = NFSWallpaperManager()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
