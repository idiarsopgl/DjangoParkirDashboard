# Sistem Manajemen Parkir dengan ANPR

Sistem manajemen parkir modern dengan fitur Automatic Number Plate Recognition (ANPR) untuk mengelola parkir kendaraan secara efisien.

## Daftar Isi
- [Pendahuluan](#pendahuluan)
- [Fitur Utama](#fitur-utama)
- [Panduan Pengguna](#panduan-pengguna)
  - [Panduan untuk Petugas Parkir](#panduan-untuk-petugas-parkir)
  - [Panduan untuk Admin](#panduan-untuk-admin)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Pemeliharaan](#pemeliharaan)
- [ANPR & Pencocokan Gambar](#anpr-pencocokan-gambar)
- [Spesifikasi Sistem](#spesifikasi-sistem)

## Pendahuluan

Sistem Manajemen Parkir dengan ANPR adalah solusi modern untuk mengelola area parkir dengan efisien. Sistem ini menggunakan teknologi pengenalan plat nomor otomatis (ANPR) untuk mencatat kendaraan yang masuk dan keluar, serta dilengkapi dengan berbagai fitur manajemen dan pelaporan.

## Fitur Utama

1. Pengenalan Plat Nomor Otomatis (ANPR)
2. Manajemen Parkir Real-time
3. Sistem Pembayaran Digital
4. Pelaporan dan Analitik
5. Manajemen Pengguna
6. Backup dan Restore Data
7. Log Aktivitas
8. Dashboard Interaktif
9. ANPR & Pencocokan Gambar

## Panduan Pengguna

### Panduan untuk Petugas Parkir

#### 1. Login ke Sistem
- Buka aplikasi di browser
- Masukkan username dan password yang diberikan
- Klik tombol "Masuk"

#### 2. Mencatat Kendaraan Masuk
1. Di halaman utama, klik "Kendaraan Masuk"
2. Arahkan kamera ke plat nomor kendaraan
3. Sistem akan otomatis mendeteksi plat nomor
4. Verifikasi hasil deteksi
5. Pilih jenis kendaraan
6. Klik "Simpan" untuk mencetak tiket

#### 3. Mencatat Kendaraan Keluar
1. Scan tiket parkir atau masukkan nomor tiket
2. Sistem akan menampilkan informasi kendaraan
3. Verifikasi plat nomor kendaraan
4. Sistem akan menghitung biaya parkir
5. Proses pembayaran:
   - Pilih metode pembayaran
   - Masukkan jumlah yang diterima
   - Klik "Proses Pembayaran"
6. Cetak struk pembayaran

#### 4. Menangani Kasus Khusus
- **Tiket Hilang**:
  1. Klik "Tiket Hilang"
  2. Masukkan plat nomor kendaraan
  3. Verifikasi dengan foto kendaraan
  4. Proses sesuai prosedur tiket hilang

- **Kendaraan Menginap**:
  1. Gunakan menu "Kendaraan Menginap"
  2. Ikuti prosedur tarif menginap

#### 5. Laporan Harian
1. Di akhir shift, buka menu "Laporan Shift"
2. Verifikasi semua transaksi
3. Cetak laporan shift
4. Serahkan ke supervisor

### Panduan untuk Admin

#### 1. Dashboard Admin
- **Akses Dashboard**:
  1. Login sebagai admin
  2. Lihat statistik real-time:
     - Jumlah kendaraan
     - Pendapatan
     - Slot tersedia
     - Grafik tren

#### 2. Manajemen Pengguna
- **Menambah Pengguna Baru**:
  1. Buka menu "Kelola Pengguna"
  2. Klik "Tambah Pengguna"
  3. Isi informasi:
     - Username
     - Password
     - Role (Admin/Petugas)
     - Informasi pribadi
  4. Klik "Simpan"

- **Mengelola Pengguna**:
  1. Edit informasi pengguna
  2. Reset password
  3. Nonaktifkan akun
  4. Atur hak akses

#### 3. Manajemen Parkir
- **Pengaturan Tarif**:
  1. Buka menu "Pengaturan Tarif"
  2. Atur tarif berdasarkan:
     - Jenis kendaraan
     - Durasi
     - Tarif khusus

- **Manajemen Slot**:
  1. Atur jumlah slot
  2. Monitor okupansi
  3. Atur zona parkir

#### 4. Laporan dan Analisis
- **Laporan Keuangan**:
  1. Buka menu "Laporan"
  2. Pilih jenis laporan
  3. Atur periode
  4. Export ke Excel/PDF

- **Analisis Data**:
  1. Lihat tren parkir
  2. Analisis pendapatan
  3. Monitor kinerja sistem

#### 5. Backup dan Maintenance
- **Backup Data**:
  1. Buka menu "Backup"
  2. Pilih jenis backup
  3. Atur jadwal backup
  4. Download/restore backup

- **Log Aktivitas**:
  1. Monitor aktivitas sistem
  2. Filter log berdasarkan:
     - Waktu
     - Pengguna
     - Jenis aktivitas
  3. Export log

#### 6. Pengaturan Sistem
- **Konfigurasi Umum**:
  1. Pengaturan aplikasi
  2. Konfigurasi printer
  3. Pengaturan kamera
  4. Integrasi sistem

- **Keamanan**:
  1. Atur kebijakan password
  2. Monitor login gagal
  3. Atur backup otomatis

## Instalasi

1. Prasyarat
   - Python 3.8+
   - Pip
   - Virtualenv (disarankan)
   - Tesseract OCR (penting untuk fitur ANPR)

2. Clone repository
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
4. Install Tesseract OCR:
   - **Windows**: 
     1. Download Tesseract installer dari [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
     2. Install ke lokasi default (`C:\Program Files\Tesseract-OCR\`)
     3. Pastikan Tesseract berada di PATH sistem

   - **Linux**:
     ```bash
     sudo apt install tesseract-ocr
     ```
   
   - **macOS**:
     ```bash
     brew install tesseract
     ```

5. Setup database:
   ```bash
   python manage.py migrate
   ```
6. Jalankan aplikasi:
   ```bash
   python manage.py runserver 8900
   ```

## Konfigurasi

1. Salin `.env.example` ke `.env`
2. Sesuaikan konfigurasi:
   - Database
   - Secret key
   - Path kamera
   - Pengaturan printer

## Pemeliharaan

1. Backup rutin:
   - Database
   - File konfigurasi
   - Log sistem

2. Monitoring:
   - Penggunaan disk
   - Performa sistem
   - Log error

3. Update:
   - Sistem operasi
   - Dependencies
   - Aplikasi

4. Troubleshooting:
   - Cek log error
   - Verifikasi konfigurasi
   - Test koneksi

## ANPR & Pencocokan Gambar

### Fitur ANPR

1. Pengenalan Plat Nomor Otomatis
2. Penyimpanan & Pencocokan Gambar Kendaraan
3. Validasi Keamanan Berbasis Gambar

### Spesifikasi Teknis

#### Database

Model `ParkingRecord` menyimpan data parkir dengan field:
- `entry_image`: Path gambar saat kendaraan masuk
- `exit_image`: Path gambar saat kendaraan keluar
- `image_match_score`: Skor kecocokan gambar (0-1)

#### Backend

1. Manajemen Gambar
   - `save_camera_image`: Menyimpan gambar dari webcam dengan timestamp unik
   - `compare_images`: Mencocokkan gambar menggunakan histogram comparison
   - Format gambar: JPEG
   - Lokasi penyimpanan: `/static/uploads/`

2. API Endpoints
   - `/api/capture-entry`: Mencatat kendaraan masuk
   - `/api/capture-exit`: Mencatat kendaraan keluar

#### Frontend

1. Komponen Kamera
   - Menggunakan WebRTC untuk akses webcam
   - Preview langsung dari kamera
   - Capture gambar otomatis

2. Antarmuka Pengguna
   - Progress bar warna untuk skor kecocokan
   - Tampilan biaya parkir real-time
   - Status validasi kendaraan

### Fitur Keamanan

1. Validasi Gambar
   - Timestamp unik untuk setiap gambar
   - Pencocokan gambar masuk & keluar
   - Skor kecocokan sebagai validasi

2. Validasi Parkir
   - Cek status parkir sebelum keluar
   - Validasi operator yang bertugas
   - Error handling untuk kegagalan sistem

## Spesifikasi Sistem

### Kebutuhan Minimal
- CPU: 2 core
- RAM: 4 GB
- Storage: 10 GB
- OS: Windows/Linux
- Webcam dengan resolusi minimal 720p

### Kapasitas Database

SQLite dengan spesifikasi minimal:

1. Kapasitas Record:
   - Ukuran optimal database: 2-3 GB
   - Jumlah record optimal: ~5.5 juta record

2. Performa:
   - Transaksi per detik: 50-100
   - Kendaraan per jam: 100-200
   - Kendaraan per hari: 2,400-4,800

3. Maintenance:
   ```sql
   -- Hapus record lama (jalankan setiap bulan)
   DELETE FROM parking_record 
   WHERE created_at < date('now', '-6 months');
   
   -- Optimasi database
   VACUUM;
   ```

### Backup & Recovery

1. Backup Database:
   ```bash
   # Backup mingguan
   python manage.py dumpdata > backup/parking_$(date +%Y%m%d).json
   ```

2. Backup Gambar:
   ```bash
   # Backup folder uploads
   tar -czf backup/images_$(date +%Y%m%d).tar.gz media/uploads/
   ```

3. Recovery:
   ```bash
   # Restore database
   python manage.py loaddata backup/parking_20250101.json
   ```

## Kontak Support

Untuk bantuan teknis, hubungi:
- Email: support@parking-system.com
- Telp: (021) 1234567
- Jam kerja: 08.00 - 17.00 WIB
