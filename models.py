# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, JSON, Date, Text, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB 
from database import Base, engine
import datetime

class Toko(Base):
    __tablename__ = 'toko'
    id = Column(Integer, primary_key=True)
    nama_toko = Column(String(100), nullable=False)
    alamat = Column(Text)
    kota = Column(String(50))

class Karyawan(Base):
    __tablename__ = 'karyawan'
    id = Column(Integer, primary_key=True)
    nama_karyawan = Column(String(100), nullable=False)
    posisi = Column(String(50))
    id_toko = Column(Integer, ForeignKey('toko.id'), nullable=False)

class Produk(Base):
    __tablename__ = 'produk'
    id = Column(Integer, primary_key=True)
    kode_produk = Column(String(20), unique=True, nullable=False)
    nama_produk = Column(String(100), nullable=False)
    kategori = Column(String(50))
    harga_jual = Column(Numeric(10, 2), nullable=False)

class Member(Base):
    __tablename__ = 'member'
    id = Column(Integer, primary_key=True)
    kode_member = Column(String(20), unique=True, nullable=False)
    nama_member = Column(String(100))
    tanggal_bergabung = Column(Date)

class Transaksi(Base):
    __tablename__ = 'transaksi'
    id = Column(Integer, primary_key=True)
    waktu_transaksi = Column(DateTime(timezone=True), default=datetime.datetime.now)
    id_toko = Column(Integer, ForeignKey('toko.id'), nullable=False)
    id_karyawan = Column(Integer, ForeignKey('karyawan.id'), nullable=False)
    id_member = Column(Integer, ForeignKey('member.id'))

class DetailTransaksi(Base):
    __tablename__ = 'detail_transaksi'
    id = Column(Integer, primary_key=True)
    id_transaksi = Column(Integer, ForeignKey('transaksi.id', ondelete='CASCADE'), nullable=False)
    id_produk = Column(Integer, ForeignKey('produk.id'), nullable=False)
    jumlah = Column(Integer, CheckConstraint('jumlah > 0'), nullable=False)
    harga_saat_transaksi = Column(Numeric(10, 2), nullable=False)

class StokGudang(Base):
    __tablename__ = 'stok_gudang'
    id = Column(Integer, primary_key=True)
    id_produk = Column(Integer, ForeignKey('produk.id'), nullable=False)
    id_toko = Column(Integer, ForeignKey('toko.id'), nullable=False)
    jumlah_stok = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime(timezone=True), default=datetime.datetime.now)

class FilterTersimpan(Base):
    __tablename__ = 'filter_tersimpan'
    id = Column(Integer, primary_key=True)
    nama_filter = Column(String(100), unique=True, nullable=False)
    deskripsi = Column(Text)
    konfigurasi_json = Column(JSONB, nullable=False)
    dibuat_oleh = Column(String(100))
    dibuat_pada = Column(DateTime(timezone=True), default=datetime.datetime.now)