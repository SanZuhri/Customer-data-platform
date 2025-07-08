-- Skema untuk PostgreSQL
-- Versi 1.1: Menambahkan komentar rinci untuk kejelasan.

-- ===== TABEL MASTER =====

-- Tabel untuk menyimpan data master setiap gerai/toko.
CREATE TABLE toko (
    id SERIAL PRIMARY KEY,
    nama_toko VARCHAR(100) NOT NULL,
    alamat TEXT,
    kota VARCHAR(50)
);

-- Tabel untuk menyimpan data master karyawan.
CREATE TABLE karyawan (
    id SERIAL PRIMARY KEY,
    nama_karyawan VARCHAR(100) NOT NULL,
    posisi VARCHAR(50),
    id_toko INTEGER NOT NULL REFERENCES toko(id) -- Setiap karyawan terikat pada satu toko.
);

-- Tabel untuk menyimpan katalog semua produk yang dijual.
CREATE TABLE produk (
    id SERIAL PRIMARY KEY,
    kode_produk VARCHAR(20) UNIQUE NOT NULL, -- Kode unik untuk setiap produk.
    nama_produk VARCHAR(100) NOT NULL,
    kategori VARCHAR(50),
    harga_jual NUMERIC(10, 2) NOT NULL -- Menggunakan NUMERIC untuk presisi keuangan.
);

-- Tabel untuk menyimpan data pelanggan yang terdaftar sebagai member.
CREATE TABLE member (
    id SERIAL PRIMARY KEY,
    kode_member VARCHAR(20) UNIQUE NOT NULL,
    nama_member VARCHAR(100),
    tanggal_bergabung DATE
);


-- ===== TABEL TRANSAKSIONAL & JUNCTION =====

-- Tabel header untuk setiap transaksi penjualan (nota).
CREATE TABLE transaksi (
    id SERIAL PRIMARY KEY,
    waktu_transaksi TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Menggunakan TIMESTAMPTZ agar timezone-aware.
    id_toko INTEGER NOT NULL REFERENCES toko(id),
    id_karyawan INTEGER NOT NULL REFERENCES karyawan(id),
    id_member INTEGER REFERENCES member(id) NULL -- Bisa NULL jika pembeli bukan member.
);

-- Tabel detail/item dalam setiap transaksi.
-- Ini adalah junction table antara 'transaksi' dan 'produk'.
CREATE TABLE detail_transaksi (
    id SERIAL PRIMARY KEY,
    id_transaksi INTEGER NOT NULL REFERENCES transaksi(id) ON DELETE CASCADE, -- Jika transaksi dihapus, detailnya ikut terhapus.
    id_produk INTEGER NOT NULL REFERENCES produk(id),
    jumlah INTEGER NOT NULL CHECK (jumlah > 0), -- Memastikan jumlah selalu positif.
    harga_saat_transaksi NUMERIC(10, 2) NOT NULL -- Mencatat harga saat itu, karena harga bisa berubah.
);

-- Tabel untuk mencatat jumlah stok setiap produk di setiap toko.
-- Ini adalah junction table antara 'toko' dan 'produk'.
CREATE TABLE stok_gudang (
    id SERIAL PRIMARY KEY,
    id_produk INTEGER NOT NULL REFERENCES produk(id),
    id_toko INTEGER NOT NULL REFERENCES toko(id),
    jumlah_stok INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(id_produk, id_toko) -- Memastikan tidak ada duplikasi stok untuk produk yang sama di toko yang sama.
);


-- ===== TABEL KONFIGURASI APLIKASI =====

-- Tabel independen untuk menyimpan konfigurasi filter yang dibuat pengguna.
CREATE TABLE filter_tersimpan (
    id SERIAL PRIMARY KEY,
    nama_filter VARCHAR(100) UNIQUE NOT NULL,
    deskripsi TEXT,
    konfigurasi_json JSONB NOT NULL, -- Menggunakan JSONB karena lebih efisien untuk query dan indexing di PostgreSQL.
    dibuat_oleh VARCHAR(100),
    dibuat_pada TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ===== INDEX UNTUK OPTIMASI PERFORMA =====

-- Index untuk mempercepat query yang memfilter berdasarkan rentang waktu.
CREATE INDEX idx_transaksi_waktu ON transaksi(waktu_transaksi);

-- Index untuk mempercepat join dan filter berdasarkan toko.
CREATE INDEX idx_transaksi_toko ON transaksi(id_toko);

-- Index untuk mempercepat join dan filter berdasarkan produk.
CREATE INDEX idx_detail_transaksi_produk ON detail_transaksi(id_produk);

-- Index untuk mempercepat filter berdasarkan kategori produk, yang umum digunakan.
CREATE INDEX idx_produk_kategori ON produk(kategori);
