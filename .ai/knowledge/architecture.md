# ARSITEKTUR TEKNIS — Platform E-Commerce Mandiri Fashion Wanita

## 1. Pendekatan Utama

- [x] **Web App** — Backend (REST API) + Frontend (Web Responsif)
- [ ] n8n Orchestration
- [ ] Custom Script (Python/Node)
- [ ] Desktop App

**Alasan:** Project ini adalah platform e-commerce multi-merchant yang dioperasikan langsung oleh merchant (kelola produk, pesanan, pelanggan) dan pembeli (browse, belanja, bayar). Karena ada dua aktor dengan kebutuhan berbeda dan alur data kompleks (auth, CRUD, payment flow, notifikasi, CRM), solusinya adalah aplikasi web dengan backend REST API dan frontend web responsif. Satu backend melayani dua client (web dan mobile app di masa depan). Backend dipisah dari frontend untuk menjaga fleksibilitas — mobile app (React Native) bisa konsumsi API yang sama tanpa perubahan.

---

## 2. Aliran Data (Data Flow)

### 2a. Alur Utama: Pembeli Belanja

```
Pembeli (Web/Mobile)
  → Browse katalog (GET produk)
  → Tambah ke keranjang (POST cart)
  → Isi form checkout (POST checkout)
  → Bayar via Midtrans (POST buat transaksi → redirect ke halaman Midtrans)
  → Midtrans verifikasi pembayaran
  → Webhook Midtrans → Backend update status order
  → Notifikasi dikirim ke merchant + pembeli
```

### 2b. Alur Utama: Merchant Kelola Toko

```
Merchant (Login)
  → Dashboard: lihat pesanan masuk, notifikasi
  → Kelola produk (CRUD produk, varian, foto, kategori)
  → Kelola pesanan (ubah status, input resi)
  → Lihat data pelanggan (CRM, ekspor CSV)
  → Pengaturan toko (nama, logo, ongkir, kebijakan)
```

### 2c. Alur Pembayaran (Midtrans)

```
Backend: Kirim data order ke Midtrans (Snap API)
  → Terima snap_token
  → Frontend: tampilkan halaman pembayaran Midtrans

Midtrans: Kirim webhook ke backend
  → Backend: verifikasi signature SHA-512
  → Backend: cek idempotency (apakah order_id sudah diproses)
  → Backend: update status order → "paid"
  → Backend: kurangi stok varian
  → Backend: simpan raw_response sebagai audit trail
  → Backend: trigger notifikasi
```

---

## 3. Struktur Folder

```
e-commerce-mandiri-fashion/
├── .ai/
│   ├── knowledge/
│   │   ├── prd.md              ← PRD v2 (freezed)
│   │   ├── ssot.md             ← Database Design (SSOT)
│   │   └── architecture.md     ← Dokumen ini
│   └── decisions/              ← ADR (Architecture Decision Records)
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── apps/
│   │   ├── authentication/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── permissions.py
│   │   │   └── signals.py
│   │   ├── products/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── filters.py
│   │   ├── cart/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   ├── orders/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── utils.py
│   │   ├── payments/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── midtrans_client.py
│   │   ├── customers/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   └── exporters.py
│   │   ├── notifications/
│   │   │   ├── models.py
│   │   │   ├── services.py
│   │   │   └── urls.py
│   │   ├── reviews/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   └── urls.py
│   │   └── store/
│   │       ├── models.py
│   │       ├── serializers.py
│   │       ├── views.py
│   │       └── urls.py
│   ├── media/                   ← upload produk, logo, dll
│   │   └── .gitkeep
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   ├── claymorphism.css
│   │   │   └── responsive.css
│   │   ├── js/
│   │   │   ├── app.js
│   │   │   ├── cart.js
│   │   │   ├── checkout.js
│   │   │   └── utils.js
│   │   └── images/
│   │       └── placeholder.png
│   ├── templates/
│   │   ├── base.html
│   │   ├── store/
│   │   │   ├── home.html
│   │   │   ├── catalog.html
│   │   │   └── product_detail.html
│   │   ├── checkout/
│   │   │   ├── cart.html
│   │   │   └── payment.html
│   │   ├── order/
│   │   │   ├── confirmation.html
│   │   │   └── tracking.html
│   │   └── merchant/
│   │       ├── dashboard.html
│   │       ├── product_form.html
│   │       ├── order_list.html
│   │       ├── customer_list.html
│   │       └── store_settings.html
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── .env.template
│   └── tests/
│       ├── __init__.py
│       ├── test_authentication.py
│       ├── test_products.py
│       ├── test_cart.py
│       ├── test_orders.py
│       └── test_payments.py
├── mobile/
│   └── (React Native — fase 3)
├── docs/
│   └── USER_GUIDE.md
└── .gitignore
```

---

## 4. Dependency & Environment Variables

### 4a. Backend Dependencies (Python/Django)

| Package | Fungsi |
|---------|--------|
| Django | Framework utama backend |
| Django REST Framework | Serializer & API views |
| django-environ | Baca .env secara aman |
| djangorestframework-simplejwt | JWT auth (access + refresh token) |
| mysqlclient | Koneksi ke MySQL |
| Pillow | Proses & validasi gambar |
| django-cors-headers | Izinkan cross-origin (web ↔ API) |
| pyjwt | Decode/verify JWT (opsional, kalau custom logic) |
| requests | HTTP client ke Midtrans API |

### 4b. Environment Variables

```env
# ── Django ────────────────────────────────────────
DJANGO_SECRET_KEY=***
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_DEBUG=True

# ── Database ─────────────────────────────────────
DB_ENGINE=mysql
DB_NAME=ecommerce_fashion
DB_USER=root
DB_PASSWORD=***
DB_HOST=127.0.0.1
DB_PORT=3306

# ── Midtrans ─────────────────────────────────────
MIDTRANS_SERVER_KEY=
MIDTRANS_CLIENT_KEY=
MIDTRANS_IS_PRODUCTION=False
MIDTRANS_WEBHOOK_URL=/api/payments/webhook/

# ── Media / File Upload ─────────────────────────
MEDIA_ROOT=media/
MEDIA_URL=/media/
MAX_UPLOAD_SIZE_MB=5

# ── Email (Notifikasi) ──────────────────────────
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USER=
EMAIL_PASSWORD=

# ── CORS (Development) ──────────────────────────
CORS_ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

---

## 5. Database

- [ ] SQLite (untuk lokal/sederhana)
- [x] **MySQL** (untuk production)
- [ ] Tidak pakai database

**Alasan:** MySQL adalah pasangan paling natural untuk Django dan mudah di-deploy ke hampir semua hosting PHP/Python. Untuk skala awal (multi-merchant, bukan jutaan user), MySQL sudah sangat memadai. Jika nanti perlu scale, migrasi ke PostgreSQL bisa dilakukan tanpa perubahan signifikan di kode aplikasi.

**Schema lengkap:** Lihat `ssot.md` (Single Source of Truth)

**Enkripsi data sensitif:**
- Password: PBKDF2 (Django default)
- Token Midtrans: disimpan apa adanya (tidak perlu dienkripsi di DB, hanya akses yang dibatasi)
- Data pelanggan (nama, telepon, alamat): tidak dienkripsi di DB (unsur kontak, bukan data finansial)

---

## 6. Catatan Keamanan & Robustness (Desain Level)

| # | Area | Catatan | Tanggung Jawab |
|---|------|---------|----------------|
| 1 | **Webhook Midtrans** | WAJIB verifikasi signature SHA-512 sebelum memproses payload — jangan percaya body mentah dari HTTP request | Engineer |
| 2 | **Webhook Midtrans (Idempotency)** | Midtrans bisa retry webhook — cek `midtrans_order_id` dan status sebelum update, jangan proses ulang | Engineer |
| 3 | **Auth** | JWT (access 15 menit + refresh 7 hari). Password hash PBKDF2 (Django default). Login rate limit: max 5 percobaan per 15 menit per IP | Engineer |
| 4 | **Cart Persistence** | Guest pakai `session_id` dari cookie, bind ke `user_id` saat login (merge cart). Session harus signed & httpOnly | Engineer |
| 5 | **Upload Gambar** | Validasi tipe file (jpg/png/webp), limit ukuran, rename filename random (anti path traversal). Yang boleh diakses publik hanya file di folder `media/products/` dan `media/store/` | Engineer |
| 6 | **SQL Injection** | Django ORM sudah aman default — jangan pakai `raw()` atau `extra()` tanpa parameterisasi. WAJIB hindari string interpolation ke query | Engineer |
| 7 | **CSRF** | Django CSRF protection WAJIB aktif untuk semua form/mutating endpoint | Engineer |
| 8 | **Rate Limiting** | Terapkan rate limiting pada: auth endpoints (brute force), checkout (spam order), upload gambar (abuse storage) | Engineer |
| 9 | **Order Stok** | Stok dikurangi saat status `paid` (bukan saat checkout). Kalau `canceled`/`expired`, stok dikembalikan otomatis. Race condition: pakai database transaction + SELECT FOR UPDATE saat kurangi stok | Engineer |
| 10 | **Webhook URL** | Webhook Midtrans (`/api/payments/webhook/`) harus bisa diakses dari internet — pastikan server punya public IP atau reverse proxy | DevOps |

---

## 7. Catatan Khusus

### 7a. Pemilihan Django (bukan Laravel)

> User memutuskan untuk menggunakan Django (Python) sebagai backend, bukan Laravel (PHP) seperti di project brief awal. Alasan: ekosistem Python lebih luas untuk data processing, dan Django menyediakan admin panel bawaan yang bisa digunakan merchant sebagai dashboard alternatif jika web frontend belum selesai.

### 7b. Frontend: Django Templates + Vanilla JS (bukan SPA)

> Untuk fase pertama, storefront dan merchant dashboard dibangun dengan Django templates + vanilla JavaScript. Ini lebih cepat dibangun, lebih ringan di deploy, dan cukup untuk semua fitur di PRD. React/Next.js TIDAK dipakai di fase ini — kecuali ada kebutuhan spesifik yang tidak bisa ditangani vanilla JS.

### 7c. Mobile App: Fase 3 (Belum Sekarang)

> React Native mobile app ada di PRD sebagai Nice to Have. Ini akan dibangun di fase terpisah SETELAH web stabil. Satu backend (Django REST API) sudah dirancang untuk melayani dua client — tidak perlu perubahan backend saat mobile app dibangun.

### 7d. Admin Panel Bawaan Django

> Django punya admin panel bawaan yang bisa diaktifkan untuk merchant. Ini useful sebagai fallback/dashboard mentah SEBELUM merchant dashboard web selesai dibangun. Bisa diaktifkan untuk development & testing.

### 7e. Deployment Strategy

**Target: VPS lokal Indonesia** (spec: 2 vCPU, 2 GB RAM, 15 GB SSD, budget ~50rb/bulan)

```
Internet
   │
   ▼
Nginx (port 80/443)
   ├── /static/  → file CSS/JS dari disk
   ├── /media/   → foto produk dari disk
   └── /         → Gunicorn (port 8000) → Django
          │
          ▼
MySQL (port 3306, localhost only)
```

**Stack deployment:**
| Komponen | Cara | Catatan |
|----------|------|--------|
| Nginx | Reverse proxy + static files | Static files & media dilayani langsung oleh Nginx (bukan Django) |
| Gunicorn | WSGI server untuk Django | 2-3 worker (sesuai RAM 2GB) |
| MySQL | Database | Hanya diakses dari localhost, tidak expose ke internet |
| Django | Backend | Virtual environment, not as container |

**Security deployment:**
- MySQL: hanya listen localhost — tidak ada port yang dibuka ke internet selain 80/443
- Gunicorn: hanya listen localhost:8000 — Nginx yang forward
- SSH: port 22, non-root login, password auth OFF (pakai key saja)
- Firewall: buka port 80, 443, 22 saja

**Domain & SSL:**
- Fase awal: akses via IP langsung (`http://IP_VPS/`)
- SSL: Let's Encrypt via Certbot (pas domain sudah ada)
- Domain: belum ditentukan — beli saat siap launch

**File Gambar:**
- Fase development: pakai placeholder dari internet (unsplash/placeholder.com)
- Fase production: upload foto produk ke disk VPS (`media/products/`)
- Nanti (kalau scale): migrasi ke S3-compatible storage

**Backup:**
- Cron harian: `mysqldump` → kompres → upload ke Google Drive / S3
- Media files: rsync ke storage backup mingguan

**Monitoring (basic):**
- `htop` untuk cek resource usage
- `journalctl` untuk cek log Django/Gunicorn
- UptimeRobot (gratis) untuk cek server hidup/mati

### 7f. API Versioning

> Semua endpoint API menggunakan prefix `/api/v1/`. Ini memudahkan migrasi di masa depan tanpa breaking change.

---

## 8. Riwayat Perubahan

| Versi | Tanggal | Perubahan | ADR terkait |
|-------|---------|-----------|-------------|
| v1 | 2025-08-25 | Desain awal: Django backend + MySQL + vanilla JS web + Midtrans, multi-merchant, 15 entitas | - |
| v1.1 | 2025-08-25 | Update Deployment Strategy: VPS lokal 2GB/2core/15GB, Gunicorn+Nginx+systemd, domain belum, gambar placeholder | ADR-001 |

---

> **Arsitektur sudah di-freeze.** Silakan panggil Engineer untuk mulai koding, atau DevOps untuk setup infrastruktur.
