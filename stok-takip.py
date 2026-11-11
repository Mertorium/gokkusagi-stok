from datetime import datetime, timedelta
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
    "<h1 style='text-align: center;'>🌈 GÖKKUŞAĞI TEMİZLİK VE AMBALAJ - Stok &"
    " Finans Yönetimi</h1>",
    unsafe_allow_html=True,
)
st.divider()

# Yatay Sekmeler (st.tabs)
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Sepet & Satış Yap",
    "Veresiye",
    "Cari",
    "Kasa",
    "Stok Listesi",
    "Kritik Stok",
    "Raporlar",
])

# 1. SEPET & SATIŞ YAP
with tab1:
  sol_kolon, sag_kolon = st.columns([1.1, 1.9], gap="medium")

  with sol_kolon:
    st.markdown("#### 🛒 Sepet ve Toplu Satış Paneli")
    with st.container(border=True):
      c1, c2, c3 = st.columns([2, 1, 1])
      with c1:
        tarih = st.text_input(
            "Tarih", value=datetime.now().strftime("%d.%m.%Y"), key="sepet_tarih"
        )
      with c2:
        st.write("")
        if st.button("Bugün"):
          tarih = datetime.now().strftime("%d.%m.%Y")
      with c3:
        st.write("")
        if st.button("Dün"):
          tarih = (datetime.now() - timedelta(days=1)).strftime("%d.%m.%Y")

      musteri_listesi = ["GENEL MÜŞTERİ"] + veri.get("ml", [])
      musteri = st.selectbox(
          "Müşteri / Firma", sorted(list(set(musteri_listesi)))
      )

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
        adet = st.number_input("Adet", min_value=1, value=1, key="sepet_adet")
      with col_b:
        varsayilan_fiyat = (
            veri["u"].get(urun, {"maliyet": 0}).get("maliyet", 0) * 1.2
            if urun in veri["u"]
            else 0.0
        )
        birim_fiyat = st.number_input(
            "Birim Fiyat (TL)",
            min_value=0.0,
            value=float(varsayilan_fiyat),
            key="sepet_fiyat",
        )

      odeme_tipi = st.radio(
          "Ödeme Yöntemi",
          ["Nakit", "Kredi Kartı", "Veresiye"],
          horizontal=True,
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
with tab2:
  st.header("📖 Müşteri Veresiye Defteri")
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
with tab3:
  st.header("👥 Cari Müşteri ve Firma Yönetimi")
  yeni_m = st.text_input("Yeni Müşteri / Firma Adı", key="cari_yeni_m")
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
with tab4:
  st.header("💰 Kasa Özeti ve Gider Yönetimi")
  toplam_satis = sum(s.get("tutar", 0) for s in veri["s"])
  st.metric("Toplam Satış / Ciro", f"{toplam_satis:.2f} TL")

# 5. STOK LİSTESİ (YENİ: Ürün Ekleme, Düzenleme ve Silme Özelliği Eklendi)
with tab5:
  st.header("📦 Ürün ve Stok Yönetimi")

  st.subheader("➕ Yeni Ürün Ekle")
  with st.form("stok_ekle_form"):
    u_ad = st.text_input("Ürün Adı").strip().upper()
    col_s1, col_s2 = st.columns(2)
    with col_s1:
      u_adet = st.number_input("Adet", min_value=1, value=10)
    with col_s2:
      u_kritik = st.number_input("Kritik Stok Eşiği", min_value=0, value=5)
    u_mal = st.number_input("Birim Maliyet (TL)", min_value=0.0)

    if st.form_submit_button("Ürünü Kaydet"):
      if u_ad:
        veri["u"][u_ad] = {
            "adet": u_adet,
            "maliyet": u_mal,
            "kritik": u_kritik,
        }
        veri_kaydet(veri)
        st.success(f"{u_ad} başarıyla kaydedildi.")
        st.rerun()

  st.divider()
  st.subheader("✏️ Stok Düzenle / Sil")
  if veri["u"]:
    secilen_stok = st.selectbox(
        "Düzenlenecek veya Silinecek Ürünü Seçin", sorted(list(veri["u"].keys()))
    )
    mevcut_bilgi = veri["u"][secilen_stok]

    with st.form("stok_duzenle_form"):
      d_adet = st.number_input(
          "Güncel Adet",
          min_value=0,
          value=int(mevcut_bilgi.get("adet", 0)),
      )
      d_kritik = st.number_input(
          "Güncel Kritik Eşik",
          min_value=0,
          value=int(mevcut_bilgi.get("kritik", 5)),
      )
      d_mal = st.number_input(
          "Güncel Birim Maliyet (TL)",
          min_value=0.0,
          value=float(mevcut_bilgi.get("maliyet", 0.0)),
      )

      col_d1, col_d2 = st.columns(2)
      with col_d1:
        guncelle_basildi = st.form_submit_button(
            "💾 Değişiklikleri Kaydet", type="primary"
        )
      with col_d2:
        sil_basildi = st.form_submit_button(
            "🗑️ Bu Ürünü Stoktan Sil", type="secondary"
        )

      if guncelle_basildi:
        veri["u"][secilen_stok] = {
            "adet": d_adet,
            "maliyet": d_mal,
            "kritik": d_kritik,
        }
        veri_kaydet(veri)
        st.success(f"{secilen_stok} güncellendi.")
        st.rerun()

      if sil_basildi:
        del veri["u"][secilen_stok]
        veri_kaydet(veri)
        st.success(f"{secilen_stok} stoktan tamamen silindi.")
        st.rerun()

  st.divider()
  st.subheader("📋 Mevcut Stok Listesi")
  if veri["u"]:
    stok_list = [
        {
            "Ürün": k,
            "Adet": v["adet"],
            "Kritik Eşik": v.get("kritik", 5),
            "Birim Maliyet": f"{v.get('maliyet',0):.2f} TL",
        }
        for k, v in veri["u"].items()
    ]
    st.table(pd.DataFrame(stok_list))
  else:
    st.info("Kayıtlı ürün bulunmuyor.")

# 6. KRİTİK STOK
with tab6:
  st.header("⚠️ Kritik Stok Seviyeleri")
  kritik_liste = []
  for k, v in veri["u"].items():
    esik = v.get("kritik", 5)
    if v["adet"] <= esik:
      kritik_liste.append(
          {"Ürün": k, "Mevcut Adet": v["adet"], "Kritik Eşik": esik}
      )

  if kritik_liste:
    st.table(pd.DataFrame(kritik_liste))
  else:
    st.success("Kritik seviyede ürün bulunmuyor.")

# 7. RAPORLAR
with tab7:
  st.header("📊 Finansal Raporlar")
  toplam_ciro = sum(s.get("tutar", 0) for s in veri["s"])
  toplam_kar = sum(s.get("kar", 0) for s in veri["s"])
  st.metric("Toplam Ciro", f"{toplam_ciro:.2f} TL")
  st.metric("Toplam Kâr", f"{toplam_kar:.2f} TL")
