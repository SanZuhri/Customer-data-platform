## Instalasi

1. **Clone repository:**
   ```sh
   git clone https://github.com/USERNAME/alfamart-dashboard.git
   cd alfamart-dashboard
   ```
2. **Buat virtual environment & aktifkan:**
   ```sh
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   *(Jika belum ada requirements.txt, install manual:)*
   ```sh
   pip install streamlit pandas sqlalchemy psycopg2-binary plotly streamlit-condition-tree
   ```

4. **Setup database:**
   - Pastikan PostgreSQL sudah berjalan dan database sudah dibuat sesuai konfigurasi di `app.py`/`database.py`.
   - Jalankan migrasi/tabel jika perlu.

## Menjalankan Aplikasi

```sh
streamlit run app.py
```

Akses di browser: [http://localhost:8501](http://localhost:8501)

## Struktur Folder
- `app.py` : Main Streamlit app
- `database.py`, `models.py` : Koneksi & model database
- `data_generator.py` : (Opsional) Generator data dummy
- `venv/` : Virtual environment (tidak diupload ke repo)

## Catatan
- Pastikan environment variabel database sudah benar.
- Untuk pengembangan, gunakan branch terpisah.
