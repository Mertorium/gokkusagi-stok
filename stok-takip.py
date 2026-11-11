from datetime import datetime
import json
import os
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Gökkuşağı Temizlik ve Ambalaj - Stok & Finans",
    page_icon="🌈",
    layout="wide",
)

FILE = "stok_veri.json"


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

# Üst Başlık
st.markdown(
    "### 🌈 GÖKKUŞAĞI TEMİZLİK VE AMBALAJ - Stok & Finans Yönetimi"
)
st.divider()

# Menü Sekmeleri (Üst Sekme Görünümü)
menu = st.selectbox(
    "Menü Sekmeleri",
    [
        "1. Sepet & Satış Yap",
        "2. Veresiye",
        "3. Cari",
        "4. Kasa",
        "5. Stok Listesi",
        "6. Kritik Stok",
        "7. Raporlar",
    ],
    label_visibility="collapsed",
)

# 1. SEPET & SATIŞ YAP
if menu == "1. Sepet & Satış Yap":
  # Masaüstündeki gibi sol ve sağ ana kolonlar
  sol_kolon, sag_kolon = st.columns([1.1, 1.9], gap="medium")

  with sol_kolon:
    st.markdown("#### 🛒 Sepet ve Toplu Satış Paneli")
    with st.container(border=True):
      c1, c2, c3 = st.columns([2, 1, 1])
      with c1:
        tarih = st.text_input("Tarih", value=datetime.now().strftime("%d.%m.%Y"))
      with c2:
        st.write("")
        if st.button("Bugün"):
          tarih = datetime.now().strftime("%d.%m.%Y")
      with c3:
        st.write("")
        if st.button("Dün"):
          from datetime import timedelta

          tarih = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")

      musteri_listesi = ["GENEL MÜŞTERİ"] + veri.get("ml", [])
      musteri = st.selectbox("Müşteri / Firma", sorted(list(set(musteri_listesi))))

      aktif_urunler = [
          u
          for u, b in veri["u"].items()
          if isinstance(b, dict) and b.get("adet", 0) > 0
      ]
      urun = st.selectbox(
          "Ürün Seçin",
          sorted(aktif_urunler) if aktif_urunler else ["Stokta ürün yok"],
      )

      col_a, col_b = st.columns(2)
      with col_a:
        adet = st.number_input("Adet", min_value=1, value=1)
      with col_b:
        varsayilan_fiyat = (
            veri["u"].get(urun, {"maliyet": 0}).get("maliyet", 0) * 1.2
            if urun in veri["u"]
            else 0.0
        )
        birim_fiyat = st.number_input(
            "Birim Fiyat (TL)", min_value=0.0, value=float(varsayilan_fiyat)
        )

      odeme_tipi = st.radio(
          "Ödeme Yöntemi", ["Nakit", "Kredi Kartı", "Veresiye"], horizontal=True
      )

      st.markdown(
          f"**Ürün Toplamı: {adet * birim_fiyat:.2f} TL**",
          help="Seçilen miktar ve birim fiyatın toplamı",
      )

      if "sepet" not in st.session_state:
        st.session_state.sepet = []

      if st.button(
          "➕ Sepete Ekle", use_container_width=True, type="primary"
      ):
        if urun and urun != "Stokta ürün yok":
          st.session_state.sepet.append({
              "urun": urun,
              "adet": adet,
              "birim": birim_fiyat,
              "tutar": adet * birim_fiyat,
          })
          st.success(f"{urun} sepete eklendi.")
          st.rerun()
        else:
          st.error("Geçerli bir ürün seçin.")

      if st.button(
          "🛒 Sepeti Satışa Dönüştür (Tamamla)", use_container_width=True
      ):
        if not st.session_state.sepet:
          st.warning("Sepet boş.")
        elif odeme_tipi == "Veresiye" and musteri == "GENEL MÜŞTERİ":
          st.error("Veresiye satışlar için Genel Müşteri seçilemez.")
        else:
          hata = False
          for item in st.session_state.sepet:
            if veri["u"][item["urun"]]["adet"] < item["adet"]:
              st.error(f"{item['urun']} için yeterli stok yok!")
              hata = True
              break
          if not hata:
            for item in st.session_state.sepet:
              u_adi = item["urun"]
              u_adet = item["adet"]
              u_tutar = item["tutar"]
              veri["u"][u_adi]["adet"] -= u_adet
              mal = veri["u"][u_adi]["maliyet"] * u_adet
              kar = u_tutar - mal
              veri["s"].append({
                  "no": len(veri["s"]) + 1,
                  "tarih": tarih,
                  "urun": u_adi,
                  "adet": u_adet,
                  "tutar": u_tutar,
                  "maliyet": mal,
                  "kar": kar,
                  "odeme": odeme_tipi,
                  "musteri": musteri,
              })
            veri_kaydet(veri)
            st.session_state.sepet = []
            st.success("Satış başarıyla tamamlandı!")
            st.rerun()

    # Aktif Sepet Listesi
    st.markdown("#### Aktif Sepet Listesi")
    if st.session_state.sepet:
      sepet_gosterim = []
      for idx, item in enumerate(st.session_state.sepet):
        sepet_gosterim.append({
            "No": idx + 1,
            "Ürün": item["urun"],
            "Adet": item["adet"],
            "Birim Fiyat": f"{item['birim']:.2f} TL",
            "Toplam Tutar": f"{item['tutar']:.2f} TL",
        })
      st.table(pd.DataFrame(sepet_gosterim))
      sepet_toplam = sum(i["tutar"] for i in st.session_state.sepet)
      st.markdown(f"**SEPET GENEL TOPLAM: {sepet_toplam:.2f} TL**")

      if st.button("Seçilen Ürünü Sepetten Çıkar", type="secondary"):
        if st.session_state.sepet:
          st.session_state.sepet.pop()
          st.rerun()
    else:
      st.info("Aktif sepet boş.")

  with sag_kolon:
    st.markdown("#### 📋 Son Satış İşlemleri")
    if veri["s"]:
      satis_listesi = []
      for s in reversed(veri["s"]):
        satis_listesi.append({
            "No": s.get("no", 1),
            "Tarih": s.get("tarih", ""),
            "Ürün": s.get("urun", ""),
            "Adet": s.get("adet", 0),
            "Tutar": f"{s.get('tutar', 0):.2f} TL",
            "Kâr": f"{s.get('kar', 0):.2f} TL",
            "Ödeme": s.get("odeme", ""),
            "Müşteri": s.get("musteri", ""),
        })
      st.table(pd.DataFrame(satis_listesi))

      if st.button("Seçili Son Satışı İade Et / Sil"):
        if veri["s"]:
          silinen = veri["s"].pop()
          veri["u"][silinen["urun"]]["adet"] += silinen["adet"]
          veri_kaydet(veri)
          st.success("Satış iptal edildi ve stok iade alındı.")
          st.rerun()
    else:
      st.info("Henüz satış kaydı bulunmuyor.")

# 2. VERESİYE
elif menu == "2. Veresiye":
  st.header("📖 Müşteri Veresiye Defteri")
  # Veresiye içeriği...
  borclar = {}
  odenenler = {}
  for s in veri["s"]:
    if s.get("odeme") == "Veresiye" and s.get("musteri"):
      borclar[s["musteri"]] = borclar.get(s["musteri"], 0) + s["tutar"]
  for t in veri["t"]:
    if t.get("musteri"):
      odenenler[t["musteri"]] = odenenler.get(t["musteri"], 0) + t.get("tutar", 0)

  veresiye_data = []
  for m, b in borclar.items():
    kal = b - odenenler.get(m, 0)
    if kal > 0.01:
      veresiye_data.append({
          "Müşteri": m,
          "Toplam Borç": f"{b:.2f} TL",
          "Ödenen": f"{odenenler.get(m, 0):.2f} TL",
          "Kalan Borç": f"{kal:.2f} TL",
      })
  if veresiye_data:
    st.table(pd.DataFrame(veresiye_data))
  else:
    st.info("Kayıtlı veresiye borcu yok.")

# 3. CARİ
elif menu == "3. Cari":
  st.header("👥 Cari Müşteri ve Firma Yönetimi")
  yeni_m = st.text_input("Yeni Müşteri / Firma Adı")
  if st.button("Müşteri Ekle"):
    if yeni_m.strip():
      m_ad = yeni_m.strip().upper()
      if m_ad not in veri["ml"]:
        veri["ml"].append(m_ad)
        veri_kaydet(veri)
        st.success(f"'{m_ad}' eklendi.")
        st.rerun()
  st.write("Kayıtlı Müşteriler:", veri["ml"])

# 4. KASA
elif menu == "4. Kasa":
  st.header("💰 Kasa Özeti ve Gider Yönetimi")
  # Kasa özeti hesapları...
  toplam_satis = sum(s.get("tutar", 0) for s in veri["s"])
  st.metric("Toplam Satış / Ciro", f"{toplam_satis:.2f} TL")

# 5. STOK LİSTESİ
elif menu == "5. Stok Listesi":
  st.header("📦 Ürün ve Stok Yönetimi")
  with st.form("stok_ekle_form"):
    u_ad = st.text_input("Ürün Adı").strip().upper()
    u_adet = st.number_input("Adet", min_value=1, value=10)
    u_mal = st.number_input("Birim Maliyet (TL)", min_value=0.0)
    if st.form_submit_button("Ürünü Kaydet"):
      if u_ad:
        veri["u"][u_ad] = {"adet": u_adet, "maliyet": u_mal}
        veri_kaydet(veri)
        st.success(f"{u_ad} kaydedildi.")
        st.rerun()

  if veri["u"]:
    stok_list = [
        {
            "Ürün": k,
            "Adet": v["adet"],
            "Birim Maliyet": f"{v.get('maliyet',0):.2f} TL",
        }
        for k, v in veri["u"].items()
    ]
    st.table(pd.DataFrame(stok_list))

# 6. KRİTİK STOK
elif menu == "6. Kritik Stok":
  st.header("⚠️ Kritik Stok Seviyeleri")
  # Kritik stoklar...

# 7. RAPORLAR
elif menu == "7. Raporlar":
  st.header("📊 Finansal Raporlar")
  toplam_ciro = sum(s.get("tutar", 0) for s in veri["s"])
  toplam_kar = sum(s.get("kar", 0) for s in veri["s"])
  st.metric("Toplam Ciro", f"{toplam_ciro:.2f} TL")
  st.metric("Toplam Kâr", f"{toplam_kar:.2f} TL")
