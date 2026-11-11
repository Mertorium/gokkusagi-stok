import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class StokUygulamasi(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gökkuşağı Temizlik ve Ambalaj - Stok & Finans")
        self.geometry("1400x850")
        
        self.dosya_adi = "stok_veri.json"
        self.veri = self.verileri_yukle()
        self.sepet = []
        
        self.setup_ui()

    def verileri_yukle(self):
        if os.path.exists(self.dosya_adi):
            try:
                with open(self.dosya_adi, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    if not isinstance(d.get("u"), dict): d["u"] = {}
                    if not isinstance(d.get("s"), list): d["s"] = []
                    if not isinstance(d.get("t"), list): d["t"] = []
                    if not isinstance(d.get("g"), list): d["g"] = []
                    if not isinstance(d.get("ml"), list): d["ml"] = []
                    return d
            except:
                pass
        return {"u": {}, "s": [], "t": [], "g": [], "ml": []}

    def verileri_kaydet(self):
        with open(self.dosya_adi, "w", encoding="utf-8") as f:
            json.dump(self.veri, f, ensure_ascii=False, indent=4)

    def setup_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab1 = self.tabview.add("1. Sepet & Satış Yap")
        self.tab2 = self.tabview.add("2. Veresiye")
        self.tab3 = self.tabview.add("3. Cari")
        self.tab4 = self.tabview.add("4. Kasa")
        self.tab5 = self.tabview.add("5. Stok Listesi")
        self.tab6 = self.tabview.add("6. Kritik Stok")
        self.tab7 = self.tabview.add("7. Raporlar")
        
        self.setup_sepet_tab()
        self.setup_veresiye_tab()
        self.setup_cari_tab()
        self.setup_kasa_tab()
        self.setup_stok_tab()
        self.setup_kritik_tab()
        self.setup_rapor_tab()

    def setup_sepet_tab(self):
        sol_frame = ctk.CTkFrame(self.tab1)
        sol_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        sağ_frame = ctk.CTkFrame(self.tab1)
        sağ_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        giriş_frame = ctk.CTkFrame(sol_frame)
        giriş_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(giriş_frame, text="Tarih:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.tarih_entry = ctk.CTkEntry(giriş_frame, width=120)
        self.tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.tarih_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkButton(giriş_frame, text="Bugün", width=60, command=lambda: (self.tarih_entry.delete(0, tk.END), self.tarih_entry.insert(0, datetime.now().strftime("%d.%m.%Y")))).grid(row=0, column=2, padx=5, pady=5)
        
        ctk.CTkLabel(giriş_frame, text="Müşteri / Firma:").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.musteri_combo = ttk.Combobox(giriş_frame, values=["GENEL MÜŞTERİ"] + self.veri["ml"])
        self.musteri_combo.set("GENEL MÜŞTERİ")
        self.musteri_combo.grid(row=0, column=4, padx=5, pady=5)
        
        odeme_frame = ctk.CTkFrame(giriş_frame)
        odeme_frame.grid(row=1, column=0, columnspan=5, pady=5, sticky="ew")
        self.odeme_var = tk.StringVar(value="Nakit")
        ctk.CTkRadioButton(odeme_frame, text="Nakit", variable=self.odeme_var, value="Nakit").pack(side="left", padx=10)
        ctk.CTkRadioButton(odeme_frame, text="Kredi Kartı", variable=self.odeme_var, value="Kredi Kartı").pack(side="left", padx=10)
        ctk.CTkRadioButton(odeme_frame, text="Veresiye", variable=self.odeme_var, value="Veresiye").pack(side="left", padx=10)
        
        ctk.CTkLabel(giriş_frame, text="Ürün Seçin:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        aktif_urunler = [u for u, b in self.veri["u"].items() if b.get("adet", 0) > 0]
        self.urun_combo = ttk.Combobox(giriş_frame, values=aktif_urunler)
        self.urun_combo.grid(row=2, column=1, padx=5, pady=5)
        self.urun_combo.bind("<<ComboboxSelected>>", self.urun_secildi)
        
        ctk.CTkLabel(giriş_frame, text="Adet:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.adet_entry = ctk.CTkEntry(giriş_frame, width=80)
        self.adet_entry.insert(0, "1")
        self.adet_entry.grid(row=2, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(giriş_frame, text="Birim Fiyatı (TL):").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.fiyat_entry = ctk.CTkEntry(giriş_frame, width=100)
        self.fiyat_entry.grid(row=3, column=1, padx=5, pady=5)
        
        ctk.CTkButton(giriş_frame, text="➕ Sepete Ekle", fg_color="#1f538d", command=self.sepete_ekle).grid(row=4, column=0, columnspan=5, pady=10, sticky="ew")
        ctk.CTkButton(giriş_frame, text="🛒 Sepeti Satışa Dönüştür (Tamamla)", fg_color="#2b9348", command=self.sepeti_tamamla).grid(row=5, column=0, columnspan=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(sol_frame, text="Aktif Sepet Listesi", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        self.sepet_agac = ttk.Treeview(sol_frame, columns=("Ürün", "Adet", "Birim Fiyat", "Toplam Tutar"), show="headings")
        self.sepet_agac.heading("Ürün", text="Ürün")
        self.sepet_agac.heading("Adet", text="Adet")
        self.sepet_agac.heading("Birim Fiyat", text="Birim Fiyat")
        self.sepet_agac.heading("Toplam Tutar", text="Toplam Tutar")
        self.sepet_agac.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(sol_frame, text="Seçilen Ürünü Sepetten Çıkar", fg_color="#d90429", command=self.sepetten_cikar).pack(anchor="w", padx=5, pady=5)
        self.sepet_toplam_label = ctk.CTkLabel(sol_frame, text="SEPET GENEL TOPLAM: 0.00 TL", font=("Arial", 14, "bold"))
        self.sepet_toplam_label.pack(anchor="e", padx=5, pady=10)
        
        ctk.CTkLabel(sağ_frame, text="Son Satış İşlemleri", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=5)
        self.satis_agac = ttk.Treeview(sağ_frame, columns=("No", "Tarih", "Ürün", "Adet", "Tutar", "Kâr", "Ödeme", "Müşteri"), show="headings")
        for col in ("No", "Tarih", "Ürün", "Adet", "Tutar", "Kâr", "Ödeme", "Müşteri"):
            self.satis_agac.heading(col, text=col)
            self.satis_agac.column(col, width=80)
        self.satis_agac.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(sağ_frame, text="Seçili Satışı Sil (İade Et)", fg_color="#d90429", command=self.satis_sil).pack(anchor="e", padx=5, pady=5)
        self.satisları_guncelle()

    def urun_secildi(self, event):
        urun = self.urun_combo.get()
        if urun in self.veri["u"]:
            maliyet = self.veri["u"][urun].get("maliyet", 0)
            varsayilan_satis = maliyet * 1.2
            self.fiyat_entry.delete(0, tk.END)
            self.fiyat_entry.insert(0, f"{varsayilan_satis:.2f}")

    def sepete_ekle(self):
        urun = self.urun_combo.get()
        adet_str = self.adet_entry.get()
        fiyat_str = self.fiyat_entry.get()
        
        if not urun or not adet_str or not fiyat_str:
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun.")
            return
            
        try:
            adet = int(adet_str)
            fiyat = float(fiyat_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz sayısal değer.")
            return
            
        if adet <= 0 or fiyat < 0:
            messagebox.showerror("Hata", "Adet ve fiyat sıfırdan büyük olmalıdır.")
            return

        if urun not in self.veri["u"]:
            messagebox.showerror("Hata", "Böyle bir ürün bulunamadı.")
            return

        stok = self.veri["u"][urun]["adet"]
        toplam_sepette_adet = sum(item["adet"] for item in self.sepet if item["urun"] == urun)
        if stok < (toplam_sepette_adet + adet):
            messagebox.showerror("Hata", f"Yetersiz stok! Mevcut: {stok}")
            return

        tutar = adet * fiyat
        self.sepet.append({"urun": urun, "adet": adet, "birim": fiyat, "tutar": tutar})
        self.sepet_listesini_guncelle()

    def sepet_listesini_guncelle(self):
        for i in self.sepet_agac.get_children():
            self.sepet_agac.delete(i)
        toplam = 0
        for item in self.sepet:
            self.sepet_agac.insert("", "end", values=(item["urun"], item["adet"], f"{item['birim']:.2f} TL", f"{item['tutar']:.2f} TL"))
            toplam += item["tutar"]
        self.sepet_toplam_label.configure(text=f"SEPET GENEL TOPLAM: {toplam:.2f} TL")

    def sepetten_cikar(self):
        selected_item = self.sepet_agac.selection()
        if not selected_item:
            return
        item_index = self.sepet_agac.index(selected_item[0])
        del self.sepet[item_index]
        self.sepet_listesini_guncelle()

    def sepeti_tamamla(self):
        if not self.sepet:
            messagebox.showwarning("Uyarı", "Sepet boş.")
            return

        tarih = self.tarih_entry.get()
        musteri = self.musteri_combo.get()
        odeme = self.odeme_var.get()

        if odeme == "Veresiye" and musteri == "GENEL MÜŞTERİ":
            messagebox.showerror("Hata", "Veresiye satışlar için geçerli bir müşteri seçmelisiniz.")
            return

        for item in self.sepet:
            urun = item["urun"]
            adet = item["adet"]
            tutar = item["tutar"]
            maliyet = self.veri["u"][urun].get("maliyet", 0) * adet
            kar = tutar - maliyet

            self.veri["u"][urun]["adet"] -= adet
            self.veri["s"].append({
                "no": len(self.veri["s"]) + 1,
                "tarih": tarih,
                "urun": urun,
                "adet": adet,
                "tutar": tutar,
                "kar": kar,
                "odeme": odeme,
                "musteri": musteri
            })

        self.verileri_kaydet()
        self.sepet = []
        self.sepet_listesini_guncelle()
        self.satisları_guncelle()
        
        aktif_urunler = [u for u, b in self.veri["u"].items() if b.get("adet", 0) > 0]
        self.urun_combo['values'] = aktif_urunler
        
        messagebox.showinfo("Başarılı", "Satış tamamlandı!")

    def satisları_guncelle(self):
        for i in self.satis_agac.get_children():
            self.satis_agac.delete(i)
        for s in reversed(self.veri["s"]):
            self.satis_agac.insert("", "end", values=(
                s.get("no", 1), s.get("tarih", ""), s.get("urun", ""), s.get("adet", 0),
                f"{s.get('tutar', 0):.2f} TL", f"{s.get('kar', 0):.2f} TL",
                s.get("odeme", ""), s.get("musteri", "")
            ))

    def satis_sil(self):
        selected_item = self.satis_agac.selection()
        if not selected_item:
            return
        satis_no = self.satis_agac.item(selected_item[0])["values"][0]
        
        for s in self.veri["s"]:
            if s.get("no") == satis_no:
                self.veri["u"][s["urun"]]["adet"] += s["adet"]
                self.veri["s"].remove(s)
                break
                
        self.verileri_kaydet()
        self.satisları_guncelle()
        
        aktif_urunler = [u for u, b in self.veri["u"].items() if b.get("adet", 0) > 0]
        self.urun_combo['values'] = aktif_urunler
        
        messagebox.showinfo("Bilgi", "Satış silindi ve stoklar güncellendi.")

    def setup_veresiye_tab(self):
        self.veresiye_frame = ctk.CTkFrame(self.tab2)
        self.veresiye_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(self.veresiye_frame, text="Müşteri Veresiye Defteri", font=("Arial", 16, "bold")).pack(anchor="w", padx=5, pady=5)
        
        self.veresiye_agac = ttk.Treeview(self.veresiye_frame, columns=("Müşteri", "Toplam Borç", "Ödenen", "Kalan Borç"), show="headings")
        for col in ("Müşteri", "Toplam Borç", "Ödenen", "Kalan Borç"):
            self.veresiye_agac.heading(col, text=col)
        self.veresiye_agac.pack(fill="both", expand=True, padx=5, pady=5)
        
        tahsilat_frame = ctk.CTkFrame(self.veresiye_frame)
        tahsilat_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(tahsilat_frame, text="Tahsilat Alınacak Müşteri:").grid(row=0, column=0, padx=5, pady=5)
        self.tahsilat_musteri_combo = ttk.Combobox(tahsilat_frame)
        self.tahsilat_musteri_combo.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(tahsilat_frame, text="Tahsil Edilen Tutar (TL):").grid(row=0, column=2, padx=5, pady=5)
        self.tahsilat_entry = ctk.CTkEntry(tahsilat_frame, width=100)
        self.tahsilat_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(tahsilat_frame, text="Tahsilat Türü:").grid(row=0, column=4, padx=5, pady=5)
        self.tahsilat_tip_combo = ttk.Combobox(tahsilat_frame, values=["Nakit", "Kredi Kartı"], width=10)
        self.tahsilat_tip_combo.set("Nakit")
        self.tahsilat_tip_combo.grid(row=0, column=5, padx=5, pady=5)
        
        ctk.CTkButton(tahsilat_frame, text="💵 Tahsilatı Kaydet", fg_color="#2b9348", command=self.tahsilat_kaydet).grid(row=0, column=6, padx=10, pady=5)
        
        self.veresiyeleri_guncelle()

    def veresiyeleri_guncelle(self):
        for i in self.veresiye_agac.get_children():
            self.veresiye_agac.delete(i)
            
        borclar = {}
        odenenler = {}
        for s in self.veri["s"]:
            if s.get("odeme") == "Veresiye" and s.get("musteri"):
                borclar[s["musteri"]] = borclar.get(s["musteri"], 0) + s["tutar"]
        for t in self.veri["t"]:
            if t.get("musteri"):
                odenenler[t["musteri"]] = odenenler.get(t["musteri"], 0) + t.get("tutar", 0)
                
        aktif_borclular = []
        for m, b in borclar.items():
            kal = b - odenenler.get(m, 0)
            if kal > 0.01:
                aktif_borclular.append(m)
                self.veresiye_agac.insert("", "end", values=(m, f"{b:.2f} TL", f"{odenenler.get(m, 0):.2f} TL", f"{kal:.2f} TL"))
                
        if hasattr(self, "tahsilat_musteri_combo"):
            self.tahsilat_musteri_combo['values'] = aktif_borclular

    def tahsilat_kaydet(self):
        musteri = self.tahsilat_musteri_combo.get()
        tutar_str = self.tahsilat_entry.get()
        tip = self.tahsilat_tip_combo.get()
        
        if not musteri or not tutar_str:
            messagebox.showwarning("Uyarı", "Lütfen müşteri seçin ve tutar girin.")
            return
            
        try:
            tutar = float(tutar_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz tutar.")
            return
            
        if tutar <= 0:
            messagebox.showerror("Hata", "Tutar sıfırdan büyük olmalıdır.")
            return
            
        self.veri["t"].append({
            "tarih": datetime.now().strftime("%d.%m.%Y"),
            "musteri": musteri,
            "tutar": tutar,
            "tip": tip
        })
        self.verileri_kaydet()
        self.veresiyeleri_guncelle()
        self.tahsilat_entry.delete(0, tk.END)
        messagebox.showinfo("Başarılı", f"{musteri} hesabından {tutar:.2f} TL tahsilat kaydedildi.")

    def setup_cari_tab(self):
        frame = ctk.CTkFrame(self.tab3)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Yeni Cari Müşteri / Firma Ekle", font=("Arial", 16, "bold")).pack(anchor="w", padx=5, pady=5)
        
        giris_f = ctk.CTkFrame(frame)
        giris_f.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(giris_f, text="Müşteri Adı:").pack(side="left", padx=5)
        self.yeni_m_entry = ctk.CTkEntry(giris_f, width=250)
        self.yeni_m_entry.pack(side="left", padx=5)
        
        ctk.CTkButton(giris_f, text="➕ Müşteri Ekle", fg_color="#1f538d", command=self.musteri_ekle).pack(side="left", padx=5)
        
        ctk.CTkLabel(frame, text="Kayıtlı Müşteriler", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(15, 5))
        self.cari_agac = ttk.Treeview(frame, columns=("Müşteri Adı",), show="headings")
        self.cari_agac.heading("Müşteri Adı", text="Müşteri / Firma Adı")
        self.cari_agac.pack(fill="both", expand=True, padx=5, pady=5)
        self.carileri_guncelle()

    def musteri_ekle(self):
        ad = self.yeni_m_entry.get().strip().upper()
        if not ad:
            messagebox.showwarning("Uyarı", "Müşteri adı boş olamaz.")
            return
        if ad in self.veri["ml"]:
            messagebox.showwarning("Uyarı", "Bu müşteri zaten kayıtlı.")
            return
            
        self.veri["ml"].append(ad)
        self.verileri_kaydet()
        self.musteri_combo['values'] = ["GENEL MÜŞTERİ"] + self.veri["ml"]
        self.carileri_guncelle()
        self.yeni_m_entry.delete(0, tk.END)
        messagebox.showinfo("Başarılı", f"'{ad}' başarıyla eklendi.")

    def carileri_guncelle(self):
        for i in self.cari_agac.get_children():
            self.cari_agac.delete(i)
        tum_m = sorted(list(set(self.veri["ml"] + [s.get("musteri") for s in self.veri["s"] if s.get("musteri") and s.get("musteri") != "GENEL MÜŞTERİ"])))
        for m in tum_m:
            self.cari_agac.insert("", "end", values=(m,))

    def setup_kasa_tab(self):
        frame = ctk.CTkFrame(self.tab4)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.kasa_ozet_label = ctk.CTkLabel(frame, text="Kasa Özeti", font=("Arial", 16, "bold"))
        self.kasa_ozet_label.pack(anchor="w", padx=5, pady=5)
        
        gider_f = ctk.CTkFrame(frame)
        gider_f.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkLabel(gider_f, text="Gider Ekle (Maaş, Kira vb.)", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        ctk.CTkLabel(gider_f, text="Gider Türü:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.gider_tur_combo = ttk.Combobox(gider_f, values=["Muhasebe Ücreti", "Çalışan Maaşı", "Kira", "Elektrik / Su", "Dükkan Masrafı", "Diğer"])
        self.gider_tur_combo.set("Dükkan Masrafı")
        self.gider_tur_combo.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(gider_f, text="Tutar (TL):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.gider_tutar_entry = ctk.CTkEntry(gider_f, width=100)
        self.gider_tutar_entry.grid(row=1, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(gider_f, text="Kaynak:").grid(row=1, column=4, padx=5, pady=5, sticky="w")
        self.gider_tip_combo = ttk.Combobox(gider_f, values=["Nakit", "Kredi Kartı"], width=10)
        self.gider_tip_combo.set("Nakit")
        self.gider_tip_combo.grid(row=1, column=5, padx=5, pady=5)
        
        ctk.CTkLabel(gider_f, text="Detay:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.gider_detay_entry = ctk.CTkEntry(gider_f, width=300)
        self.gider_detay_entry.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        ctk.CTkButton(gider_f, text="💸 Gideri Kaydet", fg_color="#d90429", command=self.gider_kaydet).grid(row=2, column=4, columnspan=2, padx=5, pady=5, sticky="ew")

    def gider_kaydet(self):
        tur = self.gider_tur_combo.get()
        tutar_str = self.gider_tutar_entry.get()
        tip = self.gider_tip_combo.get()
        detay = self.gider_detay_entry.get().strip()
        
        try:
            tutar = float(tutar_str.replace(",", "."))
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz tutar.")
            return
            
        if tutar <= 0:
            messagebox.showerror("Hata", "Tutar sıfırdan büyük olmalıdır.")
            return
            
        self.veri["g"].append({
            "tarih": datetime.now().strftime("%d.%m.%Y"),
            "tur": tur,
            "tutar": tutar,
            "tip": tip,
            "detay": f"{tur}" + (f" - {detay}" if detay else "")
        })
        self.verileri_kaydet()
        self.gider_tutar_entry.delete(0, tk.END)
        self.gider_detay_entry.delete(0, tk.END)
        messagebox.showinfo("Başarılı", "Gider kaydedildi.")

    def setup_stok_tab(self):
        frame = ctk.CTkFrame(self.tab5)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        giriş_f = ctk.CTkFrame(frame)
        giriş_f.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(giriş_f, text="Ürün Adı:").grid(row=0, column=0, padx=5, pady=5)
        self.stok_ad_entry = ctk.CTkEntry(giriş_f)
        self.stok_ad_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(giriş_f, text="Eklenecek Adet:").grid(row=0, column=2, padx=5, pady=5)
        self.stok_adet_entry = ctk.CTkEntry(giriş_f, width=80)
        self.stok_adet_entry.insert(0, "10")
        self.stok_adet_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(giriş_f, text="Birim Maliyet (TL):").grid(row=0, column=4, padx=5, pady=5)
        self.stok_maliyet_entry = ctk.CTkEntry(giriş_f, width=100)
        self.stok_maliyet_entry.grid(row=0, column=5, padx=5, pady=5)
        
        ctk.CTkLabel(giriş_f, text="Kritik Sınır:").grid(row=0, column=6, padx=5, pady=5)
        self.stok_kritik_entry = ctk.CTkEntry(giriş_f, width=60)
        self.stok_kritik_entry.insert(0, "5")
        self.stok_kritik_entry.grid(row=0, column=7, padx=5, pady=5)
        
        self.kasadan_dus_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(giriş_f, text="Ücretini Nakit Kasadan Düş", variable=self.kasadan_dus_var).grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        
        ctk.CTkButton(giriş_f, text="➕ Ürünü Kaydet / Güncelle", fg_color="#1f538d", command=self.stok_kaydet).grid(row=1, column=3, columnspan=5, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(frame, text="Mevcut Stok Listesi", font=("Arial", 14, "bold")).pack(anchor="w", padx=5, pady=(15, 5))
        self.stok_agac = ttk.Treeview(frame, columns=("Ürün", "Adet", "Kritik Sınır", "Birim Maliyet", "Toplam Değer"), show="headings")
        for col in ("Ürün", "Adet", "Kritik Sınır", "Birim Maliyet", "Toplam Değer"):
            self.stok_agac.heading(col, text=col)
        self.stok_agac.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.stoklari_guncelle()

    def stok_kaydet(self):
        ad = self.stok_ad_entry.get().strip().upper()
        if not ad:
            messagebox.showwarning("Uyarı", "Ürün adı boş olamaz.")
            return
            
        try:
            adet = int(self.stok_adet_entry.get())
            maliyet = float(self.stok_maliyet_entry.get().replace(",", "."))
            kritik = int(self.stok_kritik_entry.get())
        except ValueError:
            messagebox.showerror("Hata", "Geçersiz sayısal değer.")
            return
            
        mevcut = self.veri["u"].get(ad, {"adet": 0, "maliyet": 0, "kritik": 5})
        mevcut["adet"] += adet
        mevcut["maliyet"] = maliyet
        mevcut["kritik"] = kritik
        self.veri["u"][ad] = mevcut
        
        if self.kasadan_dus_var.get() and (adet * maliyet) > 0:
            self.veri["g"].append({
                "tarih": datetime.now().strftime("%d.%m.%Y"),
                "tur": "Ürün Alım Gideri",
                "tutar": adet * maliyet,
                "tip": "Nakit",
                "detay": f"{ad} ({adet} adet alım)"
            })
            
        self.verileri_kaydet()
        self.stoklari_guncelle()
        
        aktif_urunler = [u for u, b in self.veri["u"].items() if b.get("adet", 0) > 0]
        self.urun_combo['values'] = aktif_urunler
        
        self.stok_ad_entry.delete(0, tk.END)
        messagebox.showinfo("Başarılı", f"'{ad}' başarıyla kaydedildi.")

    def stoklari_guncelle(self):
        for i in self.stok_agac.get_children():
            self.stok_agac.delete(i)
        for k, v in self.veri["u"].items():
            self.stok_agac.insert("", "end", values=(
                k, v["adet"], v.get("kritik", 5),
                f"{v.get('maliyet', 0):.2f} TL",
                f"{(v['adet'] * v.get('maliyet', 0)):.2f} TL"
            ))

    def setup_kritik_tab(self):
        frame = ctk.CTkFrame(self.tab6)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(frame, text="Kritik Stok Seviyesindeki Ürünler", font=("Arial", 16, "bold")).pack(anchor="w", padx=5, pady=5)
        self.kritik_agac = ttk.Treeview(frame, columns=("Ürün", "Mevcut Adet", "Kritik Sınır"), show="headings")
        for col in ("Ürün", "Mevcut Adet", "Kritik Sınır"):
            self.kritik_agac.heading(col, text=col)
        self.kritik_agac.pack(fill="both", expand=True, padx=5, pady=5)
        self.kritikleri_guncelle()

    def kritikleri_guncelle(self):
        for i in self.kritik_agac.get_children():
            self.kritik_agac.delete(i)
        for k, v in self.veri["u"].items():
            if v["adet"] <= v.get("kritik", 5):
                self.kritik_agac.insert("", "end", values=(k, v["adet"], v.get("kritik", 5)))

    def setup_rapor_tab(self):
        frame = ctk.CTkFrame(self.tab7)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.rapor_label = ctk.CTkLabel(frame, text="Genel Finansal Raporlar", font=("Arial", 18, "bold"))
        self.rapor_label.pack(anchor="w", padx=10, pady=10)
        
        self.rapor_icerik = ctk.CTkLabel(frame, text="", font=("Arial", 14), justify="left")
        self.rapor_icerik.pack(anchor="w", padx=20, pady=10)
        
        ctk.CTkButton(frame, text="Raporları Yenile", command=self.raporlari_guncelle).pack(anchor="w", padx=10, pady=10)
        self.raporlari_guncelle()

    def raporlari_guncelle(self):
        toplam_ciro = sum(s.get("tutar", 0) for s in self.veri["s"])
        toplam_kar = sum(s.get("kar", 0) for s in self.veri["s"])
        toplam_gider = sum(g.get("tutar", 0) for g in self.veri["g"])
        net_kazanc = toplam_kar - toplam_gider
        
        metin = (
            f"• Toplam Ciro: {toplam_ciro:.2f} TL\n\n"
            f"• Toplam Brüt Kâr: {toplam_kar:.2f} TL\n\n"
            f"• Toplam Giderler: {toplam_gider:.2f} TL\n\n"
            f"• Net Kazanç (Kâr - Gider): {net_kazanc:.2f} TL"
        )
        self.rapor_icerik.configure(text=metin)

if __name__ == "__main__":
    app = StokUygulamasi()
    app.mainloop()
