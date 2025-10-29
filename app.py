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
st.caption("Transaksi uang masuk dan keluar.")

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

menu = st.sidebar.radio(
    "Navigasi",
    [
        "📋 Lihat Data",
        "📆 Lihat Data Periodik",
        "📅 Lihat Data Per-Tahun",
        "➕ Tambah Data",
        "✏️ Edit Data",
        "🗑️ Hapus Data"
    ]
)

# ----------------------------
# 📊 LIHAT DATA
# ----------------------------
if menu == "📋 Lihat Data":
    st.subheader("📘 Laporan Pembukuan")
    data = read_data()

    if data:
        df = pd.DataFrame(data)

        # --- 1️⃣ Ubah tipe data tanggal ---
        if "tanggal" in df.columns:
            df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date

        # --- 2️⃣ Hitung total sebelum rename ---
        total_debet = df["debet"].sum()
        total_kredit = df["kredit"].sum()
        saldo_akhir = df["total_saldo"].iloc[-1]

        # --- 3️⃣ Format angka ke Rupiah sebelum rename ---
        df["debet"] = df["debet"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
        df["kredit"] = df["kredit"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
        df["total_saldo"] = df["total_saldo"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

             
        # --- 4️⃣ Rename kolom agar tampil lebih rapi ---
        df.rename(columns={
            "id": "No Trans",
            "created_at": "Tanggal Dibuat",
            "tanggal": "Tanggal Transaksi",
            "keterangan": "Deskripsi",
            "debet": "Uang Masuk",
            "kredit": "Uang Keluar",
            "total_saldo": "Saldo Akhir"
        }, inplace=True)
       
        # --- 5️⃣ Tampilkan tabel dan kolom nomor urut ---
        # df.index = range(1, len(df) + 1)
        # df.index.name = "Nomor"
        # st.dataframe(df, use_container_width=True)
                # --- 5️⃣ Tampilkan tabel ---
        df.index = range(1, len(df) + 1)
        df.index.name = "Nomor"

        # --- 5️⃣ Tampilkan tabel ---
        df.index = range(1, len(df) + 1)
        df.index.name = "Nomor"

        # --- 5️⃣ Tampilkan tabel dari dataframe hasil supabase ---
        df.index = range(1, len(df) + 1)
        df.index.name = "Nomor"

        st.dataframe(df, use_container_width=True)

        # st.dataframe(df, use_container_width=True)

        # --- 6️⃣ Tampilkan total di bawah tabel ---
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 2])
        col1.metric("Total Uang Masuk", f"Rp {total_debet:,.0f}".replace(",", "."))
        col2.metric("Total Uang Keluar", f"Rp {total_kredit:,.0f}".replace(",", "."))
        col3.metric("Saldo Akhir", f"Rp {saldo_akhir:,.0f}".replace(",", "."))
    else:
        st.info("Belum ada data pembukuan.")
# -------------------------
# LIHAT DATA PERIODIK
# LIHAT DATA PERIODIK
elif menu == "📆 Lihat Data Periodik":
    st.subheader("📆 Laporan Data Periodik")
    st.caption("Pilih rentang tanggal untuk menampilkan transaksi.")

    start_date = st.date_input("Dari tanggal")
    end_date = st.date_input("Sampai tanggal")

    if st.button("🔍 Tampilkan Data"):
        data = read_data()
        if data:
            df = pd.DataFrame(data)
            df["tanggal"] = pd.to_datetime(df["tanggal"]).dt.date

            filtered_df = df[(df["tanggal"] >= start_date) & (df["tanggal"] <= end_date)]

            if not filtered_df.empty:
                # Format kolom numerik ke Rupiah
                filtered_df["debet"] = filtered_df["debet"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
                filtered_df["kredit"] = filtered_df["kredit"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
                filtered_df["total_saldo"] = filtered_df["total_saldo"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

                # Rename kolom agar sama seperti "Lihat Data"
                filtered_df.rename(columns={
                    "id": "No Trans",
                    "created_at": "Tanggal Dibuat",
                    "tanggal": "Tanggal Transaksi",
                    "keterangan": "Deskripsi",
                    "debet": "Uang Masuk",
                    "kredit": "Uang Keluar",
                    "total_saldo": "Saldo Akhir"
                }, inplace=True)

                # Tambahkan nomor urut
                filtered_df.index = range(1, len(filtered_df) + 1)
                filtered_df.index.name = "Nomor"

                # Tampilkan tabel
                st.dataframe(filtered_df, use_container_width=True)

                # Dapatkan saldo akhir periode sebelumnya
                saldo_akhir_sebelumnya = 0
                # Filter data sebelum start_date untuk cari saldo akhir terakhir sebelum periode
                prev_df = df[df["tanggal"] < start_date]
                if not prev_df.empty:
                    saldo_akhir_sebelumnya = prev_df["total_saldo"].iloc[-1]

                # Tampilkan keterangan saldo akhir periode sebelumnya di bawah tabel
                st.markdown(f"**SALDO AKHIR PERIODE SEBELUMNYA:** Rp {saldo_akhir_sebelumnya:,.0f}".replace(",", "."))

                # Hitung total untuk periode yang dipilih (gunakan filtered_df asli tanpa format string)
                total_debet = df[(df["tanggal"] >= start_date) & (df["tanggal"] <= end_date)]["debet"].sum()
                total_kredit = df[(df["tanggal"] >= start_date) & (df["tanggal"] <= end_date)]["kredit"].sum()
                saldo_akhir = df[(df["tanggal"] >= start_date) & (df["tanggal"] <= end_date)]["total_saldo"].iloc[-1]

                # Tampilkan total di bawah keterangan saldo akhir periode sebelumnya
                st.markdown("---")
                col1, col2, col3 = st.columns([2, 2, 2])
                col1.metric("Total Uang Masuk", f"Rp {total_debet:,.0f}".replace(",", "."))
                col2.metric("Total Uang Keluar", f"Rp {total_kredit:,.0f}".replace(",", "."))
                col3.metric("Saldo Akhir", f"Rp {saldo_akhir:,.0f}".replace(",", "."))
            else:
                st.warning("Tidak ada transaksi pada periode tersebut.")
        else:
            st.info("Belum ada data pembukuan.")

#--------------------------
# LIHAT DATA PER-TAHUN
elif menu == "📅 Lihat Data Per-Tahun":
    st.subheader("📅 Laporan Data Tahunan (Rekap per Bulan)")
    st.caption("Pilih tahun untuk melihat total Debet, Kredit, dan Saldo Akhir per bulan.")

    data = read_data()
    if data:
        df = pd.DataFrame(data)
        df["tanggal"] = pd.to_datetime(df["tanggal"])
        df["tahun"] = df["tanggal"].dt.year
        df["bulan"] = df["tanggal"].dt.month

        tahun_tersedia = sorted(df["tahun"].unique(), reverse=True)
        selected_year = st.selectbox("Pilih Tahun", tahun_tersedia)

        # Filter data berdasarkan tahun yang dipilih
        filtered_df = df[df["tahun"] == selected_year]

        if not filtered_df.empty:
            # Rekap per bulan
            monthly_summary = (
                filtered_df.groupby("bulan")
                .agg({
                    "debet": "sum",
                    "kredit": "sum"
                })
                .reset_index()
                .sort_values("bulan")
            )

            # Hitung saldo akhir berjalan per bulan
            monthly_summary["saldo_akhir"] = (monthly_summary["debet"] - monthly_summary["kredit"]).cumsum()

            # Tambahkan nama bulan (dalam Bahasa Indonesia)
            nama_bulan = {
                1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
                5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
                9: "September", 10: "Oktober", 11: "November", 12: "Desember"
            }
            monthly_summary["Deskripsi"] = monthly_summary["bulan"].map(nama_bulan)

            # Format angka ke Rupiah
            monthly_summary["debet"] = monthly_summary["debet"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            monthly_summary["kredit"] = monthly_summary["kredit"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
            monthly_summary["saldo_akhir"] = monthly_summary["saldo_akhir"].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

            # Rapikan kolom
            monthly_summary = monthly_summary.rename(columns={
                "debet": "Uang Masuk",
                "kredit": "Uang Keluar",
                "saldo_akhir": "Saldo Akhir"
            })[["Deskripsi", "Uang Masuk", "Uang Keluar", "Saldo Akhir"]]

            # Tampilkan tabel
            monthly_summary.index = range(1, len(monthly_summary) + 1)
            monthly_summary.index.name = "No"
            st.dataframe(monthly_summary, use_container_width=True)

            # Tampilkan total akhir
            total_debet = filtered_df["debet"].sum()
            total_kredit = filtered_df["kredit"].sum()
            saldo_akhir = monthly_summary["Saldo Akhir"].iloc[-1]

            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Uang Masuk", f"Rp {total_debet:,.0f}".replace(",", "."))
            col2.metric("Total Uang Keluar", f"Rp {total_kredit:,.0f}".replace(",", "."))
            col3.metric("Saldo Akhir Tahun", saldo_akhir)

        else:
            st.warning(f"Tidak ada transaksi di tahun {selected_year}.")
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