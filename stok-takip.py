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
    df_sepet = pd.DataFrame(st.session_state.sepet)
    st.table(df_sepet)

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
    st.table(pd.DataFrame(veri["s"])[::-1])
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
          "Toplam Borç": b,
          "Ödenen": odenenler.get(m, 0),
          "Kalan Borç": kal,
      })

  if veresiye_listesi:
    df_v = pd.DataFrame(veresiye_listesi)
    st.table(df_v)

    Secilen_m = st.selectbox(
        "Tahsilat Alınacak Müşteri", [x["Müşteri"] for x in veresiye_listesi]
    )
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
        st.success(f"{Secilen_m} hesabından {tahsilat_tutari} TL tahsil edildi.")
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
      if isinstance(t, dict) and t.get("tip") == "Nakit"
  )
  nakit_gider = sum(
      g.get("tutar", 0)
      for g in veri["g"]
      if isinstance(g, dict) and g.get("tip") == "Nakit"
  )
  net_nakit = nakit_giris - nakit_gider

  kart_giris = sum(
      s.get("ciro", 0)
      for s in veri["s"]
      if isinstance(s, dict) and s.get("odeme_tipi") == "Kredi Kartı"
  ) + sum(
      t.get("tutar", 0)
      for t in veri["t"]
      if isinstance(t, dict) and t.get("tip") == "Kredi Kartı"
  )
  kart_gider = sum(
      g.get("tutar", 0)
      for g in veri["g"]
      if isinstance(g, dict) and g.get("tip") == "Kredi Kartı"
  )
  net_kart = kart_giris - kart_gider

  st.metric(
      "Net Kasa Toplamı",
      f"{net_nakit + net_kart:.2f} TL",
      f"Nakit: {net_nakit:.2f} TL | Kart: {net_kart:.2f} TL",
  )

  st.subheader("💸 Gider Ekle (Maaş, Muhasebe vb.)")
  g_tur = st.selectbox(
      "Gider Türü",
      [
          "Muhasebe Ücreti",
          "Çalışan Maaşı",
          "Kira",
          "Elektrik / Su",
          "Dükkan Masrafı",
          "Diğer",
      ],
  )
  g_tutar = st.number_input("Gider Tutarı (TL)", min_value=0.0)
  g_tip = st.selectbox("Ödeme Kaynağı", ["Nakit", "Kredi Kartı"])
  g_detay = st.text_input("Açıklama / Detay")

  if st.button("Gideri Kaydet ve Kasadan Düş"):
    if g_tutar > 0:
      veri["g"].append({
          "tarih": datetime.now().strftime("%d.%m.%Y"),
          "tur": g_tur,
          "tutar": g_tutar,
          "tip": g_tip,
          "detay": f"{g_tur}" + (f" - {g_detay}" if g_detay else ""),
      })
      veri_kaydet(veri)
      st.success("Gider kasadan düşüldü.")
      st.rerun()

# 5. STOK LİSTESİ
elif menu == "Stok Listesi":
  st.header("📦 Ürün ve Stok Yönetimi")

  with st.form("urun_ekle"):
    st.subheader("Yeni Ürün Ekle / Stok Girişi")
    u_ad = st.text_input("Ürün Adı").strip().upper()
    u_adet = st.number_input("Eklenecek Adet", min_value=0, value=10)
    u_maliyet = st.number_input(
        "Birim Maliyet / Alış Fiyatı (TL)", min_value=0.0
    )
    u_kritik = st.number_input("Kritik Stok Sınırı", min_value=1, value=5)
    kasadan_dus = st.checkbox("Ücretini Nakit Kasadan Düş")

    if st.form_submit_button("Ürünü Kaydet"):
      if u_ad:
        mevcut = veri["u"].get(
            u_ad, {"adet": 0, "maliyet": 0, "kritik": 5}
        )
        mevcut["adet"] += u_adet
        mevcut["maliyet"] = u_maliyet
        mevcut["kritik"] = u_kritik
        veri["u"][u_ad] = mevcut

        if kasadan_dus and (u_adet * u_maliyet) > 0:
          veri["g"].append({
              "tarih": datetime.now().strftime("%d.%m.%Y"),
              "tur": "Ürün Alım Gideri",
              "tutar": u_adet * u_maliyet,
              "tip": "Nakit",
              "detay": f"{u_ad} ({u_adet} adet alım)",
          })
        veri_kaydet(veri)
        st.success(f"{u_ad} başarıyla kaydedildi!")
        st.rerun()

  st.subheader("Mevcut Stoklar")
  if veri["u"]:
    stok_data = [
        {
            "Ürün": k,
            "Adet": v["adet"],
            "Kritik Sınır": v["kritik"],
            "Birim Maliyet": v["maliyet"],
            "Toplam Değer": v["adet"] * v["maliyet"],
        }
        for k, v in veri["u"].items()
    ]
    st.table(pd.DataFrame(stok_data))
  else:
    st.info("Henüz kayıtlı ürün yok.")

# 6. RAPORLAR
elif menu == "Raporlar":
  st.header("📊 Finansal Raporlar")
  toplam_ciro = sum(
      s.get("ciro", 0) for s in veri["s"] if isinstance(s, dict)
  )
  toplam_kar = sum(s.get("kar", 0) for s in veri["s"] if isinstance(s, dict))
  toplam_gider = sum(
      g.get("tutar", 0) for g in veri["g"] if isinstance(g, dict)
  )

  st.metric("Toplam Ciro", f"{toplam_ciro:.2f} TL")
  st.metric("Toplam Brüt Kâr", f"{toplam_kar:.2f} TL")
  st.metric("Toplam Giderler", f"{toplam_gider:.2f} TL")
  st.metric(
      "Net Kazanç (Kâr - Gider)", f"{toplam_kar - toplam_gider:.2f} TL"
  )
