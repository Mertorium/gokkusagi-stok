from datetime import datetime, timedelta
import io
import json
import os
import pandas as pd
import streamlit as st

# ReportLab kütüphanesini güvenli şekilde yükleme
try:
  from reportlab.lib.pagesizes import letter
  from reportlab.pdfgen import canvas

  reportlab_mevcut = True
except ImportError:
  reportlab_mevcut = False

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


# PDF Fiş Oluşturma Fonksiyonu (Kâr bilgisi içermez)
def satis_fisi_pdf_olustur(satis_detay):
  buffer = io.BytesIO()
  if reportlab_mevcut:
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "GÖKKUŞAĞI TEMİZLİK VE AMBALAJ")
    p.setFont("Helvetica", 10)
    p.drawString(50, height - 65, "Satış Fişi / Bilgilendirme Belgesi")
    p.line(50, height - 75, width - 50, height - 75)

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 110, f"Fiş No: #{satis_detay.get('no', 1)}")
    p.drawString(50, height - 130, f"Tarih: {satis_detay.get('tarih', '')}")
    p.drawString(
        50, height - 150, f"Müşteri / Firma: {satis_detay.get('musteri', '')}"
    )
    p.drawString(
        50, height - 170, f"Ödeme Yöntemi: {satis_detay.get('odeme', '')}"
    )

    p.line(50, height - 190, width - 50, height - 190)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 210, "Ürün Açıklaması")
    p.drawString(300, height - 210, "Adet")
    p.drawString(380, height - 210, "Toplam Tutar")

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 240, str(satis_detay.get("urun", "")))
    p.drawString(300, height - 240, str(satis_detay.get("adet", "")))
    p.drawString(380, height - 240, f"{satis_detay.get('tutar', 0):.2f} TL")

    p.line(50, height - 270, width - 50, height - 270)

    p.setFont("Helvetica-Bold", 14)
    p.drawString(
        300, height - 300, f"GENEL TOPLAM: {satis_detay.get('tutar', 0):.2f} TL"
    )

    p.showPage()
    p.save()
  buffer.seek(0)
  return buffer


veri = veri_yukle()

# Üst Başlık
st.markdown(
    "<h1 style='text-align: center;'>🌈 GÖKKUŞAĞI TEMİZLİK VE AMBALAJ - Stok &"
    " Finans Yönetimi</h1>",
    unsafe_allow_html=True,
)
st.divider()

# Yatay Sekmeler (st.tabs)
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "Sepet & Satış Yap",
    "Veresiye",
    "Cari",
    "Kasa",
    "Giderler",
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

      aktif_urunler = []
      for u_adi, alimlar in veri["u"].items():
        toplam_adet = sum(
            a.get("adet", 0) for a in alimlar if isinstance(a, dict)
        )
        if toplam_adet > 0:
          aktif_urunler.append(u_adi)

      urun = st.selectbox(
          "Ürün Seçin",
          sorted(aktif_urunler) if aktif_urunler else ["Stokta ürün yok"],
      )

      col_a, col_b = st.columns(2)
      with col_a:
        adet = st.number_input("Adet", min_value=1, value=1, key="sepet_adet")
      with col_b:
        varsayilan_fiyat = 0.0
        if urun in veri["u"] and veri["u"][urun]:
          varsayilan_fiyat = veri["u"][urun][-1].get("maliyet", 0.0) * 1.2

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
            u_adi = item["urun"]
            istenen_adet = item["adet"]
            toplam_stok = sum(
                a.get("adet", 0) for a in veri["u"].get(u_adi, [])
            )
            if toplam_stok < istenen_adet:
              st.error(f"'{u_adi}' için yeterli stok yok!")
              hata = True
              break

          if not hata:
            for item in st.session_state.sepet:
              u_adi = item["urun"]
              kalan_satis_adeti = item["adet"]
              u_tutar = item["tutar"]

              toplam_maliyet = 0.0
              while kalan_satis_adeti > 0 and veri["u"][u_adi]:
                en_eski_alim = veri["u"][u_adi][0]
                if en_eski_alim["adet"] > kalan_satis_adeti:
                  en_eski_alim["adet"] -= kalan_satis_adeti
                  toplam_maliyet += kalan_satis_adeti * en_eski_alim["maliyet"]
                  kalan_satis_adeti = 0
                else:
                  dusulen_adet = en_eski_alim["adet"]
                  toplam_maliyet += dusulen_adet * en_eski_alim["maliyet"]
                  kalan_satis_adeti -= dusulen_adet
                  veri["u"][u_adi].pop(0)

              kar = u_tutar - toplam_maliyet
              veri["s"].append({
                  "no": len(veri["s"]) + 1,
                  "tarih": tarih,
                  "urun": u_adi,
                  "adet": item["adet"],
                  "tutar": u_tutar,
                  "maliyet": toplam_maliyet,
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

  # SAĞ KOLON: Müşteri Bazlı Ayrı Başlıklar, Seçmeli İptal/Düzenleme ve PDF Fiş İndirme
  with sag_kolon:
    st.markdown("#### 📋 Müşteri Satışları ve İptal / Fiş İşlemleri")
    if veri["s"]:
      satis_secenekleri = [
          f"No: {s.get('no')} | Tarih: {s.get('tarih')} | Müşteri: {s.get('musteri')} | Ürün: {s.get('urun')} ({s.get('adet')} Adet) - {s.get('tutar'):.2f} TL"
          for s in veri["s"]
      ]
      secilen_satis_str = st.selectbox(
          "İşlem Yapılacak Satışı Seçin (İptal / İade / PDF Fiş)",
          satis_secenekleri[::-1],
          key="secilen_satis_yonetim",
      )

      if secilen_satis_str:
        satis_no_str = secilen_satis_str.split(" | ")[0].replace("No: ", "")
        satis_idx = None
        target_satis = None
        for idx, s in enumerate(veri["s"]):
          if str(s.get("no")) == satis_no_str:
            satis_idx = idx
            target_satis = s
            break

        if target_satis:
          st.info(
              f"Seçilen Satış -> Müşteri: {target_satis.get('musteri')} | Ürün:"
              f" {target_satis.get('urun')} | Adet: {target_satis.get('adet')}"
              f" | Tutar: {target_satis.get('tutar'):.2f} TL"
          )

          # PDF Fiş İndir Butonu
          if reportlab_mevcut:
            pdf_buffer = satis_fisi_pdf_olustur(target_satis)
            st.download_button(
                label="📄 Seçilen Satışın Fişini PDF Olarak İndir",
                data=pdf_buffer,
                file_name=f"Satis_Fisi_No_{target_satis.get('no')}.pdf",
                mime="application/pdf",
            )
          else:
            st.warning(
                "PDF oluşturucu (reportlab) sistemde yüklü değil. Lütfen"
                " 'requirements.txt' dosyasına 'reportlab' ekleyin."
            )

          onay_kutu = st.checkbox(
              "⚠️ İptal/İade işlemi için onay veriyorum",
              key=f"onay_{satis_no_str}",
          )

          col_islem1, col_islem2 = st.columns(2)
          with col_islem1:
            if st.button("🗑️ Seçilen Satışı Tamamen İptal Et"):
              if not onay_kutu:
                st.error("Lütfen önce onay kutusunu işaretleyin!")
              else:
                u_adi = target_satis.get("urun")
                iade_adet = target_satis.get("adet")
                if u_adi not in veri["u"]:
                  veri["u"][u_adi] = []
                if veri["u"][u_adi]:
                  veri["u"][u_adi][-1]["adet"] += iade_adet
                else:
                  veri["u"][u_adi].append({
                      "tarih": target_satis.get("tarih"),
                      "adet": iade_adet,
                      "maliyet": target_satis.get("maliyet") / iade_adet
                      if iade_adet > 0
                      else 0,
                      "kritik": 5,
                  })

                veri["s"].pop(satis_idx)
                veri_kaydet(veri)
                st.success(
                    "Satış iptal edildi ve ürünler stoğa geri eklendi."
                )
                st.rerun()

          with col_islem2:
            iade_parca_adet = st.number_input(
                "İade Adedi",
                min_value=1,
                max_value=int(target_satis.get("adet", 1)),
                value=1,
                key=f"iade_adet_{satis_no_str}",
            )
            if st.button("🔄 Kısmi İade Al"):
              if not onay_kutu:
                st.error("Lütfen önce onay kutusunu işaretleyin!")
              else:
                orijinal_adet = target_satis.get("adet")
                if iade_parca_adet >= orijinal_adet:
                  st.error(
                      "Tam adetten fazla iade için tamamen iptal butonunu"
                      " kullanın."
                  )
                else:
                  birim_fiyat_orijinal = (
                      target_satis.get("tutar") / orijinal_adet
                  )
                  birim_maliyet_orijinal = (
                      target_satis.get("maliyet") / orijinal_adet
                  )

                  iade_tutar = iade_parca_adet * birim_fiyat_orijinal
                  iade_maliyet = iade_parca_adet * birim_maliyet_orijinal
                  iade_kar = iade_tutar - iade_maliyet

                  target_satis["adet"] -= iade_parca_adet
                  target_satis["tutar"] -= iade_tutar
                  target_satis["maliyet"] -= iade_maliyet
                  target_satis["kar"] -= iade_kar

                  u_adi = target_satis.get("urun")
                  if u_adi not in veri["u"]:
                    veri["u"][u_adi] = []
                  if veri["u"][u_adi]:
                    veri["u"][u_adi][-1]["adet"] += iade_parca_adet
                  else:
                    veri["u"][u_adi].append({
                        "tarih": target_satis.get("tarih"),
                        "adet": iade_parca_adet,
                        "maliyet": birim_maliyet_orijinal,
                        "kritik": 5,
                    })

                  veri_kaydet(veri)
                  st.success(
                      f"{iade_parca_adet} adet ürün iade alındı ve stoğa"
                      " eklendi."
                  )
                  st.rerun()

      st.divider()
      st.markdown("#### 👤 Müşteri Bazlı Satış Başlıkları")
      musteri_gruplari = {}
      for s in veri["s"]:
        m_adi = s.get("musteri", "GENEL MÜŞTERİ")
        if m_adi not in musteri_gruplari:
          musteri_gruplari[m_adi] = []
        musteri_gruplari[m_adi].append(s)

      for m_adi, m_satislar in musteri_gruplari.items():
        with st.expander(
            f"🏷️ {m_adi} ({len(m_satislar)} Satış İşlemi)", expanded=False
        ):
          m_tablo = []
          for s in reversed(m_satislar):
            m_tablo.append({
                "No": s.get("no"),
                "Tarih": s.get("tarih"),
                "Ürün": s.get("urun"),
                "Adet": s.get("adet"),
                "Toplam Tutar": f"{s.get('tutar'):.2f} TL",
                "Ödeme": s.get("odeme"),
            })
          st.table(pd.DataFrame(m_tablo))
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
  st.header("💰 Kasa ve Nakit Bakiye Yönetimi")

  nakit_satislar_toplami = sum(
      s.get("tutar", 0) for s in veri["s"] if s.get("odeme") == "Nakit"
  )
  giderler_kasadan = sum(
      g.get("tutar", 0) for g in veri["g"] if g.get("kasadan_dus", True)
  )
  stok_kasadan = sum(
      a.get("adet", 0) * a.get("maliyet", 0)
      for alimlar in veri["u"].values()
      for a in alimlar
      if a.get("kasadan_dus", True)
  )

  net_kasa_bakiye = nakit_satislar_toplami - giderler_kasadan - stok_kasadan

  st.metric(
      "Kasa Mevcut Nakit Bakiyesi",
      f"{net_kasa_bakiye:.2f} TL",
      help=(
          "Nakit Satışlar - Kasadan Düşülen Giderler - Kasadan Düşülen Stok"
          " Alımları"
      ),
  )

  st.divider()
  st.subheader("📅 Tarih Bazlı Kasa ve Günlük Geçmiş İnceleme")
  kasa_tarih = st.date_input(
      "İncelemek İstediğiniz Tarihi Seçin",
      value=datetime.today(),
      key="kasa_tarih_secim",
  )
  secilen_kasa_tarih_str = kasa_tarih.strftime("%d.%m.%Y")

  g_satislar = [
      s for s in veri["s"] if s.get("tarih") == secilen_kasa_tarih_str
  ]
  g_giderler = [
      g for g in veri["g"] if g.get("tarih") == secilen_kasa_tarih_str
  ]

  g_ciro_dahil = sum(s.get("tutar", 0) for s in g_satislar)
  g_kar_dahil = sum(s.get("kar", 0) for s in g_satislar)
  g_toplam_gider = sum(g.get("tutar", 0) for g in g_giderler)

  kc1, kc2, kc3 = st.columns(3)
  with kc1:
    st.metric(f"{secilen_kasa_tarih_str} Ciro", f"{g_ciro_dahil:.2f} TL")
  with kc2:
    st.metric(f"{secilen_kasa_tarih_str} Kâr", f"{g_kar_dahil:.2f} TL")
  with kc3:
    st.metric(f"{secilen_kasa_tarih_str} Gider", f"{g_toplam_gider:.2f} TL")

  st.markdown("#### Bu Günde Satılan Ürünler")
  if g_satislar:
    st.table(pd.DataFrame(g_satislar))
  else:
    st.info(f"{secilen_kasa_tarih_str} tarihinde satış kaydı bulunmuyor.")

  st.markdown("#### Bu Günde Yapılan Giderler")
  if g_giderler:
    st.table(pd.DataFrame(g_giderler))
  else:
    st.info(f"{secilen_kasa_tarih_str} tarihinde gider kaydı bulunmuyor.")

# 5. GİDERLER
with tab5:
  st.header("💸 Gider Yönetimi (Maaş, Muhasebe vb.)")
  with st.form("gider_ekle_form"):
    g_tarih = st.text_input(
        "Gider Tarihi",
        value=datetime.now().strftime("%d.%m.%Y"),
        key="gider_tarih",
    )
    g_aciklama = st.text_input(
        "Gider Açıklaması / Türü",
        placeholder="Örn: İşçi Maaşı, Muhasebe Ücreti, Elektrik Faturası",
    )
    g_tutar = st.number_input(
        "Gider Tutarı (TL)", min_value=0.0, value=0.0, key="gider_tutar"
    )
    g_kasadan_dus = st.checkbox(
        "Bu gider ücreti kasanın bakiyesinden düşülsün", value=True
    )

    if st.form_submit_button("Gideri Kaydet"):
      if g_aciklama.strip() and g_tutar > 0:
        veri["g"].append({
            "tarih": g_tarih,
            "aciklama": g_aciklama.strip(),
            "tutar": g_tutar,
            "kasadan_dus": g_kasadan_dus,
        })
        veri_kaydet(veri)
        st.success(f"'{g_aciklama.strip()}' gideri başarıyla kaydedildi.")
        st.rerun()
      else:
        st.error("Lütfen geçerli bir açıklama ve 0'dan büyük tutar girin.")

  st.divider()
  st.subheader("📋 Kayıtlı Giderler Listesi")
  if veri["g"]:
    gider_tablo = []
    for idx, g in enumerate(reversed(veri["g"])):
      gider_tablo.append({
          "No": len(veri["g"]) - idx,
          "Tarih": g.get("tarih"),
          "Açıklama": g.get("aciklama"),
          "Tutar": f"{g.get('tutar'):.2f} TL",
          "Kasadan Düştü mü?": "Evet"
          if g.get("kasadan_dus", True)
          else "Hayır",
      })
    st.table(pd.DataFrame(gider_tablo))

    if st.button("Seçili Son Gideri Sil"):
      veri["g"].pop()
      veri_kaydet(veri)
      st.success("Son gider kaydı silindi.")
      st.rerun()
  else:
    st.info("Kayıtlı gider bulunmuyor.")

# 6. STOK LİSTESİ
with tab6:
  st.header("📦 Ürün ve Stok Yönetimi (Parti Bazlı Alım)")

  st.subheader("➕ Yeni Alım / Stok Ekle")
  with st.form("stok_ekle_form"):
    u_ad = st.text_input("Ürün Adı").strip().upper()
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
      alim_tarih = st.text_input(
          "Alım Tarihi",
          value=datetime.now().strftime("%d.%m.%Y"),
          key="alim_tarih",
      )
    with col_s2:
      u_adet = st.number_input("Adet", min_value=1, value=10, key="ekle_adet")
    with col_s3:
      u_kritik = st.number_input(
          "Kritik Eşik", min_value=0, value=5, key="ekle_kritik"
      )
    u_mal = st.number_input(
        "Birim Maliyet (TL)", min_value=0.0, key="ekle_mal"
    )
    stok_kasadan_dus = st.checkbox(
        "Bu stok alım ücreti kasadan düşülsün mü?", value=True, key="stok_kasa_cb"
    )

    if st.form_submit_button("Stok Girişini Kaydet"):
      if u_ad:
        if u_ad not in veri["u"]:
          veri["u"][u_ad] = []
        veri["u"][u_ad].append({
            "tarih": alim_tarih,
            "adet": u_adet,
            "maliyet": u_mal,
            "kritik": u_kritik,
            "kasadan_dus": stok_kasadan_dus,
        })
        veri_kaydet(veri)
        st.success(f"'{u_ad}' için yeni stok partisi eklendi.")
        st.rerun()

  st.divider()
  st.subheader("📋 Mevcut Stok Listesi (En Yeni Alım Üstte)")
  if veri["u"]:
    stok_listesi_tablo = []
    for u_adi, alimlar in veri["u"].items():
      for idx, alim in enumerate(reversed(alimlar)):
        if alim.get("adet", 0) > 0:
          stok_listesi_tablo.append({
              "Ürün Adı": u_adi,
              "Alım Tarihi": alim.get("tarih", "-"),
              "Adet": alim.get("adet", 0),
              "Kritik Eşik": alim.get("kritik", 5),
              "Birim Maliyet": f"{alim.get('maliyet', 0):.2f} TL",
              "Kasadan Düştü mü?": "Evet"
              if alim.get("kasadan_dus", True)
              else "Hayır",
              "Orijinal_Index": len(alimlar) - 1 - idx,
          })

    if stok_listesi_tablo:
      df_stok = pd.DataFrame(stok_listesi_tablo)
      st.table(df_stok.drop(columns=["Orijinal_Index"]))

      st.divider()
      st.subheader("✏️ Belirli Bir Stok Partisini Düzenle veya Sil")
      secenekler = [
          f"{row['Ürün Adı']} - Tarih: {row['Alım Tarihi']} - Adet: {row['Adet']} (Index: {row['Orijinal_Index']})"
          for row in stok_listesi_tablo
      ]
      secilen_parti = st.selectbox("Düzenlenecek / Silinecek Stok Partisi", secenekler)

      if secilen_parti:
        parcalar = secilen_parti.split(" (Index: ")
        u_adi = parcalar[0].split(" - Tarih: ")[0]
        orijinal_idx = int(parcalar[1].replace(")", ""))

        if u_adi in veri["u"] and len(veri["u"][u_adi]) > orijinal_idx:
          parti_bilgi = veri["u"][u_adi][orijinal_idx]

          with st.form("parti_duzenle_form"):
            d_tarih = st.text_input(
                "Parti Tarihi",
                value=parti_bilgi.get(
                    "tarih", datetime.now().strftime("%d.%m.%Y")
                ),
            )
            d_adet = st.number_input(
                "Adet", min_value=0, value=int(parti_bilgi.get("adet", 0))
            )
            d_kritik = st.number_input(
                "Kritik Eşik",
                min_value=0,
                value=int(parti_bilgi.get("kritik", 5)),
            )
            d_mal = st.number_input(
                "Birim Maliyet (TL)",
                min_value=0.0,
                value=float(parti_bilgi.get("maliyet", 0.0)),
            )

            col_p1, col_p2 = st.columns(2)
            with col_p1:
              guncelle_tik = st.form_submit_button(
                  "💾 Partiyi Güncelle", type="primary"
              )
            with col_p2:
              sil_tik = st.form_submit_button(
                  "🗑️ Bu Partiyi Sil", type="secondary"
              )

            if guncelle_tik:
              veri["u"][u_adi][orijinal_idx].update({
                  "tarih": d_tarih,
                  "adet": d_adet,
                  "maliyet": d_mal,
                  "kritik": d_kritik,
              })
              veri_kaydet(veri)
              st.success("Stok partisi güncellendi.")
              st.rerun()

            if sil_tik:
              veri["u"][u_adi].pop(orijinal_idx)
              if not veri["u"][u_adi]:
                del veri["u"][u_adi]
              veri_kaydet(veri)
              st.success("Stok partisi silindi.")
              st.rerun()
    else:
      st.info("Aktif stok bulunmuyor.")
  else:
    st.info("Kayıtlı ürün bulunmuyor.")

# 7. KRİTİK STOK
with tab7:
  st.header("⚠️ Kritik Stok Seviyeleri")
  kritik_liste = []
  for k, alimlar in veri["u"].items():
    toplam_adet = sum(a.get("adet", 0) for a in alimlar)
    esik = alimlar[-1].get("kritik", 5) if alimlar else 5
    if toplam_adet <= esik:
      kritik_liste.append(
          {"Ürün": k, "Toplam Mevcut Adet": toplam_adet, "Kritik Eşik": esik}
      )

  if kritik_liste:
    st.table(pd.DataFrame(kritik_liste))
  else:
    st.success("Kritik seviyede ürün bulunmuyor.")

# 8. RAPORLAR
with tab8:
  st.header("📊 Detaylı Finansal Raporlar")
  rapor_tarihi = st.date_input(
      "Rapor Tarihi Seçin", value=datetime.today(), key="rapor_tarih_secim"
  )
  secilen_tarih_str = rapor_tarihi.strftime("%d.%m.%Y")

  st.subheader(f"📅 {secilen_tarih_str} Tarihli Rapor Özeti")

  gunluk_satislar = [
      s for s in veri["s"] if s.get("tarih") == secilen_tarih_str
  ]
  gunluk_giderler = [
      g for g in veri["g"] if g.get("tarih") == secilen_tarih_str
  ]

  ciro_veresiye_dahil = sum(s.get("tutar", 0) for s in gunluk_satislar)
  ciro_veresiye_haric = sum(
      s.get("tutar", 0) for s in gunluk_satislar if s.get("odeme") != "Veresiye"
  )

  kar_veresiye_dahil = sum(s.get("kar", 0) for s in gunluk_satislar)
  kar_veresiye_haric = sum(
      s.get("kar", 0) for s in gunluk_satislar if s.get("odeme") != "Veresiye"
  )

  toplam_gider = sum(g.get("tutar", 0) for g in gunluk_giderler)

  c1, c2 = st.columns(2)
  with c1:
    st.metric("Günlük Ciro (Veresiye Dahil)", f"{ciro_veresiye_dahil:.2f} TL")
    st.metric("Günlük Ciro (Veresiye Hariç)", f"{ciro_veresiye_haric:.2f} TL")
  with c2:
    st.metric("Günlük Kâr (Veresiye Dahil)", f"{kar_veresiye_dahil:.2f} TL")
    st.metric("Günlük Kâr (Veresiye Hariç)", f"{kar_veresiye_haric:.2f} TL")

  st.metric("Günlük Toplam Giderler", f"{toplam_gider:.2f} TL")

  st.divider()
  st.subheader("📋 Seçilen Güne Ait Satışlar")
  if gunluk_satislar:
    st.table(pd.DataFrame(gunluk_satislar))
  else:
    st.info("Bu tarihte satış kaydı bulunmuyor.")

  st.subheader("📋 Seçilen Güne Ait Giderler")
  if gunluk_giderler:
    st.table(pd.DataFrame(gunluk_giderler))
  else:
    st.info("Bu tarihte gider kaydı bulunmuyor.")
