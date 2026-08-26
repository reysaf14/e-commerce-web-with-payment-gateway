# Implementation Plan — Platform E-Commerce Mandiri Fashion Wanita

> **Dokumen ini** menjadi panduan kerja Engineer per fase. Setiap milestone harus **selesai dan diverifikasi** sebelum lanjut ke milestone berikutnya.

---

## Timeline Ringkas

| Milestone | Nama | Focus Area |
|-----------|------|-----------|
| M0 | Project Foundation | Setup Django, semua model, database, config |
| M1 | Authentication & Store | Register, login, JWT, pengaturan toko |
| M2 | Product Management | CRUD produk, varian, foto, kategori |
| M3 | Storefront Publik | Halaman toko yang bisa dilihat pembeli |
| M4 | Cart & Checkout | Keranjang persisten, form checkout, buat order |
| M5 | Payment Integration | Midtrans Snap, webhook, verifikasi, stok |
| M6 | Merchant Dashboard | Kelola pesanan, CRM, notifikasi, cetak |
| M7 | Nice-to-Have | Review, wishlist, promo, analytics |
| M8 | Testing & Review | Unit test, flow test, code review, security check |

---

## M0 — Project Foundation

### Goal
Backend bisa jalan, semua model tercipta, database siap — tapi belum ada fitur bisnis sama sekali.

### Deliverables
| # | File/Task | Catatan |
|---|-----------|---------|
| 1 | Django project `config/` + apps | Ikuti struktur folder dari architecture.md |
| 2 | `requirements.txt` | Semua dependency dari architecture.md section 4a |
| 3 | `config/settings/base.py` | Installed apps, middleware, REST framework config, JWT config, media config, CORS |
| 4 | `config/settings/development.py` | DEBUG=True, SQLite fallback untuk dev lokal |
| 5 | `config/settings/production.py` | MySQL config dari .env, static files, security headers |
| 6 | `config/.env.template` | Semua environment variables dari architecture.md section 4b |
| 7 | **Semua models.py** (15 entitas) | Ikuti SSOT **persis** — field names, tipe, constraint, indeks |
| 8 | `manage.py` | Standard Django manage.py |
| 9 | `config/urls.py` | Root URL routing ke semua apps |
| 10 | `docker-compose.yml` | MySQL 8.0 saja (bukan full stack) |
| 11 | `.gitignore` | Standard Python/Django gitignore |
| 12 | `media/.gitkeep` | Agar folder media ter-tracked |

### Verification (fungsional dasar)
- [ ] `python manage.py check` → 0 errors
- [ ] `python manage.py makemigrations --check` → tidak ada migration tertinggal
- [ ] `python manage.py migrate` → berhasil (SQLite untuk dev)
- [ ] `python -m py_compile` → semua file .py baru lolos

### Catatan Keamanan (dari architecture.md section 6)
- Password hash: PBKDF2 (Django default)
- CSRF protection: aktif di settings
- File upload: validasi tipe & ukuran (siap di models/signals)
- Rate limiting: siap di settings (akan diaktifkan di M1)

---

## M1 — Authentication & Store Settings

### Goal
Merchant bisa daftar, login, logout, dan mengatur toko (nama, logo, ongkir, kebijakan). Ini fondasi untuk semua fitur merchant.

### Deliverables
| # | File/Task | Catatan |
|---|-----------|---------|
| 1 | `authentication/serializers.py` | Register serializer, Login serializer (email+password), User profile |
| 2 | `authentication/views.py` | RegisterView, LoginView (return JWT access+refresh), RefreshView, MeView |
| 3 | `authentication/permissions.py` | IsMerchant permission class |
| 4 | `authentication/urls.py` | `/api/v1/auth/register/`, `/login/`, `/refresh/`, `/me/` |
| 5 | `store/serializers.py` | StoreSettings serializer (read + update) |
| 6 | `store/views.py` | StoreSettingsView (GET/PUT) — merchant only |
| 7 | `store/urls.py` | `/api/v1/settings/` |
| 8 | Rate limiting | Aktifkan throttling di REST framework settings: AnonRateType '5/minute' untuk login |

### Verification (fungsional dasar)
- [ ] Daftar user baru → otomatis buat StoreSettings
- [ ] Login → terima JWT token
- [ ] GET `/api/v1/settings/` dengan token → data toko muncul
- [ ] Tanpa token → 401
- [ ] Login rate limit aktif

---

## M2 — Product Management

### Goal
Merchant bisa kelola katalog produk penuh: CRUD produk, varian, foto, dan kategori.

### Deliverables
| # | File/Task | Catatan |
|---|-----------|---------|
| 1 | `products/serializers.py` | Product serializer (nested: category, variants, images), Category serializer |
| 2 | `products/views.py` | ProductViewSet (CRUD), CategoryViewSet, ImageUploadView |
| 3 | `products/urls.py` | `/api/v1/products/`, `/api/v1/categories/` |
| 4 | `products/filters.py` | Filter produk: kategori, harga, status, is_featured |
| 5 | Upload gambar | Validasi: jpg/png/webp, max 5MB, rename random filename |
| 6 | Auto-generate slug | Dari nama produk → slug unik per toko |

### Verification (fungsional dasar)
- [ ] Tambah produk dengan 3 varian, 4 foto → cek di DB
- [ ] Upload gambar .exe → ditolak; .jpg > 5MB → ditolak
- [ ] Filter produk by kategori → hasil sesuai

---

## M3 — Storefront Publik

### Goal
Pembeli bisa melihat toko: beranda, katalog, detail produk. Toko harus terlihat "enak dipandang" dengan claymorphism accent.

### Deliverables
| # | File/Task | Catatan |
|---|-----------|---------|
| 1 | `store/views.py` (public) | StorefrontView: GET info toko, GET produk公众, GET detail公众 |
| 2 | `store/serializers.py` (public) | StorePublicSerializer, ProductPublicSerializer |
| 3 | `store/urls.py` (public) | `/api/v1/store/`, `/api/v1/store/products/`, `/api/v1/store/products/<slug>/` |
| 4 | `templates/base.html` | Base template: navbar, footer, meta tags |
| 5 | `templates/store/home.html` | Hero banner, produk unggulan, kategori populer |
| 6 | `templates/store/catalog.html` | Grid katalog, filter kategori, sort, search, pagination |
| 7 | `templates/store/product_detail.html` | Galeri foto, pilihan varian, stok, deskripsi, tombol "Tambah ke Keranjang" |
| 8 | `static/css/base.css` | Design system: palette warna hangat, tipografi, spacing |
| 9 | `static/css/claymorphism.css` | Accent: kartu produk, tombol CTA, badge |
| 10 | `static/css/responsive.css` | Mobile-first breakpoints |
| 11 | `static/js/app.js` | Router SPA-lite untuk navigasi antar halaman tanpa reload |
| 12 | `static/js/utils.js` | Fetch wrapper (dengan JWT header), toast notification, loading skeleton |

### Verification (fungsional dasar)
- [ ] Buka `/` → beranda tampil
- [ ] Buka `/catalog` → grid produk muncul dengan filter & sort
- [ ] Klik produk → detail produk tampil
- [ ] Resize browser ke 360px → layout menyesuaikan

---

## M4 — Cart & Checkout

### Goal
Pembeli bisa tambah produk ke keranjang, ubah jumlah, isi form checkout, dan membuat pesanan (sebelum bayar).

### Deliverables
| # | File/Task | Catatan |
|---|-----------|---------|
| 1 | `cart/serializers.py` | CartSerializer, CartItemSerializer |
| 2 | `cart/views.py` | CartView (GET/DELETE), AddItemView, UpdateItemView, RemoveItemView |
| 3 | `cart/urls.py` | `/api/v1/cart/`, `/api/v1/cart/items/` |
| 4 | `orders/serializers.py` | OrderSerializer, CreateOrderSerializer |
| 5 | `orders/views.py` | CreateOrderView (checkout), OrderConfirmationView |
| 6 | `orders/urls.py` | `/api/v1/checkout/`, `/api/v1/orders/<order_number>/` |
| 7 | `orders/utils.py` | Generate order_number (TKN-YYYYMMDD-XXXX), hitung subtotal & total |
| 8 | `templates/checkout/cart.html` | Keranjang: item, qty, subtotal, hapus item |
| 9 | `templates/checkout/payment.html` | Form checkout: pengiriman, ringkasan, pilih metode bayar |
| 10 | `templates/order/confirmation.html` | Konfirmasi order: detail, status, instruksi bayar |
| 11 | `static/js/cart.js` | Logic cart: tambah, ubah qty, hapus, hitung total |
| 12 | `static/js/checkout.js` | Logic checkout: validasi form, submit order |

### Verification (fungsional dasar)
- [ ] Tambah item ke cart → item muncul
- [ ] Ubah qty → total berubah
- [ ] Checkout → order baru tercipta dengan status `waiting_payment`
- [ ] Cek order di DB → order_number unik, data snapshot lengkap

---

## M5 — Payment Integration (Midtrans)

### Goal
Pembeli bisa bayar via Midtrans (VA, e-wallet, QRIS), status order otomatis update via webhook, stok otomatis dikurangi.

### Deliverables
| # | File/Task | Catatan |
|---|-----------|---------|
| 1 | `payments/midtrans_client.py` | Wrapper API: create_transaction(), check_status() |
| 2 | `payments/views.py` | CreatePaymentView (buat snap token), WebhookView (tanpa auth) |
| 3 | `payments/urls.py` | `/api/v1/payments/create/`, `/api/v1/payments/webhook/` |
| 4 | **Webhook handler** | Verifikasi signature SHA-512, idempotency check, update order status |
| 5 | **Stok management** | Order paid → kurangi stok (SELECT FOR UPDATE); order canceled/expired → kembalikan stok |
| 6 | **Notifikasi** | Order paid → notifikasi ke merchant + pembeli; order expired → notifikasi ke pembeli |
| 7 | `notifications/services.py` | Fungsi kirim notifikasi: create_notification() |

### Verification (fungsional dasar)
- [ ] Checkout → dapat snap_token
- [ ] Webhook Midtrans sandbox → order status = `paid`
- [ ] Order `paid` → stok berkurang
- [ ] Webhook yang sama 2x → tidak double-proses
- [ ] Notifikasi tercipta

---

## M6 — Merchant Dashboard

### Goal
Merchant bisa mengelola pesanan, melihat data pelanggan, menerima notifikasi, dan mencetak struk/label.

### Deliverables
| # | File/Task | Catatan |
|---|-----------|---------|
| 1 | `orders/views.py` (merchant) | OrderListView (filter by status, tanggal), OrderDetailView, UpdateStatusView, UpdateTrackingView |
| 2 | `customers/views.py` | CustomerListView, CustomerDetailView, CustomerExportView |
| 3 | `customers/exporters.py` | Export CSV: nama, telepon, email, total belanja, frekuensi, terakhir beli |
| 4 | `notifications/views.py` | NotificationListView, MarkAsReadView |
| 5 | `templates/merchant/dashboard.html` | Ringkasan: pesanan masuk hari ini, notifikasi, akses cepat |
| 6 | `templates/merchant/order_list.html` | Daftar pesanan dengan filter status & tanggal |
| 7 | `templates/merchant/customer_list.html` | Daftar pelanggan, tombol export CSV |
| 8 | `templates/order/tracking.html` | Pembeli: lacak pesanan via order_number |
| 9 | **Cetak struk & label** | Fungsi utils: generate_receipt_html() & generate_label_html() → print via browser |
| 10 | **Notifikasi badge** | Tampilkan jumlah notifikasi belum dibaca di navbar dashboard |

### Verification (fungsional dasar)
- [ ] Dashboard tampil dengan pesanan terbaru
- [ ] Filter pesanan by status → hasil sesuai
- [ ] Ubah status Dibayar → Dikemas → berhasil
- [ ] Export CSV → file terdownload
- [ ] Pembeli lacak pesanan via order_number

---

## M7 — Nice-to-Have

### Goal
Fitur-fitur tambahan yang menambah value tanpa menjadi blocker launch.

### Deliverables (berdasarkan PRD Nice to Have, diurutkan prioritas)
| # | Fitur | Catatan |
|---|-------|---------|
| 1 | Ulasan Produk (Review) | Rating 1-5 + komentar, tampil di halaman produk, hanya bisa setelah order selesai |
| 2 | Wishlist | Simpan produk favorit, toggle di halaman detail, tampil di halaman khusus |
| 3 | Kode Promo / Diskon | Kode unik, persentase/nominal, minimum belanja, batas penggunaan, kadaluarsa |
| 4 | Dashboard Analitik | Grafik penjualan harian/bulanan, produk terlaris, AOV |
| 5 | Mode "Catalog Only" | Toggle: tampilkan produk tapi transaksi lewat WA/direct |
| 6 | Poin Loyalitas | Poin per belanja, tukar poin jadi potongan harga |

### Verification (fungsional dasar)
- [ ] Review bisa ditambah → rating muncul di produk
- [ ] Wishlist bisa ditambah/dihapus
- [ ] Kode promo diterapkan → harga berkurang
- [ ] Dashboard analitik tampil

---

## M8 — Testing & Review

### Goal
Full test keseluruhan sistem: unit test, flow test, code review, security check. Tidak ada kode baru di milestone ini — hanya verifikasi dan perbaikan.

### Deliverables
| # | Task | Catatan |
|---|------|---------|
| 1 | **Unit Test lengkap** | Buat/test semua model, serializer, view di setiap app |
| 2 | **Flow Test End-to-End** | Simulasi: daftar → atur toko → tambah produk → pembeli belanja → bayar → status update → selesai |
| 3 | **Code Review** | Cek konsistensi: error handling, logging, naming, struktur file |
| 4 | **Security Review** | Verifikasi: webhook signature, rate limiting, upload validation, CSRF, auth check di semua endpoint |
| 5 | **Performance Check** | Lighthouse score, loading time, query optimization |
| 6 | **Fix dari temuan** | Perbaiki semua bug/temuan yang ditemukan |

### Checklist Review

**Unit Test:**
- [ ] `python manage.py test` → semua PASS
- [ ] Coverage minimal: models, serializers, views, utils

**Flow Test:**
- [ ] Merchant: daftar → login → atur toko → tambah produk → lihat pesanan → ubah status → export CSV
- [ ] Pembeli: browse katalog → detail produk → tambah cart → checkout → bayar (sandbox) → konfirmasi → lacak pesanan
- [ ] Webhook: kirim mock webhook → cek order status, stok, notifikasi

**Code Review:**
- [ ] Error handling di semua endpoint API
- [ ] Logging untuk setiap aksi kritis
- [ ] Tidak ada hardcoded secret (semua dari .env)
- [ ] Tidak ada `raw()`/`extra()` tanpa parameterisasi

**Security Review:**
- [ ] Webhook Midtrans: signature SHA-512 diverifikasi
- [ ] Rate limiting aktif di auth & checkout
- [ ] Upload gambar: tipe & ukuran tervalidasi
- [ ] CSRF protection aktif untuk semua form
- [ ] Auth check: tidak ada endpoint merchant yang bisa diakses tanpa token
- [ ] Stok: race condition dicek (SELECT FOR UPDATE)

**Performance:**
- [ ] Lighthouse: Performance ≥ 80, Accessibility ≥ 90
- [ ] Tidak ada N+1 query di halaman katalog
- [ ] Loading time < 3 detik di jaringan 4G (simulasi)

### Catatan
- Milestone ini dilakukan SETELAH semua fitur selesai (M0-M7)
- Jika ada temuan: Engineer perbaiki, lalu QA/Security review ulang
- Tidak ada fitur baru — hanya fix & polish

---

## Dependency Setiap Milestone

| Milestone | Dependency |
|-----------|-----------|
| M0 | Tidak ada (fondasi) |
| M1 | M0 |
| M2 | M0, M1 |
| M3 | M0, M2 (perlu data produk untuk storefront) |
| M4 | M0, M1, M2 (perlu produk + auth untuk cart & checkout) |
| M5 | M4 (perlu order untuk payment) |
| M6 | M4, M5 (perlu order & payment untuk dashboard) |
| M7 | M4, M5, M6 (perlu semua fitur inti) |
| M8 | M0 s/d M7 (semua fitur selesai) |

---

## Riwayat Perubahan

| Versi | Tanggal | Perubahan |
|-------|---------|-----------|
| v1 | 2025-08-25 | Implementation plan awal: 8 milestone (M0-M7) |
| v1.1 | 2025-08-25 | Tambah M8 (Testing & Review) sebagai fase terpisah; setiap milestone hanya verifikasi fungsional dasar |
