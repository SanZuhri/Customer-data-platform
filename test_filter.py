# app.py
import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker
from streamlit_condition_tree import condition_tree, config_from_dataframe, JsCode
import re # Import library regular expression

# Asumsikan file-file ini sudah ada
from database import engine
from models import Base, FilterTersimpan

# Inisialisasi: Buat tabel di database jika belum ada.
Base.metadata.create_all(bind=engine)

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Dashboard Analisis Penjualan",
    page_icon="📊",
    layout="wide"
)
st.title("📊 Dashboard Analisis Penjualan")
st.info(
    "Versi final dengan perbaikan untuk menangani kueri null pada Pandas."
)
st.markdown("---")


# --- FUNGSI DATABASE (Tidak Berubah) ---
Session = sessionmaker(bind=engine)

def save_filter_to_db(name: str, tree_dict: dict):
    session = Session()
    try:
        if session.query(FilterTersimpan).filter_by(nama_filter=name).first():
            st.warning(f"Nama filter '{name}' sudah ada.")
            return
        new_filter = FilterTersimpan(nama_filter=name, konfigurasi_json=tree_dict, dibuat_oleh="user_dashboard")
        session.add(new_filter)
        session.commit()
        st.toast(f"✅ Filter '{name}' berhasil disimpan!", icon="💾")
    finally:
        session.close()

def load_all_filter_names():
    session = Session()
    try:
        return [f[0] for f in session.query(FilterTersimpan.nama_filter).order_by(FilterTersimpan.nama_filter).all()]
    finally:
        session.close()

def get_filter_config_by_name(name: str) -> dict | None:
    session = Session()
    try:
        result = session.query(FilterTersimpan.konfigurasi_json).filter_by(nama_filter=name).first()
        return result[0] if result else None
    finally:
        session.close()

# --- PEMUATAN DATA & LOGIKA INTI ---
@st.cache_data(ttl=600)
def load_data_from_db():
    query = """
    SELECT
        t.id AS id_transaksi, t.waktu_transaksi, tk.nama_toko, tk.kota,
        kr.nama_karyawan, kr.posisi AS posisi_karyawan, p.nama_produk,
        p.kategori AS kategori_produk, p.harga_jual, dt.jumlah AS jumlah_item,
        dt.harga_saat_transaksi, (dt.jumlah * dt.harga_saat_transaksi) AS total_harga_item,
        m.nama_member, m.tanggal_bergabung AS tanggal_join_member
    FROM transaksi t
    JOIN detail_transaksi dt ON t.id = dt.id_transaksi
    JOIN produk p ON dt.id_produk = p.id
    JOIN toko tk ON t.id_toko = tk.id
    JOIN karyawan kr ON t.id_karyawan = kr.id
    LEFT JOIN member m ON t.id_member = m.id;
    """
    with engine.connect() as connection:
        df = pd.read_sql(query, connection)
    df['waktu_transaksi'] = pd.to_datetime(df['waktu_transaksi']).dt.tz_localize(None)
    df['tanggal_join_member'] = pd.to_datetime(df['tanggal_join_member']).dt.tz_localize(None)
    # Ganti nama kolom dengan spasi agar aman untuk .query()
    df.columns = [c.replace(' ', '_') for c in df.columns]
    return df

# **LANGKAH KUNCI 1: Fungsi untuk Memperbaiki Kueri**
def fix_query_for_pandas(query_string: str) -> str:
    """
    Mengonversi sintaks null dari gaya SQL ke gaya Pandas menggunakan regular expression.
    Contoh: `(nama_kolom == null)` menjadi `(nama_kolom.isnull())`
             `(`Nama Kolom` != null)` menjadi `(`Nama Kolom`.notnull())`
    """
    # Mencari pola: (opsional spasi)(nama kolom)(opsional spasi)(operator)(opsional spasi)(null)
    # Nama kolom bisa berupa kata biasa atau diapit backtick
    pattern_eq = re.compile(r"([\w`_]+)\s*==\s*null")
    pattern_ne = re.compile(r"([\w`_]+)\s*!=\s*null")
    
    # Lakukan penggantian
    fixed_query = pattern_eq.sub(r"\1.isnull()", query_string)
    fixed_query = pattern_ne.sub(r"\1.notnull()", fixed_query)
    
    return fixed_query

# Blok utama aplikasi
try:
    df_initial = load_data_from_db()
except Exception as e:
    st.error(f"Gagal terhubung atau mengambil data dari database: {e}")
    st.stop()

if df_initial.empty:
    st.warning("Tidak ada data transaksi di database. Jalankan `data_generator.py` untuk mengisinya.")
    st.stop()

# Konfigurasi `streamlit-condition-tree` (sudah benar dari sebelumnya)
config = config_from_dataframe(df_initial)
config['operators'] = {
    **config.get('operators', {}),
    'is_null': {'label': 'Is Null', 'cardinality': 0, 'sqlFormatFunc': JsCode("function(f) { return `${f}.isnull()`; }")},
    'is_not_null': {'label': 'Is Not Null', 'cardinality': 0, 'sqlFormatFunc': JsCode("function(f) { return `${f}.notnull()`; }")}
}
for f_type in config.get('types', {}):
    if 'operators' not in config['types'][f_type]:
        config['types'][f_type]['operators'] = []
    config['types'][f_type]['operators'].extend(['is_null', 'is_not_null'])
select_fields = {'nama_toko': 'select', 'kota': 'select', 'posisi_karyawan': 'select', 'kategori_produk': 'select'}
for field, f_type in select_fields.items():
    if field in config['fields']:
        config['fields'][field]['type'] = f_type
        unique_values = df_initial[field].dropna().unique().tolist()
        config['fields'][field]['fieldSettings'] = {'listValues': unique_values}

# Manajemen State (Tidak Berubah)
if 'filter_version' not in st.session_state:
    st.session_state.filter_version = 0
if 'active_tree' not in st.session_state:
    st.session_state.active_tree = None

# UI (Tidak Berubah)
with st.expander("📁 Simpan atau Muat Konfigurasi Filter", expanded=True):
    col_load, col_save = st.columns(2)
    with col_load:
        st.subheader("Muat Filter")
        all_names = load_all_filter_names()
        selected_name = st.selectbox("Pilih filter untuk diterapkan", options=[""] + all_names)
        if st.button("🚀 Terapkan Filter", use_container_width=True):
            if selected_name:
                config_from_db = get_filter_config_by_name(selected_name)
                if config_from_db:
                    st.session_state.filter_version += 1
                    st.session_state.active_tree = config_from_db
                    st.rerun()
            else:
                st.warning("Pilih nama filter terlebih dahulu.")
    with col_save:
        st.subheader("Simpan Filter Saat Ini")
        with st.form("save_form", clear_on_submit=True):
            filter_name = st.text_input("Beri nama untuk filter ini")
            tree_key_to_save = f"tree_v{st.session_state.filter_version}"
            current_tree_value = st.session_state.get(tree_key_to_save)
            if st.form_submit_button("💾 Simpan Filter", use_container_width=True):
                if filter_name and current_tree_value and current_tree_value.get('children'):
                    save_filter_to_db(filter_name, current_tree_value)
                else:
                    st.warning("Nama filter tidak boleh kosong dan harus ada aturan yang aktif.")
st.markdown("---")
st.header("Panel Pembuat Filter")
dynamic_key = f"tree_v{st.session_state.filter_version}"
query_string = condition_tree(config=config, placeholder="Buat aturan atau muat filter...", tree=st.session_state.active_tree, key=dynamic_key, return_type='queryString')
if dynamic_key in st.session_state:
    st.session_state.active_tree = st.session_state[dynamic_key]

# --- TAMPILKAN HASIL ---
st.markdown("---")
st.header("Hasil Analisis")

if query_string:
    # **LANGKAH KUNCI 2: Terapkan Perbaikan Sebelum Menjalankan Query**
    fixed_query = fix_query_for_pandas(query_string)
    
    st.subheader("Kueri Asli & yang Diperbaiki:")
    st.code(f"Asli: {query_string}\nDiperbaiki: {fixed_query}", language="text")
    
    st.subheader("Data Hasil Filter:")
    try:
        # Gunakan kueri yang sudah diperbaiki
        df_filtered = df_initial.query(fixed_query)
        st.dataframe(df_filtered)
        st.success(f"Menampilkan {len(df_filtered):,} dari {len(df_initial):,} baris data.")
    except Exception as e:
        st.error(f"Kueri filter tidak valid untuk Pandas: {e}")
else:
    st.subheader("Data Awal (Tidak ada filter yang diterapkan)")
    st.dataframe(df_initial)