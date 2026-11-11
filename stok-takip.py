import json
import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Gökkuşağı Temizlik ve Ambalaj", page_icon="🌈", layout="wide"
)

FILE = "stok_veri.json"


# Veri Yükleme ve Güvenlik Kontrolü
def veri_yukle():
  if os.path.exists(FILE):
    try:
      with open(FILE, "r", encoding="utf-8") as f:
        d = json.load(f)
        if not isinstance(d.get("u"), dict):
          d["u"] = {}
        if not isinstance(d.get("s"), list):
          d["s"] = []
        if not isinstance(d.get("t"), list):
          d["t"] = []
        if not isinstance(d.get("g"), list):
          d["g"] = []
        if not isinstance(d.get("ml"), list):
          d["ml"] = []
        return d
    except:
      pass
  return {"u": {}, "s": [], "t": [], "g": [], "ml": []}


def veri_kaydet(d):
  with open(FILE, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=4)


veri = veri_yukle()

st.title("🌈 Gökkuşağı Temizlik ve Ambalaj - Stok & Finans")

# Menü Sekmeleri
menu = st.sidebar.radio(
    "Menü",
    [
        "Sepet & Satış",
        "Veresiye Defteri",
        "Cari Hesaplar",
        "Kasa & Giderler",
        "Stok Listesi",
        "Raporlar",
    ],
)

# 1. SEPET & SATIŞ YAP
if menu == "Sepet & Satış":
  st.header("🛒 Satış ve Sepet Yönetimi")

  col1, col2 = st.columns(2)
  with col1:
    musteri_listesi = ["GENEL MÜŞTERİ"] + veri.get("ml", [])
    for s in veri["s"]:
      if (
          isinstance(s, dict)
          and s.get("musteri")
          and s["musteri"] not in musteri_listesi
      ):
        musteri_listesi.append(s["musteri"])
    musteri = st.selectbox("Müşteri / Firma Seç", sorted(list(set(musteri_listesi))))

    aktif_urunler = [
        u
        for u, b in veri["u"].items()
        if isinstance(b, dict) and b.get("adet", 0) > 0
    ]
    urun = st.selectbox(
        "Ürün Seç", sorted(aktif_urunler) if aktif_urunler else ["Stokta ürün yok"]
    )

  with col2:
    adet = st.number_input("Adet", min_value=1, value=1)
    varsayilan_fiyat = (
        veri["u"].get(urun, {"maliyet": 0}).get("maliyet", 0) * 1.2
        if urun in veri["u"]
        else 0.0
    )
    birim_fiyat = st.number_input(
        "Birim Satış Fiyatı (TL)", min_value=0.0, value=float(varsayilan_fiyat)
    )
    odeme_tipi = st.selectbox(
        "Ödeme Yöntemi", ["Nakit", "Kredi Kartı", "Veresiye"]
    )

  if "sepet" not in st.session_state:
    st.session_state.sepet = []

  if st.button("➕ Sepete Ekle"):
    if urun and urun != "Stokta ürün yok":
      st.session_state.sepet.append({
          "urun": urun,
          "adet": adet,
          "birim": birim_fiyat,
          "tutar": adet * birim_fiyat,
      })
      st.success(f"{urun} sepete eklendi.")
    else:
      st.error("Lütfen geçerli bir ürün seçin.")

  if st.session_state.sepet:
    st.subheader("Aktif Sepet")
    sepet_gosterim = []
    for item in st.session_state.sepet:
      sepet_gosterim.append({
          "Ürün": item["urun"],
          "Adet": item["adet"],
          "Birim Fiyat": f"{item['birim']:.2f} TL",
          "Toplam Tutar": f"{item['tutar']:.2f} TL",
      })
    st.table(pd.DataFrame(sepet_gosterim))

    if st.button("🛒 Sepeti Satışa Dönüştür (Tamamla)"):
      if odeme_tipi == "Veresiye" and musteri == "GENEL MÜŞTERİ":
        st.error(
            "Veresiye satışlar için Genel Müşteri seçilemez, geçerli bir"
            " müşteri adı seçmelisiniz."
        )
      else:
        bugun = datetime.now().strftime("%d.%m.%Y")
        hata_var = False
        for item in st.session_state.sepet:
          u_adi = item["urun"]
          u_adet = item["adet"]
          if veri["u"][u_adi]["adet"] < u_adet:
            st.error(f"{u_adi} için yeterli stok yok!")
            hata_var = True
            break

        if not hata_var:
          for item in st.session_state.sepet:
            u_adi = item["urun"]
            u_adet = item["adet"]
            u_tutar = item["tutar"]

            veri["u"][u_adi]["adet"] -= u_adet
            mal = veri["u"][u_adi]["maliyet"] * u_adet
            kar = u_tutar - mal

            veri["s"].append({
                "tarih": bugun,
                "urun": u_adi,
                "adet": u_adet,
                "ciro": u_tutar,
                "maliyet": mal,
                "kar": kar,
                "odeme_tipi": odeme_tipi,
                "musteri": musteri,
            })
          veri_kaydet(veri)
          st.session_state.sepet = []
          st.success("Satış başarıyla tamamlandı ve stoktan düşüldü!")
          st.rerun()

  st.subheader("Son Satışlar")
  if veri["s"]:
    goruntulenecek_satislar = []
    for s in reversed(veri["s"]):
      goruntulenecek_satislar.append({
          "Tarih": s.get("tarih", ""),
          "Müşteri": s.get("musteri", ""),
          "Ürün": s.get("urun", ""),
          "Adet": s.get("adet", 0),
          "Ciro": f"{s.get('ciro', 0):.2f} TL",
          "Maliyet": f"{s.get('maliyet', 0):.2f} TL",
          "Kâr": f"{s.get('kar', 0):.2f} TL",
          "Ödeme Tipi": s.get("odeme_tipi", ""),
      })
    st.table(pd.DataFrame(goruntulenecek_satislar))
  else:
    st.info("Henüz satış kaydı yok.")

# 2. VERESİYE DEFTERİ
elif menu == "Veresiye Defteri":
  st.header("📖 Müşteri Veresiye Defteri")
  borclar = {}
  odenenler = {}

  for s in veri["s"]:
    if (
        isinstance(s, dict)
        and s.get("odeme_tipi") == "Veresiye"
        and s.get("musteri")
    ):
      borclar[s["musteri"]] = borclar.get(s["musteri"], 0) + s["ciro"]
  for t in veri["t"]:
    if isinstance(t, dict) and t.get("musteri"):
      odenenler[t["musteri"]] = odenenler.get(t["musteri"], 0) + t.get(
          "tutar", 0
      )

  veresiye_listesi = []
  for m, b in borclar.items():
    kal = b - odenenler.get(m, 0)
    if kal > 0.01:
      veresiye_listesi.append({
          "Müşteri": m,
          "Toplam Borç": f"{b:.2f} TL",
          "Ödenen": f"{odenenler.get(m, 0):.2f} TL",
          "Kalan Borç": f"{kal:.2f} TL",
      })

  if veresiye_listesi:
    st.table(pd.DataFrame(veresiye_listesi))

    ham_veresiye = []
    for m, b in borclar.items():
      kal = b - odenenler.get(m, 0)
      if kal > 0.01:
        ham_veresiye.append(m)

    Secilen_m = st.selectbox("Tahsilat Alınacak Müşteri", ham_veresiye)
    tahsilat_tutari = st.number_input("Tahsil Edilen Tutar (TL)", min_value=0.0)
    t_tipi = st.selectbox("Tahsilat Türü", ["Nakit", "Kredi Kartı"])

    if st.button("💵 Tahsilatı Kaydet ve Kasaya Ekle"):
      if tahsilat_tutari > 0:
        veri["t"].append({
            "tarih": datetime.now().strftime("%d.%m.%Y"),
            "musteri": Secilen_m,
            "tutar": tahsilat_tutari,
            "tip": t_tipi,
        })
        veri_kaydet(veri)
        st.success(f"{Secilen_m} hesabından {tahsilat_tutari:.2f} TL tahsil edildi.")
        st.rerun()
  else:
    st.info("Kayıtlı veresiye borcu bulunan müşteri yok.")

# 3. CARİ HESAPLAR
elif menu == "Cari Hesaplar":
  st.header("👥 Cari Müşteri ve Firma Yönetimi")
  yeni_m = st.text_input("Yeni Müşteri / Firma Adı")
  if st.button("➕ Müşteri Ekle"):
    if yeni_m.strip():
      m_ad = yeni_m.strip().upper()
      if m_ad not in veri["ml"]:
        veri["ml"].append(m_ad)
        veri_kaydet(veri)
        st.success(f"'{m_ad}' eklendi.")
        st.rerun()

  st.subheader("Kayıtlı Müşteriler")
  tum_m = sorted(
      list(
          set(
              veri["ml"]
              + [
                  s["musteri"]
                  for s in veri["s"]
                  if isinstance(s, dict)
                  and s.get("musteri")
                  and s["musteri"] != "GENEL MÜŞTERİ"
              ]
          )
      )
  )
  if tum_m:
    st.write(tum_m)
  else:
    st.info("Henüz kayıtlı müşteri yok.")

# 4. KASA & GİDERLER
elif menu == "Kasa & Giderler":
  st.header("💰 Kasa Özeti ve Gider Yönetimi")

  nakit_giris = sum(
      s.get("ciro", 0)
      for s in veri["s"]
      if isinstance(s, dict) and s.get("odeme_tipi") == "Nakit"
  ) + sum(
      t.get("tutar", 0)
      for t in veri["t"]
      if isinstance(t,
