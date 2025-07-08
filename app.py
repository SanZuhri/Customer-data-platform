# app.py
import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker
from streamlit_condition_tree import condition_tree, config_from_dataframe, JsCode
import re
from datetime import datetime

# Asumsikan file-file ini sudah ada
from database import engine
from models import Base, FilterTersimpan

# Inisialisasi: Buat tabel di database jika belum ada.
Base.metadata.create_all(bind=engine)

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Customer Data Platform",
    page_icon="⚡",
    layout="wide"
)

# --- CSS Kustom untuk Tampilan (Opsional, tapi mempercantik) ---
st.markdown("""
<style>
    /* Mengurangi padding atas dari halaman */
    .block-container {
        padding-top: 2rem;
    }
    /* Mengatur gaya tombol utama */
    .stButton>button {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNGSI-FUNGSI DATABASE ---
Session = sessionmaker(bind=engine)

def save_or_update_filter(name: str, tree_dict: dict, old_name: str = None):
    session = Session()
    try:
        # Jika old_name ada, berarti kita sedang mengedit
        if old_name and old_name != name:
            # Hapus yang lama jika nama berubah
            session.query(FilterTersimpan).filter_by(nama_filter=old_name).delete()

        # Buat atau update entri
        existing_filter = session.query(FilterTersimpan).filter_by(nama_filter=name).first()
        if existing_filter:
            existing_filter.konfigurasi_json = tree_dict
            existing_filter.dibuat_pada = datetime.now()
        else:
            new_filter = FilterTersimpan(nama_filter=name, konfigurasi_json=tree_dict, dibuat_oleh="user_dashboard")
            session.add(new_filter)
        
        session.commit()
        st.toast(f"✅ Segment '{name}' berhasil disimpan!", icon="💾")
        return True
    except Exception as e:
        session.rollback()
        st.error(f"Gagal menyimpan filter: {e}")
        return False
    finally:
        session.close()

def load_all_filters():
    session = Session()
    try:
        # Ambil semua data yang dibutuhkan untuk direktori
        return session.query(FilterTersimpan).order_by(FilterTersimpan.dibuat_pada.desc()).all()
    finally:
        session.close()

def get_filter_config_by_name(name: str) -> dict | None:
    session = Session()
    try:
        result = session.query(FilterTersimpan.konfigurasi_json).filter_by(nama_filter=name).first()
        return result[0] if result else None
    finally:
        session.close()

def delete_filter_by_name(name: str):
    session = Session()
    try:
        session.query(FilterTersimpan).filter_by(nama_filter=name).delete()
        session.commit()
        st.toast(f"🗑️ Segment '{name}' berhasil dihapus.")
        return True
    except Exception as e:
        session.rollback()
        st.error(f"Gagal menghapus filter: {e}")
        return False
    finally:
        session.close()


# --- FUNGSI PEMUATAN DATA & PERSIAPAN ---
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
    df.columns = [c.replace(' ', '_') for c in df.columns]
    return df

def get_tree_config():
    """Mempersiapkan config untuk streamlit-condition-tree."""
    df = load_data_from_db()
    config = config_from_dataframe(df)
    config['operators'] = {
        **config.get('operators', {}),
        'is_null': {'label': 'is null', 'cardinality': 0, 'sqlFormatFunc': JsCode("function(f) { return `${f}.isnull()`; }")},
        'is_not_null': {'label': 'is not null', 'cardinality': 0, 'sqlFormatFunc': JsCode("function(f) { return `${f}.notnull()`; }")}
    }
    for f_type in config.get('types', {}):
        if 'operators' not in config['types'][f_type]: config['types'][f_type]['operators'] = []
        config['types'][f_type]['operators'].extend(['is_null', 'is_not_null'])
    select_fields = {'nama_toko': 'select', 'kota': 'select', 'posisi_karyawan': 'select', 'kategori_produk': 'select'}
    for field, f_type in select_fields.items():
        if field in config['fields']:
            config['fields'][field]['type'] = f_type
            unique_values = df[field].dropna().unique().tolist()
            config['fields'][field]['fieldSettings'] = {'listValues': unique_values}
    return config

def fix_query_for_pandas(query_string: str) -> str:
    pattern_eq = re.compile(r"([\w`_]+)\s*==\s*null")
    pattern_ne = re.compile(r"([\w`_]+)\s*!=\s*null")
    fixed_query = pattern_eq.sub(r"\1.isnull()", query_string)
    fixed_query = pattern_ne.sub(r"\1.notnull()", fixed_query)
    return fixed_query


# --- MANAJEMEN STATE APLIKASI ---
# Mengontrol tab mana yang aktif
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Segment Directory"
# Menyimpan nama segmen yang sedang diedit
if "editing_segment_name" not in st.session_state:
    st.session_state.editing_segment_name = None
# Untuk strategi 'Key-Change' pada condition tree
if 'filter_version' not in st.session_state:
    st.session_state.filter_version = 0
if 'active_tree_config' not in st.session_state:
    st.session_state.active_tree_config = None


# --- HEADER UTAMA ---
st.sidebar.title("LOGO")
st.sidebar.write("CUSTOMER DATA PLATFORM")
profile_button = st.sidebar.button("Profil", use_container_width=True)


# --- STRUKTUR TAB ---
tab1, tab2, tab3 = st.tabs(["Segment Directory", "Segment Builder", "Campaign Builder"])


# ======================================================================================
# --- TAB 1: SEGMENT DIRECTORY ---
# ======================================================================================
with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.text_input("Search", placeholder="Search Segments", label_visibility="collapsed")
    with col2:
        if st.button("＋ Create New Segment", type="primary", use_container_width=True):
            # Reset state dan pindah ke tab builder
            st.session_state.editing_segment_name = None
            st.session_state.active_tree_config = None
            st.session_state.filter_version += 1 # Ganti key agar tree kosong
            st.session_state.active_tab = "Segment Builder"
            st.rerun()

    st.header("Saved Segments")
    st.markdown("---")
    
    # Header tabel
    col_h1, col_h2, col_h3, col_h4 = st.columns([0.5, 4, 2, 1])
    col_h1.write("**#**")
    col_h2.write("**Segment Name**")
    col_h3.write("**Last Modified**")
    col_h4.write("**Actions**")

    # Konten tabel
    all_filters = load_all_filters()
    if not all_filters:
        st.info("No segments saved yet. Click 'Create New Segment' to start.")
    else:
        for i, f in enumerate(all_filters):
            col_d1, col_d2, col_d3, col_d4 = st.columns([0.5, 4, 2, 1])
            col_d1.write(f"**{i+1}**")
            col_d2.write(f.nama_filter)
            col_d3.write(f.dibuat_pada.strftime("%d-%m-%Y"))
            
            # Kolom untuk tombol action
            action_cols = col_d4.columns([1, 1])
            if action_cols[0].button("✏️", key=f"edit_{f.nama_filter}", help="Edit Segment"):
                st.session_state.editing_segment_name = f.nama_filter
                st.session_state.active_tree_config = get_filter_config_by_name(f.nama_filter)
                st.session_state.filter_version += 1 # Ganti key untuk memuat tree baru
                st.session_state.active_tab = "Segment Builder"
                st.rerun()

            if action_cols[1].button("🗑️", key=f"del_{f.nama_filter}", help="Delete Segment"):
                delete_filter_by_name(f.nama_filter)
                st.rerun()
    st.markdown("---")


# ======================================================================================
# --- TAB 2: SEGMENT BUILDER ---
# ======================================================================================
with tab2:
    if st.session_state.active_tab != "Segment Builder":
        st.info("Pilih 'Create New Segment' atau klik ikon edit ✏️ dari 'Segment Directory' untuk memulai.")
    else:
        # Menyiapkan data dan config
        df = load_data_from_db()
        tree_config = get_tree_config()

        # Header dinamis
        is_editing = st.session_state.editing_segment_name is not None
        if is_editing:
            st.header(f"Edit Segment: {st.session_state.editing_segment_name}")
        else:
            st.header("Create a New Segment")
        st.markdown("---")
        
        # UI Builder
        builder_cols = st.columns([2.5, 1.5])
        with builder_cols[0]:
            segment_name = st.text_input(
                "Segment Name", 
                value=st.session_state.editing_segment_name or "",
                key="segment_name_input"
            )
            
            st.write("**Include sales when:**")
            
            dynamic_key = f"tree_v{st.session_state.filter_version}"
            query_string = condition_tree(
                config=tree_config,
                tree=st.session_state.active_tree_config,
                key=dynamic_key,
                return_type='queryString'
            )
            # Sinkronisasi balik
            if dynamic_key in st.session_state:
                st.session_state.active_tree_config = st.session_state[dynamic_key]

        # Tombol kembali dan simpan
        action_cols = st.columns(6)
        if action_cols[0].button("Back to Directory", use_container_width=True):
            st.session_state.active_tab = "Segment Directory"
            st.rerun()
        
        if action_cols[1].button("💾 Save", type="primary", use_container_width=True):
            if not segment_name:
                st.warning("Segment Name is required.")
            else:
                tree_to_save = st.session_state.get(dynamic_key)
                if save_or_update_filter(segment_name, tree_to_save, st.session_state.editing_segment_name):
                    # Kembali ke direktori setelah menyimpan
                    st.session_state.active_tab = "Segment Directory"
                    st.rerun()

        # Placeholder untuk chart
        with builder_cols[1]:
            st.subheader("ESTIMATED TOTAL SALES")
            # ... logika untuk chart bisa ditambahkan di sini ...
            st.image("https://i.imgur.com/4s2Z5z4.png") # Menggunakan gambar placeholder

# ======================================================================================
# --- TAB 3: CAMPAIGN BUILDER ---
# ======================================================================================
with tab3:
    st.header("Campaign Builder")
    st.info("Fitur ini sedang dalam pengembangan.")