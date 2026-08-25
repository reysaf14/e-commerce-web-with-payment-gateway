# SSOT — Database Design: Platform E-Commerce Mandiri Fashion Wanita

> **Single Source of Truth (SSOT)** — Dokumen ini adalah satu-satunya rujukan untuk semua entitas data, relasi, tipe field, constraint, dan indeks. Semua agent (Engineer, QA, Security) WAJIB merujuk ke dokumen ini saat bekerja dengan data. Kalau ada perbedaan antara SSOT ini dan kode — **SSOT yang benar**.

---

## Ringkasan Entitas

| # | Entitas | Fungsi Utama | Relation |
|---|---------|-------------|----------|
| 1 | User | Akun merchant yang mengelola toko | → StoreSettings (1:1), → Product, → Order (sebagai store owner) |
| 2 | StoreSettings | Pengaturan branding & operasional toko | → User (1:1) |
| 3 | Category | Kategori produk | → StoreSettings (N:1), → Product (1:N) |
| 4 | Product | Produk yang dijual | → StoreSettings (N:1), → Category (N:1) |
| 5 | Variant | Varian produk (ukuran/warna) | → Product (N:1) |
| 6 | ProductImage | Foto produk (multiple per produk) | → Product (N:1) |
| 7 | Cart | Keranjang belanja (persisten) | → Session/User |
| 8 | CartItem | Item dalam keranjang | → Cart (N:1), → Variant (N:1) |
| 9 | Customer | Profil pelanggan (CRM) | → StoreSettings (N:1) |
| 10 | Order | Pesanan | → StoreSettings (N:1), → Customer (N:1) |
| 11 | OrderItem | Item dalam pesanan (snapshot data produk) | → Order (N:1), → Variant (N:1, snapshot) |
| 12 | Payment | Record transaksi pembayaran | → Order (1:1) |
| 13 | Notification | Notifikasi ke merchant/pembeli | → StoreSettings (N:1) |
| 14 | ProductReview | Ulasan & rating produk | → Product (N:1), → OrderItem (N:1) |
| 15 | Wishlist | Produk yang disimpan pembeli | → Product (N:1) |

---

## 1. User

> Akun merchant. Hanya merchant yang daftar — pembeli tidak perlu daftar (guest checkout).

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | UUID / BigAutoField | PK | Auto-generated |
| `email` | EmailField | UNIQUE, NOT NULL | Login identifier |
| `password_hash` | CharField(255) | NOT NULL | PBKDF2/bcrypt — JANGNA plain text |
| `full_name` | CharField(150) | NOT NULL | Nama lengkap merchant |
| `phone` | CharField(20) | NULLABLE | Telepon merchant |
| `role` | CharField(20) | DEFAULT='merchant' | Hanya 'merchant' untuk saat ini |
| `is_active` | BooleanField | DEFAULT=True | Soft disable akun |
| `created_at` | DateTimeField | AUTO_NOW_ADD | Waktu daftar |
| `updated_at` | DateTimeField | AUTO_NOW | Terakhir update |

**Indeks:**
- `email` — UNIQUE (login lookup)

---

## 2. StoreSettings

> Satu merchant = satu toko. Nama toko, logo, ongkir, kebijakan.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `user_id` | BigAutoField | FK → User, UNIQUE | One-to-one dengan User |
| `store_name` | CharField(200) | NOT NULL | Nama toko tampil di storefront |
| `slug` | SlugField(200) | UNIQUE, NOT NULL | URL-friendly: toko-kamu |
| `logo_url` | ImageField | NULLABLE | Logo toko |
| `favicon_url` | ImageField | NULLABLE | Favicon |
| `description` | TextField | NULLABLE | Deskripsi singkat toko |
| `whatsapp_number` | CharField(20) | NULLABLE | Format: 628xxxxxxxxxx |
| `email_contact` | EmailField | NULLABLE | Email kontak toko |
| `instagram_handle` | CharField(100) | NULLABLE | Tanpa @ |
| `return_policy` | TextField | NULLABLE | Kebijakan pengembalian |
| `shipping_policy` | TextField | NULLABLE | Kebijakan pengiriman |
| `shipping_method` | CharField(50) | DEFAULT='flat_rate' | 'flat_rate' / 'per_kota' / 'gratis_ons' |
| `shipping_cost` | DecimalField(10,2) | DEFAULT=0 | Ongkir flat atau dasar |
| `free_shipping_min` | DecimalField(10,2) | NULLABLE | Gratis ongkir di atas nominal ini |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |
| `updated_at` | DateTimeField | AUTO_NOW | |

**Indeks:**
- `user_id` — UNIQUE (1:1 constraint)
- `slug` — UNIQUE (URL lookup)

---

## 3. Category

> Kategori/koleksi produk milik satu toko.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `store_id` | BigAutoField | FK → StoreSettings, NOT NULL | Milik toko mana |
| `name` | CharField(100) | NOT NULL | "Musim Panas", "Hijab Cerut" |
| `slug` | SlugField(120) | NOT NULL | URL-friendly |
| `sort_order` | IntegerField | DEFAULT=0 | Urutan tampil (0=atas) |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |

**Indeks:**
- `(store_id, slug)` — UNIQUE COMPOSITE (satu toko, slug kategori unik)
- `store_id` — INDEX (filter by toko)

---

## 4. Product

> Produk utama. Harga default ada di sini; varian bisa override.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `store_id` | BigAutoField | FK → StoreSettings, NOT NULL | Milik toko mana |
| `category_id` | BigAutoField | FK → Category, NULLABLE | Bisa kosong (tanpa kategori) |
| `name` | CharField(255) | NOT NULL | Nama produk |
| `slug` | SlugField(280) | NOT NULL | URL-friendly |
| `description` | TextField | NULLABLE | Deskripsi panjang |
| `price` | DecimalField(10,2) | NOT NULL | Harga default (Rp) |
| `is_active` | BooleanField | DEFAULT=True | Hidden dari storefront kalau False |
| `is_featured` | BooleanField | DEFAULT=False | Tampil di hero/unggulan |
| `total_sold` | IntegerField | DEFAULT=0 | Counter untuk "terlaris" |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |
| `updated_at` | DateTimeField | AUTO_NOW | |

**Indeks:**
- `(store_id, slug)` — UNIQUE COMPOSITE
- `(store_id, is_active, created_at)` — composite untuk katalog query
- `(store_id, is_featured)` — hero/featured query
- `category_id` — filter by kategori

---

## 5. Variant

> Varian produk: kombinasi ukuran/warna. Stok dihitung per varian.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `product_id` | BigAutoField | FK → Product, NOT NULL | Milik produk mana |
| `name` | CharField(150) | NOT NULL | "Merah - M", "Putih - L" |
| `sku` | CharField(50) | NULLABLE | SKU internal merchant |
| `price_override` | DecimalField(10,2) | NULLABLE | Kalau NULL → pakai `price` dari Product |
| `stock` | IntegerField | DEFAULT=0 | Stok tersedia |
| `is_active` | BooleanField | DEFAULT=True | |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |

**Aturan Bisnis:**
- Harga jual varian = `price_override` jika ada, else `product.price`
- Stok habis otomatis: `stock = 0` → tampil "habis" di storefront
- Stok dikurangi otomatis saat order DIBAYAR (bukan saat checkout)

**Indeks:**
- `(product_id, is_active)` — filter varian aktif per produk
- `sku` — UNIQUE per toko (cara: UNIQUE COMPOSITE `(product_id, sku)` atau cek di aplikasi)

---

## 6. ProductImage

> Multiple foto per produk. Ada urutan tampil.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `product_id` | BigAutoField | FK → Product, NOT NULL | |
| `image_url` | ImageField | NOT NULL | Path file gambar |
| `sort_order` | IntegerField | DEFAULT=0 | Urutan galeri |
| `alt_text` | CharField(255) | NULLABLE | Teks alternatif (SEO + aksesibilitas) |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |

**Aturan Bisnis:**
- Gambar pertama (sort_order=0) = thumbnail di katalog
- Batas maksimal: 8 gambar per produk (validasi di aplikasi)

**Indeks:**
- `(product_id, sort_order)` — galeri urut

---

## 7. Cart

> Keranjang belanja. Bisa guest (pakai session_id) atau user login.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `session_id` | CharField(64) | NULLABLE | ID sesi browser untuk guest |
| `user_id` | BigAtrophyField | FK → User, NULLABLE | NULL kalau guest |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |
| `updated_at` | DateTimeField | AUTO_NOW | |

**Aturan Bisnis:**
- Guest: `session_id` diisi, `user_id` NULL
- Login: `user_id` diisi — kalau ada cart guest, merge otomatis
- Cart expired otomatis: lebih dari 7 hari tanpa aktivitas → hapus

**Indeks:**
- `session_id` — INDEX (guest lookup)
- `user_id` — UNIQUE (satu user = satu cart aktif)

---

## 8. CartItem

> Item dalam keranjang. Satu varian per item.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `cart_id` | BigAutoField | FK → Cart, NOT NULL | |
| `variant_id` | BigAutoField | FK → Variant, NOT NULL | |
| `quantity` | IntegerField | DEFAULT=1, MIN=1 | |
| `added_at` | DateTimeField | AUTO_NOW_ADD | |

**Aturan Bisnis:**
- Quantity tidak boleh melebihi stok varian (validasi saat tambah + saat checkout)
- Kalau varian dihapus/ non-aktif → item otomatis dihapus dari cart

**Indeks:**
- `(cart_id, variant_id)` — UNIQUE COMPOSITE (satu varian = satu baris di cart)

---

## 9. Customer

> Profil pelanggan (CRM ringan). Diisi otomatis dari data checkout — pelanggan tidak daftar.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `store_id` | BigAutoField | FK → StoreSettings, NOT NULL | Data pelanggan per toko |
| `full_name` | CharField(150) | NOT NULL | Nama dari form checkout |
| `email` | EmailField | NULLABLE | Bisa kosong jika tidak diisi |
| `phone` | CharField(20) | NOT NULL | Nomor WhatsApp/telepon |
| `address` | TextField | NULLABLE | Alamat terakhir |
| `city` | CharField(100) | NULLABLE | Kota |
| `postal_code` | CharField(10) | NULLABLE | Kode pos |
| `total_spent` | DecimalField(12,2) | DEFAULT=0 | Akumulasi belanja |
| `order_count` | IntegerField | DEFAULT=0 | Jumlah pesanan |
| `last_order_at` | DateTimeField | NULLABLE | Pesanan terakhir |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |
| `updated_at` | DateTimeField | AUTO_NOW | |

**Aturan Bisnis:**
- Pelanggan diidentifikasi gabungan `(store_id, phone)` — satu nomor HP = satu profil per toko
- Saat checkout, sistem cek apakah phone sudah ada → update profil, kalau belum → buat baru
- `total_spent` dan `order_count` di-update otomatis setiap order SELESAI

**Indeks:**
- `(store_id, phone)` — UNIQUE COMPOSITE (identifikasi unik pelanggan per toko)
- `(store_id, last_order_at)` — untuk filter pelanggan aktif

---

## 10. Order

> Pesanan dari pembeli. Status berubah mengikuti state machine.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `store_id` | BigAutoField | FK → StoreSettings, NOT NULL | |
| `customer_id` | BigAutoField | FK → Customer, NOT NULL | |
| `order_number` | CharField(30) | UNIQUE, NOT NULL | Nomor urut: TKN-20250825-0001 |
| `status` | CharField(20) | DEFAULT='waiting_payment' | Lihat state machine |
| `subtotal` | DecimalField(12,2) | NOT NULL | Total harga item |
| `shipping_cost` | DecimalField(10,2) | DEFAULT=0 | Ongkir |
| `total_amount` | DecimalField(12,2) | NOT NULL | subtotal + shipping_cost |
| `shipping_name` | CharField(150) | NOT NULL | Nama penerima |
| `shipping_phone` | CharField(20) | NOT NULL | Telepon penerima |
| `shipping_address` | TextField | NOT NULL | Alamat lengkap |
| `shipping_city` | CharField(100) | NOT NULL | Kota tujuan |
| `shipping_postal_code` | CharField(10) | NULLABLE | Kode pos |
| `note_to_seller` | TextField | NULLABLE | Catatan pembeli untuk penjual |
| `payment_method` | CharField(50) | NULLABLE | VA, e-wallet, QRIS (diisi setelah bayar) |
| `payment_status` | CharField(20) | DEFAULT='pending' | pending / success / failed / expired |
| `tracking_number` | CharField(100) | NULLABLE | Nomor resi ekspedisi |
| `shipping_courier` | CharField(50) | NULLABLE | Nama ekspedisi |
| `shipped_at` | DateTimeField | NULLABLE | Waktu dikirim |
| `delivered_at` | DateTimeField | NULLABLE | Waktu diterima/selesai |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |
| `updated_at` | DateTimeField | AUTO_NOW | |

### Order Status — State Machine

```
waiting_payment → paid → shipped → delivered → completed
                  │        │
                  ↓        ↓
               failed    canceled
               expired
```

| Status | Arti | Siapa yang trigger |
|--------|------|-------------------|
| `waiting_payment` | Menunggu pembayaran | Otomatis saat order dibuat |
| `paid` | Pembayaran berhasil | Webhook Midtrans |
| `shipped` | Pesanan dikirim (resi sudah diinput) | Merchant |
| `delivered` | Diterima pembeli | Merchant atau auto-setelah X hari |
| `completed` | Selesai | Otomatis setelah delivered + X hari |
| `failed` | Pembayaran gagal | Webhook Midtrans |
| `expired` | Pembayaran expired | Webhook Midtrans atau scheduler |
| `canceled` | Dibatalkan | Merchant (sebelum bayar) atau auto (7 hari tanpa bayar) |

**Aturan Bisnis:**
- `order_number` format: `TKN-{YYYYMMDD}-{4-digit sequence}` → TKN-20250825-0001
- Order yang status `waiting_payment` > 7 hari → otomatis `expired`
- Order baru dibuat → stok TIDAK dikurangi (speculative hold tidak ada)
- Order status `paid` → stok varian DIKURANGI otomatis
- Order `canceled`/`expired` → stok DIKEMBALIKAN otomatis
- `total_amount` WAJIB = `subtotal` + `shipping_cost` (validasi di aplikasi)

**Indeks:**
- `order_number` — UNIQUE
- `(store_id, status)` — filter pesanan per status
- `(store_id, created_at)` — filter by tanggal
- `customer_id` — riwayat pesanan pelanggan
- `payment_status` — filter pending payment

---

## 11. OrderItem

> Item dalam pesanan. **Snapshot data produk** — kalau produk dihapus/harga berubah, data di sini tetap.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `order_id` | BigAutoField | FK → Order, NOT NULL | |
| `product_id` | BigAutoField | FK → Product, NULLABLE | NULL kalau produk sudah dihapus |
| `variant_id` | BigAutoField | FK → Variant, NULLABLE | NULL kalau varian sudah dihapus |
| `product_name` | CharField(255) | NOT NULL | SNAPSHOT nama produk |
| `variant_name` | CharField(150) | NULLABLE | SNAPSHOT nama varian |
| `unit_price` | DecimalField(10,2) | NOT NULL | SNAPSHOT harga saat beli |
| `quantity` | IntegerField | NOT NULL | Jumlah dibeli |
| `subtotal` | DecimalField(12,2) | NOT NULL | unit_price × quantity |

**Aturan Bisnis:**
- Data snapshot WAJIB diisi saat order dibuat (copy dari Product/Variant saat itu)
- `subtotal` = `unit_price` × `quantity` — dihitung saat dibuat, tidak berubah

**Indeks:**
- `order_id` — filter items per order

---

## 12. Payment

> Record transaksi pembayaran. Satu order = satu atau lebih record (bayar ulang).

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `order_id` | BigAutoField | FK → Order, NOT NULL | |
| `midtrans_order_id` | CharField(100) | NOT NULL | ID dari Midtrans |
| `midtrans_token` | CharField(255) | NULLABLE | Snap token |
| `amount` | DecimalField(12,2) | NOT NULL | Nominal dibayar |
| `payment_type` | CharField(50) | NULLABLE | bank_transfer, e-wallet, qris, dll |
| `status` | CharField(20) | NOT NULL | pending / success / failed / expired |
| `fraud_status` | CharField(20) | NULLABLE | accept / challenge / deny |
| `raw_response` | JSONField | NULLABLE | JSON lengkap dari Midtrans (untuk debugging) |
| `paid_at` | DateTimeField | NULLABLE | Waktu pembayaran berhasil |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |

**Aturan Bisnis:**
- Webhook Midtrans bisa dikirim ulang → cek `midtrans_order_id` + `status` sebelum proses (idempotency)
- `raw_response` WAJIB disimpan apa adanya — ini audit trail
- Satu order bisa punya beberapa Payment record (jika bayar ulang setelah expired)

**Indeks:**
- `midtrans_order_id` — INDEX (webhook lookup — PALING KRITIS)
- `(order_id, status)` — filter payment per order
- `status` — filter pending payment untuk scheduler

---

## 13. Notification

> Notifikasi in-app ke merchant atau pembeli.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `store_id` | BigAutoField | FK → StoreSettings, NOT NULL | |
| `recipient_type` | CharField(20) | NOT NULL | 'merchant' / 'customer' |
| `recipient_id` | BigAutoField | NOT NULL | ID user atau customer |
| `type` | CharField(30) | NOT NULL | order_paid, order_shipped, dll |
| `title` | CharField(200) | NOT NULL | Judul notifikasi |
| `message` | TextField | NOT NULL | Isi notifikasi |
| `is_read` | BooleanField | DEFAULT=False | Sudah dibaca atau belum |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |

**Tipe Notifikasi:**

| Type | Recipient | Trigger |
|------|-----------|---------|
| `order_new` | Merchant | Pesanan baru masuk (waiting_payment) |
| `order_paid` | Merchant + Customer | Pembayaran berhasil |
| `order_shipped` | Customer | Pesanan dikirim |
| `order_delivered` | Customer | Pesanan diterima |
| `order_canceled` | Customer | Pesanan dibatalkan |
| `order_expired` | Customer | Pembayaran expired |

**Indeks:**
- `(recipient_type, recipient_id, is_read)` — notifikasi belum dibaca
- `(store_id, created_at)` — notifikasi merchant berdasarkan waktu

---

## 14. ProductReview

> Ulasan & rating dari pembeli. Hanya bisa setelah pesanan SELESAI.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `product_id` | BigAutoField | FK → Product, NOT NULL | |
| `order_item_id` | BigAutoField | FK → OrderItem, UNIQUE | Satu ulasan per item dibeli |
| `rating` | IntegerField | 1–5, NOT NULL | Bintang 1-5 |
| `comment` | TextField | NULLABLE | Ulasan tulis |
| `is_anonymous` | BooleanField | DEFAULT=False | Tampilkan nama atau tidak |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |

**Aturan Bisnis:**
- Hanya bisa review kalau order-nya sudah `delivered` atau `completed`
- Satu order_item hanya bisa di-review sekali (UNIQUE di `order_item_id`)
- Rata-rata rating produk = dihitung on-the-fly dari tabel ini, tidak disimpan di Product

**Indeks:**
- `order_item_id` — UNIQUE (satu review per item)
- `(product_id, created_at)` — ulasan produk terbaru

---

## 15. Wishlist

> Produk yang disimpan pembeli tanpa beli langsung.

| Field | Tipe | Constraint | Catatan |
|-------|------|-----------|---------|
| `id` | BigAutoField | PK | |
| `session_id` | CharField(64) | NOT NULL | Identifikasi pembeli (guest atau login) |
| `product_id` | BigAutoField | FK → Product, NOT NULL | |
| `created_at` | DateTimeField | AUTO_NOW_ADD | |

**Aturan Bisnis:**
- Guest: pakai `session_id` dari cookie
- Bisa disimpan/dihapus tanpa login
- Batas wishlist: tidak dibatasi (tapi dapatkan arsitektur paginate)

**Indeks:**
- `(session_id, product_id)` — UNIQUE COMPOSITE (cek sudah wishlist atau belum)
- `session_id` — INDEX (daftar wishlist per pembeli)

---

## ERD Visual (Teks)

```
User ──1:1── StoreSettings ──1:N── Category
                   │                     │
                   │                     └──1:N── Product ──1:N── Variant
                   │                          │                    │
                   │                          ├──1:N── ProductImage │
                   │                          │                     │
                   │                          └──1:N── ProductReview│
                   │                                                │
                   ├──1:N── Customer ──1:N── Order ──1:1── Payment  │
                   │                    │     │                     │
                   │                    │     └──1:N── OrderItem ───┘
                   │                    │
                   ├──1:N── Notification │
                   │                     │
                   └─────────────────────┘

Cart ──1:N── CartItem ──N:1── Variant

Wishlist ──N:1── Product
```

---

## Riwayat Perubahan

| Versi | Tanggal | Perubahan | ADR terkait |
|-------|---------|-----------|-------------|
| v1 | 2025-08-25 | SSOT awal: 15 entitas, database design untuk platform e-commerce mandiri fashion wanita | - |

---

> **Penting:** Kalau ada perbedaan antara informasi di dokumen ini dan kode yang sedang dibuat — **ikuti SSOT ini**. Jika ada alasan teknis yang mengharuskan perubahan schema, Engineer WAJIB mengajukan perubahan ke sini dulu (via Architect) SEBELUM mengubah kode.
