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

st.markdown(
    "<h1 style='text-align: center;'>🌈 GÖKKUŞAĞI"
    " TEMİZLİK VE AMBALAJ - Stok & Finans Yönetimi</h1>",
    unsafe_allow_html=True,
)
st.divider()

# Yatay sekme tanımlamaları
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Sepet & Satış",
    "Stok",
    "Kasa",
    "Veresiye",
    "Raporlar",
])

with tab1:
  st.header("Sepet ve Toplu Satış Paneli")
  # Tarih ve müşteri alanları
  col1, col2 = st.columns([2, 1])
  with col1:
    tarih = st.date_input("Tarih", value=datetime.today())
  with col2:
    st.write("")
    if st.button("Bugün"):
      pass

  musteri = st.text_input("Müşteri / Firma", value="GENEL MÜŞTERİ")

  # Ürün ve sepet işlemleri buraya gelecek
  st.info("Sepet ve satış ekranı bileşenleri bu sekme altındadır.")

with tab2:
  st.header("Stok Yönetimi")
  st.info("Stok listesi ve kritik stok takibi bu sekme altındadır.")

with tab3:
  st.header("Kasa İşlemleri")
  st.info("Kasa gelir/gider takibi bu sekme altındadır.")

with tab4:
  st.header("Veresiye Defteri")
  st.info("Müşteri borç ve alacak takibi bu sekme altındadır.")

with tab5:
  st.header("Finansal Raporlar")
  st.info("Ciro, satış özetleri ve raporlar bu sekme altındadır.")