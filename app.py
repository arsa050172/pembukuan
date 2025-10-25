import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import date
st.set_page_config(layout="wide")

# ----------------------------
# 🔧 KONFIGURASI SUPABASE
# ----------------------------
SUPABASE_URL = "https://rimeaufssicbkjbbwgul.supabase.co"   # Ganti dengan URL proyek Supabase kamu
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJpbWVhdWZzc2ljYmtqYmJ3Z3VsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjEwNzk2NjcsImV4cCI6MjA3NjY1NTY2N30.-rZuJajqEwbf0F9hWC-iPIFf0lDtCGEcm8Zwt6FdXv8"                  # Ganti dengan kunci API Supabase kamu
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------------------
# 🎨 STYLING MODERN
# ----------------------------
st.markdown("""
    <style>
    body {
        background-color: #f4f6f8;
    }
    .main {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .stButton>button {
        background-color: #0078ff;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #005fcc;
        transform: scale(1.05);
    }
    .delete-button>button {
        background-color: #e74c3c !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Aplikasi Pembukuan Sederhana")
st.caption("Kelola data keuangan dengan tampilan modern dan interaktif.")

# ----------------------------
# 🧩 FUNGSI CRUD
# ----------------------------
def create_data(tanggal, keterangan, debet, kredit):
    # Simpan data awal
    result = supabase.table("pembukuan").insert({
        "tanggal": str(tanggal),
        "keterangan": keterangan,
        "debet": debet,
        "kredit": kredit
    }).execute()

    # Hitung ulang saldo berjalan dan update semua baris
    data = read_data()
    for row in data:
        supabase.table("pembukuan").update({
            "total_saldo": row["total_saldo"]
        }).eq("id", row["id"]).execute()

def read_data():
    data = supabase.table("pembukuan").select("*").order("tanggal", desc=False).execute()
    if not data.data:
        return []

    df = pd.DataFrame(data.data)

    # Pastikan kolom numerik tidak None
    df["debet"] = df["debet"].fillna(0)
    df["kredit"] = df["kredit"].fillna(0)

    # Hitung saldo berjalan (running balance)
    df["total_saldo"] = (df["debet"] - df["kredit"]).cumsum()

    return df.to_dict(orient="records")

    
def update_data(record_id, tanggal, keterangan, debet, kredit, total_saldo):
    supabase.table("pembukuan").update({
        "tanggal": str(tanggal),
        "keterangan": keterangan,
        "debet": debet,
        "kredit": kredit,
        "total_saldo": total_saldo
    }).eq("id", record_id).execute()

def delete_data(record_id):
    supabase.table("pembukuan").delete().eq("id", record_id).execute()

# ----------------------------
# 🧭 MENU NAVIGASI
# ----------------------------
menu = st.sidebar.radio(
    "Navigasi",
    ["📋 Lihat Data", "➕ Tambah Data", "✏️ Edit Data", "🗑️ Hapus Data"]
)

# ----------------------------
# 📊 LIHAT DATA
# ----------------------------
if menu == "📋 Lihat Data":
    st.subheader("📘 Laporan Pembukuan")
    data = read_data()
    if data:
        df = pd.DataFrame(data)
        df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date
        df.index = range(1, len(df) + 1)  # 🔢 Mulai nomor dari 1
        st.dataframe(df, use_container_width=True)

        # Total debet, kredit, saldo akhir
        # Hitung total debet, kredit, dan saldo keseluruhan
        df["saldo"] = df["debet"] - df["kredit"]
  
        total_debet = df["debet"].sum()
        total_kredit = df["kredit"].sum()
        saldo_akhir = df["total_saldo"].iloc[-1]

        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 2])
        col1.metric("Total Debet", f"Rp {total_debet:,.2f}")
        col2.metric("Total Kredit", f"Rp {total_kredit:,.2f}")
        col3.metric("Saldo Akhir", f"Rp {saldo_akhir:,.2f}")

    else:
        st.info("Belum ada data pembukuan.")

# ----------------------------
# ➕ TAMBAH DATA
# ----------------------------
elif menu == "➕ Tambah Data":
    st.subheader("Tambah Data Pembukuan")
    tanggal = st.date_input("Tanggal", date.today())
    keterangan = st.text_input("Keterangan")
    debet = st.number_input("Debet", min_value=0.0, format="%.2f")
    kredit = st.number_input("Kredit", min_value=0.0, format="%.2f")
    ## total_saldo = st.number_input("total saldo", min_value=0.0, format="%.2f")

    if st.button("💾 Simpan Data"):
        if keterangan:
            create_data(tanggal, keterangan, debet, kredit)
            st.success("✅ Data berhasil disimpan!")
        else:
            st.warning("⚠️ Keterangan tidak boleh kosong.")

# ----------------------------
# ✏️ EDIT DATA
# ----------------------------
elif menu == "✏️ Edit Data":
    st.subheader("Edit Data Pembukuan")
    data = read_data()
    if data:
        selected = st.selectbox("Pilih Data untuk Diedit", options=data, format_func=lambda x: f"{x['id']} - {x['keterangan']}")
        tanggal = st.date_input("Tanggal", pd.to_datetime(selected["tanggal"]))
        keterangan = st.text_input("Keterangan", selected["keterangan"])
        debet = st.number_input("Debet", min_value=0.0, value=float(selected["debet"]), format="%.2f")
        kredit = st.number_input("Kredit", min_value=0.0, value=float(selected["kredit"]), format="%.2f")
        total_saldo = st.number_input("total_saldo", min_value=0.0, value=float(selected["total_saldo"]), format="%.2f")
        
        if st.button("🔄 Update Data"):
            update_data(selected["id"], tanggal, keterangan, debet, kredit, total_saldo)
            st.success("✅ Data berhasil diperbarui!")
    else:
        st.info("Belum ada data untuk diedit.")

# ----------------------------
# 🗑️ HAPUS DATA
# ----------------------------
elif menu == "🗑️ Hapus Data":
    st.subheader("Hapus Data Pembukuan")
    data = read_data()
    if data:
        selected = st.selectbox("Pilih Data untuk Dihapus", options=data, format_func=lambda x: f"{x['id']} - {x['keterangan']}")
        if st.button("🗑️ Hapus Data", key="delete", help="Klik untuk menghapus data ini"):
            delete_data(selected["id"])
            st.success(f"🗑️ Data '{selected['keterangan']}' berhasil dihapus.")
    else:
        st.info("Belum ada data untuk dihapus.")


