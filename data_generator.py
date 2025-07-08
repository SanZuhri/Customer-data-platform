# data_generator.py
import pandas as pd
import random
import numpy as np
from faker import Faker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from database import engine
from datetime import datetime, time, timedelta

# Inisialisasi Faker untuk data Indonesia
fake = Faker('id_ID')
Session = sessionmaker(bind=engine)

def clear_all_data():
    """Membersihkan semua data dari tabel dengan urutan yang benar untuk menghindari error foreign key."""
    print("Membersihkan data lama dari database...")
    with engine.connect() as connection:
        with connection.begin():
            connection.execute(text('TRUNCATE TABLE detail_transaksi, stok_gudang RESTART IDENTITY CASCADE;'))
            connection.execute(text('TRUNCATE TABLE transaksi RESTART IDENTITY CASCADE;'))
            connection.execute(text('TRUNCATE TABLE karyawan RESTART IDENTITY CASCADE;'))
            connection.execute(text('TRUNCATE TABLE member RESTART IDENTITY CASCADE;'))
            connection.execute(text('TRUNCATE TABLE produk RESTART IDENTITY CASCADE;'))
            connection.execute(text('TRUNCATE TABLE toko RESTART IDENTITY CASCADE;'))
    print("Data lama berhasil dibersihkan.")


def generate_master_data():
    """Membuat dan menyimpan data master (Toko, Karyawan, Produk, Member)."""
    print("Membuat data master...")
    
    # 1. Toko
    toko_data = []
    kota_cabang = ['Bandung', 'Jakarta Selatan', 'Surabaya', 'Yogyakarta', 'Semarang']
    for i, kota in enumerate(kota_cabang):
        for j in range(1, 4): # 3 toko per kota
            toko_data.append({
                'id': len(toko_data) + 1,
                'nama_toko': f'Alfamart {kota.split()[0]} {j}',
                'alamat': fake.address(),
                'kota': kota
            })
    df_toko = pd.DataFrame(toko_data)

    # 2. Karyawan
    karyawan_data = []
    for id_toko in df_toko['id']:
        karyawan_data.append({ 'nama_karyawan': fake.name(), 'posisi': 'Kepala Toko', 'id_toko': id_toko })
        for _ in range(random.randint(3, 5)):
            karyawan_data.append({ 'nama_karyawan': fake.name(), 'posisi': random.choice(['Kasir', 'Pramuniaga']), 'id_toko': id_toko })
    df_karyawan = pd.DataFrame(karyawan_data).reset_index().rename(columns={'index': 'id'})
    df_karyawan['id'] += 1


    # 3. Produk (dengan bobot popularitas)
    produk_data = [
        {'nama': 'Air Mineral 600ml', 'kat': 'Minuman', 'harga': 3500, 'pop': 10},
        {'nama': 'Mie Instan Goreng', 'kat': 'Makanan', 'harga': 3000, 'pop': 10},
        {'nama': 'Roti Sobek Cokelat', 'kat': 'Makanan', 'harga': 12000, 'pop': 8},
        {'nama': 'Teh Kotak 250ml', 'kat': 'Minuman', 'harga': 4000, 'pop': 9},
        {'nama': 'Kopi Sachet Instan', 'kat': 'Minuman', 'harga': 1500, 'pop': 9},
        {'nama': 'Snack Kentang Asin', 'kat': 'Makanan', 'harga': 10000, 'pop': 7},
        {'nama': 'Sabun Mandi Batang', 'kat': 'Pembersih', 'harga': 4500, 'pop': 5},
        {'nama': 'Deterjen Bubuk 800g', 'kat': 'Pembersih', 'harga': 18000, 'pop': 3},
        {'nama': 'Parfum Roll-on 50ml', 'kat': 'Kosmetik', 'harga': 22000, 'pop': 2},
        {'nama': 'Baterai AA (2pcs)', 'kat': 'Lainnya', 'harga': 15000, 'pop': 2},
        {'nama': 'Lipstik Matte Red', 'kat': 'Kosmetik', 'harga': 45000, 'pop': 1},
        {'nama': 'Susu UHT 1L', 'kat': 'Minuman', 'harga': 17000, 'pop': 7},
        {'nama': 'Biskuit Cokelat', 'kat': 'Makanan', 'harga': 9000, 'pop': 6},
        {'nama': 'Permen Mint', 'kat': 'Makanan', 'harga': 2500, 'pop': 5},
        {'nama': 'Minyak Goreng 1L', 'kat': 'Makanan', 'harga': 18000, 'pop': 8},
        {'nama': 'Tissue Basah', 'kat': 'Pembersih', 'harga': 12000, 'pop': 4},
        {'nama': 'Shampoo Sachet', 'kat': 'Pembersih', 'harga': 2000, 'pop': 6},
        {'nama': 'Sabun Cair 250ml', 'kat': 'Pembersih', 'harga': 15000, 'pop': 5},
        {'nama': 'Masker Wajah', 'kat': 'Kosmetik', 'harga': 12000, 'pop': 3},
        {'nama': 'Hand Sanitizer 100ml', 'kat': 'Pembersih', 'harga': 10000, 'pop': 4},
        {'nama': 'Sikat Gigi', 'kat': 'Pembersih', 'harga': 7000, 'pop': 5},
        {'nama': 'Pasta Gigi 75g', 'kat': 'Pembersih', 'harga': 9000, 'pop': 6},
        {'nama': 'Susu Kental Manis', 'kat': 'Minuman', 'harga': 8000, 'pop': 7},
        {'nama': 'Cokelat Batang', 'kat': 'Makanan', 'harga': 12000, 'pop': 5},
        {'nama': 'Keripik Singkong', 'kat': 'Makanan', 'harga': 8000, 'pop': 6},
        {'nama': 'Sarden Kaleng', 'kat': 'Makanan', 'harga': 15000, 'pop': 4},
        {'nama': 'Saus Sambal 135ml', 'kat': 'Makanan', 'harga': 6000, 'pop': 5},
        {'nama': 'Kecap Manis 135ml', 'kat': 'Makanan', 'harga': 7000, 'pop': 5},
        {'nama': 'Minuman Isotonik', 'kat': 'Minuman', 'harga': 8000, 'pop': 6},
        {'nama': 'Susu Kedelai', 'kat': 'Minuman', 'harga': 5000, 'pop': 5},
        {'nama': 'Teh Celup 25s', 'kat': 'Minuman', 'harga': 9000, 'pop': 4},
        {'nama': 'Kopi Botol 220ml', 'kat': 'Minuman', 'harga': 7000, 'pop': 5},
        {'nama': 'Sabun Cuci Piring', 'kat': 'Pembersih', 'harga': 8000, 'pop': 5},
        {'nama': 'Pembersih Lantai', 'kat': 'Pembersih', 'harga': 15000, 'pop': 3},
        {'nama': 'Body Lotion', 'kat': 'Kosmetik', 'harga': 25000, 'pop': 2},
        {'nama': 'Bedak Tabur', 'kat': 'Kosmetik', 'harga': 18000, 'pop': 2},
        {'nama': 'Maskara Waterproof', 'kat': 'Kosmetik', 'harga': 35000, 'pop': 1},
        {'nama': 'Deodoran Spray', 'kat': 'Kosmetik', 'harga': 20000, 'pop': 2},
        {'nama': 'Snack Jagung Bakar', 'kat': 'Makanan', 'harga': 9000, 'pop': 4},
        {'nama': 'Wafer Cokelat', 'kat': 'Makanan', 'harga': 8000, 'pop': 5},
        {'nama': 'Baterai AAA (2pcs)', 'kat': 'Lainnya', 'harga': 14000, 'pop': 2},
        {'nama': 'Korek Api Gas', 'kat': 'Lainnya', 'harga': 5000, 'pop': 2},
        {'nama': 'Plastik Sampah 20L', 'kat': 'Lainnya', 'harga': 12000, 'pop': 2},
        {'nama': 'Kain Pel', 'kat': 'Lainnya', 'harga': 10000, 'pop': 2},
        {'nama': 'Sapu Lidi', 'kat': 'Lainnya', 'harga': 9000, 'pop': 2},
        {'nama': 'Senter Mini', 'kat': 'Lainnya', 'harga': 25000, 'pop': 1},
        {'nama': 'Kabel USB 1m', 'kat': 'Lainnya', 'harga': 15000, 'pop': 1},
        {'nama': 'Powerbank 5000mAh', 'kat': 'Lainnya', 'harga': 75000, 'pop': 1},
        {'nama': 'Pulpen Biru', 'kat': 'Lainnya', 'harga': 4000, 'pop': 3},
        {'nama': 'Buku Tulis 38 Lbr', 'kat': 'Lainnya', 'harga': 6000, 'pop': 3},
        {'nama': 'Penghapus Karet', 'kat': 'Lainnya', 'harga': 2000, 'pop': 3},
        {'nama': 'Pensil 2B', 'kat': 'Lainnya', 'harga': 3000, 'pop': 3},
        {'nama': 'Spidol Hitam', 'kat': 'Lainnya', 'harga': 7000, 'pop': 2},
        {'nama': 'Lakban Bening', 'kat': 'Lainnya', 'harga': 8000, 'pop': 2},
        {'nama': 'Gunting Kertas', 'kat': 'Lainnya', 'harga': 9000, 'pop': 2},
        {'nama': 'Stapler Mini', 'kat': 'Lainnya', 'harga': 12000, 'pop': 2},
        {'nama': 'Kalkulator Saku', 'kat': 'Lainnya', 'harga': 25000, 'pop': 1},
        {'nama': 'Penggaris 30cm', 'kat': 'Lainnya', 'harga': 4000, 'pop': 2},
        {'nama': 'Tip-Ex Cair', 'kat': 'Lainnya', 'harga': 7000, 'pop': 2},
        {'nama': 'Binder Clip', 'kat': 'Lainnya', 'harga': 5000, 'pop': 2},
        {'nama': 'Kertas HVS A4', 'kat': 'Lainnya', 'harga': 35000, 'pop': 2},
        {'nama': 'Map Plastik', 'kat': 'Lainnya', 'harga': 3000, 'pop': 2},
        {'nama': 'Amplop Coklat', 'kat': 'Lainnya', 'harga': 2000, 'pop': 2},
        {'nama': 'Kertas Origami', 'kat': 'Lainnya', 'harga': 4000, 'pop': 2},
        {'nama': 'Sticky Notes', 'kat': 'Lainnya', 'harga': 6000, 'pop': 2},
        {'nama': 'Paper Clip', 'kat': 'Lainnya', 'harga': 2000, 'pop': 2},
        {'nama': 'Kertas Kado', 'kat': 'Lainnya', 'harga': 5000, 'pop': 2},
        {'nama': 'Tas Belanja Lipat', 'kat': 'Lainnya', 'harga': 10000, 'pop': 2},
        {'nama': 'Payung Lipat', 'kat': 'Lainnya', 'harga': 35000, 'pop': 1},
        {'nama': 'Botol Minum 600ml', 'kat': 'Lainnya', 'harga': 12000, 'pop': 2},
        {'nama': 'Lunch Box', 'kat': 'Lainnya', 'harga': 20000, 'pop': 2},
        {'nama': 'Termos Air 1L', 'kat': 'Lainnya', 'harga': 35000, 'pop': 1},
        {'nama': 'Gelas Plastik', 'kat': 'Lainnya', 'harga': 3000, 'pop': 2},
        {'nama': 'Piring Melamin', 'kat': 'Lainnya', 'harga': 8000, 'pop': 2},
        {'nama': 'Sendok Stainless', 'kat': 'Lainnya', 'harga': 4000, 'pop': 2},
        {'nama': 'Garpu Stainless', 'kat': 'Lainnya', 'harga': 4000, 'pop': 2},
        {'nama': 'Pisau Dapur', 'kat': 'Lainnya', 'harga': 15000, 'pop': 2},
        {'nama': 'Talenan Plastik', 'kat': 'Lainnya', 'harga': 10000, 'pop': 2},
        {'nama': 'Wajan Mini', 'kat': 'Lainnya', 'harga': 25000, 'pop': 1},
        {'nama': 'Sutil Kayu', 'kat': 'Lainnya', 'harga': 5000, 'pop': 2},
        {'nama': 'Serbet Dapur', 'kat': 'Lainnya', 'harga': 6000, 'pop': 2},
        {'nama': 'Lap Kanebo', 'kat': 'Lainnya', 'harga': 12000, 'pop': 2},
        {'nama': 'Ember Plastik', 'kat': 'Lainnya', 'harga': 15000, 'pop': 2},
        {'nama': 'Gayung Plastik', 'kat': 'Lainnya', 'harga': 5000, 'pop': 2},
        {'nama': 'Sapu Ijuk', 'kat': 'Lainnya', 'harga': 12000, 'pop': 2},
        {'nama': 'Kemoceng', 'kat': 'Lainnya', 'harga': 7000, 'pop': 2},
        {'nama': 'Obeng Plus', 'kat': 'Lainnya', 'harga': 10000, 'pop': 1},
        {'nama': 'Tang Kombinasi', 'kat': 'Lainnya', 'harga': 20000, 'pop': 1},
        {'nama': 'Kunci Inggris', 'kat': 'Lainnya', 'harga': 25000, 'pop': 1},
        {'nama': 'Meteran 3m', 'kat': 'Lainnya', 'harga': 10000, 'pop': 1},
        {'nama': 'Lakban Hitam', 'kat': 'Lainnya', 'harga': 8000, 'pop': 2},
        {'nama': 'Kabel Roll 5m', 'kat': 'Lainnya', 'harga': 35000, 'pop': 1},
        {'nama': 'Lampu LED 7W', 'kat': 'Lainnya', 'harga': 15000, 'pop': 2},
        {'nama': 'Stop Kontak', 'kat': 'Lainnya', 'harga': 12000, 'pop': 2},
        {'nama': 'Adaptor Charger', 'kat': 'Lainnya', 'harga': 20000, 'pop': 1},
        {'nama': 'Kipas Angin Mini', 'kat': 'Lainnya', 'harga': 35000, 'pop': 1},
        {'nama': 'Jam Dinding', 'kat': 'Lainnya', 'harga': 25000, 'pop': 1},
        {'nama': 'Alarm Clock', 'kat': 'Lainnya', 'harga': 20000, 'pop': 1},
        {'nama': 'Bantal Leher', 'kat': 'Lainnya', 'harga': 15000, 'pop': 1},
        {'nama': 'Gantungan Kunci', 'kat': 'Lainnya', 'harga': 3000, 'pop': 2},
        {'nama': 'Korek Gas Mini', 'kat': 'Lainnya', 'harga': 4000, 'pop': 2},
        {'nama': 'Korek Api Kayu', 'kat': 'Lainnya', 'harga': 2000, 'pop': 2},
        {'nama': 'Korek Api Elektrik', 'kat': 'Lainnya', 'harga': 15000, 'pop': 1},
        {'nama': 'Kunci L', 'kat': 'Lainnya', 'harga': 8000, 'pop': 1},
        {'nama': 'Obeng Min', 'kat': 'Lainnya', 'harga': 7000, 'pop': 1},
        {'nama': 'Tang Potong', 'kat': 'Lainnya', 'harga': 12000, 'pop': 1},
        {'nama': 'Pisau Cutter', 'kat': 'Lainnya', 'harga': 5000, 'pop': 2},
        {'nama': 'Kunci Pas', 'kat': 'Lainnya', 'harga': 10000, 'pop': 1},
        {'nama': 'Obeng Tespen', 'kat': 'Lainnya', 'harga': 6000, 'pop': 1},
        {'nama': 'Tang Lancip', 'kat': 'Lainnya', 'harga': 12000, 'pop': 1},
        {'nama': 'Kunci Ring', 'kat': 'Lainnya', 'harga': 9000, 'pop': 1},
        {'nama': 'Kunci Sock', 'kat': 'Lainnya', 'harga': 15000, 'pop': 1},
        {'nama': 'Kunci T', 'kat': 'Lainnya', 'harga': 10000, 'pop': 1},
        {'nama': 'Kunci Pipa', 'kat': 'Lainnya', 'harga': 20000, 'pop': 1},
        {'nama': 'Kunci Inggris Mini', 'kat': 'Lainnya', 'harga': 12000, 'pop': 1},
        {'nama': 'Tang Crimping', 'kat': 'Lainnya', 'harga': 25000, 'pop': 1},
        {'nama': 'Kunci L Set', 'kat': 'Lainnya', 'harga': 35000, 'pop': 1},
        {'nama': 'Obeng Set', 'kat': 'Lainnya', 'harga': 20000, 'pop': 1},
        {'nama': 'Tang Kombinasi Mini', 'kat': 'Lainnya', 'harga': 15000, 'pop': 1},
        {'nama': 'Kunci Inggris Jumbo', 'kat': 'Lainnya', 'harga': 40000, 'pop': 1},
        {'nama': 'Tang Rivet', 'kat': 'Lainnya', 'harga': 30000, 'pop': 1},
        {'nama': 'Kunci Inggris Set', 'kat': 'Lainnya', 'harga': 50000, 'pop': 1},
        {'nama': 'Tang Snap Ring', 'kat': 'Lainnya', 'harga': 20000, 'pop': 1},
        {'nama': 'Tang Kombinasi Jumbo', 'kat': 'Lainnya', 'harga': 35000, 'pop': 1},
        {'nama': 'Kunci Inggris Panjang', 'kat': 'Lainnya', 'harga': 30000, 'pop': 1},
        {'nama': 'Tang Kombinasi Panjang', 'kat': 'Lainnya', 'harga': 25000, 'pop': 1},
        {'nama': 'Kunci Inggris Pendek', 'kat': 'Lainnya', 'harga': 20000, 'pop': 1},
        {'nama': 'Tang Kombinasi Pendek', 'kat': 'Lainnya', 'harga': 15000, 'pop': 1},
        {'nama': 'Kunci Inggris Kecil', 'kat': 'Lainnya', 'harga': 10000, 'pop': 1},
        {'nama': 'Tang Kombinasi Kecil', 'kat': 'Lainnya', 'harga': 8000, 'pop': 1},
        {'nama': 'Kunci Inggris Mini', 'kat': 'Lainnya', 'harga': 6000, 'pop': 1},
        {'nama': 'Tang Kombinasi Mini', 'kat': 'Lainnya', 'harga': 5000, 'pop': 1},
    ]

    # Tambahkan produk random otomatis
    kategori_list = ['Makanan', 'Minuman', 'Pembersih', 'Kosmetik', 'Lainnya']
    nama_awal = ['Super', 'Fresh', 'Best', 'Top', 'Ultra', 'Mega', 'Eco', 'Smart', 'Quick', 'Happy']
    nama_produk = ['Snack', 'Drink', 'Soap', 'Shampoo', 'Juice', 'Tea', 'Coffee', 'Biscuit', 'Candy', 'Powder', 'Spray', 'Bar', 'Bottle', 'Pack', 'Box', 'Roll', 'Cream', 'Paste', 'Oil', 'Milk']
    satuan = ['100g', '200g', '250ml', '500ml', '1L', '2L', '3pcs', '5pcs', '10pcs', '1kg']

    for i in range(200):
        kat = random.choice(kategori_list)
        nama = f"{random.choice(nama_awal)} {random.choice(nama_produk)} {random.choice(satuan)}"
        harga = random.randint(2000, 100000)
        pop = random.randint(1, 10)
        produk_data.append({'nama': nama, 'kat': kat, 'harga': harga, 'pop': pop})

    df_produk = pd.DataFrame([{
        'id': i + 1,
        'kode_produk': f'P{i+1:04d}',
        'nama_produk': p['nama'],
        'kategori': p['kat'],
        'harga_jual': p['harga'],
    } for i, p in enumerate(produk_data)])
    
    produk_weights = [p['pop'] for p in produk_data]

    # 4. Member
    member_data = [{
        'id': i + 1,
        'kode_member': f'M{i+1:05d}',
        'nama_member': fake.name(),
        'tanggal_bergabung': fake.date_between(start_date='-3y', end_date='-1M'),
    } for i in range(200)]
    df_member = pd.DataFrame(member_data)

    with engine.connect() as conn:
        with conn.begin():
            df_toko.to_sql('toko', con=conn, if_exists='append', index=False)
            df_produk.to_sql('produk', con=conn, if_exists='append', index=False)
            df_karyawan.to_sql('karyawan', con=conn, if_exists='append', index=False)
            df_member.to_sql('member', con=conn, if_exists='append', index=False)
    
    print("✅ Data master berhasil disimpan.")
    return df_toko, df_karyawan, df_produk, df_member, produk_weights


def generate_stok(df_toko, df_produk):
    print("Membuat data stok awal...")
    stok_data = []
    for _, toko in df_toko.iterrows():
        for _, produk in df_produk.iterrows():
            stok_data.append({
                'id_produk': produk['id'],
                'id_toko': toko['id'],
                'jumlah_stok': random.randint(20, 200),
                'last_updated': datetime.now()
            })
    df_stok = pd.DataFrame(stok_data)
    with engine.connect() as conn:
        with conn.begin():
            df_stok.to_sql('stok_gudang', con=conn, if_exists='append', index=False)
    print("✅ Data stok berhasil disimpan.")


def generate_transactions(days, df_toko, df_karyawan, df_produk, df_member, produk_weights):
    print(f"Membuat data transaksi untuk {days} hari terakhir...")
    transaksi_data = []
    detail_transaksi_data = []
    
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        num_transactions = random.randint(40, 60) if current_date.weekday() >= 5 else random.randint(20, 30)
        
        for _ in range(num_transactions):
            peak_hours = [time(8), time(9), time(12), time(13), time(18), time(19)]
            trans_time = random.choices(
                population=[fake.date_time_between(start_date=current_date, end_date=current_date + timedelta(days=1)-timedelta(seconds=1)),
                            datetime.combine(current_date, random.choice(peak_hours)) + timedelta(minutes=random.randint(0,59))],
                weights=[0.4, 0.6],
                k=1)[0]
            
            toko_terpilih = df_toko.sample(1).iloc[0]
            karyawan_toko = df_karyawan[df_karyawan['id_toko'] == toko_terpilih['id']]
            
            ## <-- PERBAIKAN DIMULAI DI SINI
            # 1. Tentukan apakah transaksi ini oleh member (probabilitas 60%)
            is_member_transaction = random.choices([True, False], weights=[0.6, 0.4], k=1)[0]
            
            # 2. Jika ya, pilih ID member acak. Jika tidak, gunakan None.
            member_id = random.choice(df_member['id'].tolist()) if is_member_transaction else None
            ## <-- PERBAIKAN SELESAI
            
            transaksi_id = len(transaksi_data) + 1
            transaksi_data.append({
                'id': transaksi_id,
                'waktu_transaksi': trans_time,
                'id_toko': toko_terpilih['id'],
                'id_karyawan': random.choice(karyawan_toko['id'].tolist()),
                'id_member': member_id # Gunakan variabel yang sudah kita buat
            })
            
            produk_dibeli = set()
            jumlah_item = random.choices([1,2,3,4,5], weights=[0.2,0.4,0.3,0.05,0.05], k=1)[0]
            
            for _ in range(jumlah_item):
                produk_terpilih = df_produk.sample(1, weights=produk_weights).iloc[0]
                if produk_terpilih['id'] in produk_dibeli:
                    continue
                produk_dibeli.add(produk_terpilih['id'])

                detail_transaksi_data.append({
                    'id_transaksi': transaksi_id,
                    'id_produk': produk_terpilih['id'],
                    'jumlah': random.randint(1, 3),
                    'harga_saat_transaksi': produk_terpilih['harga_jual']
                })

    with engine.connect() as conn:
        with conn.begin():
            pd.DataFrame(transaksi_data).to_sql('transaksi', con=conn, if_exists='append', index=False)
            pd.DataFrame(detail_transaksi_data).to_sql('detail_transaksi', con=conn, if_exists='append', index=False)
    print(f"✅ {len(transaksi_data)} transaksi dan {len(detail_transaksi_data)} detail berhasil disimpan.")


if __name__ == "__main__":
    clear_all_data()
    df_toko, df_karyawan, df_produk, df_member, produk_weights = generate_master_data()
    generate_stok(df_toko, df_produk)
    generate_transactions(365, df_toko, df_karyawan, df_produk, df_member, produk_weights)
    print("\n🎉 Proses pembuatan data dummy selesai!")