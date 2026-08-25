# PRD: Platform E-Commerce Mandiri untuk Merchant Fashion Wanita

## Latar Belakang

Banyak merchant fashion wanita di Indonesia yang bergantung sepenuhnya pada marketplace seperti Shopee atau Tokopedia. Ketergantungan ini menciptakan tantangan bisnis: biaya komisi tinggi per transaksi, persaingan harga yang mengerikkan margin, keterbatasan branding (toko terlihat sama dengan ribuan toko lain), dan tidak punya akses penuh ke data pelanggan sendiri. Merchant butuh saluran jual mandiri yang memberikan kontrol penuh atas harga, branding, hubungan pelanggan, dan data — tanpa harus membangun tim teknis internal yang mahal. Platform ini hadir sebagai solusi "toko online sendiri" yang siap pakai, dengan integrasi pembayaran lokal (Midtrans) dan desain yang memperkuat identitas brand fashion wanita, sehingga merchant bisa fokus menjual sambil membangun aset bisnis jangka panjang: basis pelanggan sendiri.

## User Stories

1. Sebagai **merchant fashion wanita**, saya ingin memiliki toko online dengan domain dan branding sendiri, agar pelanggan mengenal brand saya — bukan hanya marketplace.
2. Sebagai **merchant**, saya ingin mengelola katalog produk (foto, varian ukuran/warna, stok, harga) dengan mudah, agar bisa cepat merespons tren fashion musiman.
3. Sebagai **merchant**, saya ingin pelanggan bisa belanja, bayar, dan terima konfirmasi otomatis tanpa campur tangan manual, agar operasional hemat tenaga.
4. Sebagai **merchant**, saya ingin menerima pembayaran via transfer bank, e-wallet, dan virtual account (Midtrans), agar menutupi preferensi bayar mayoritas pembeli Indonesia.
5. Sebagai **merchant**, saya ingin melihat daftar pesanan masuk, status pembayaran, dan detail pengiriman di satu halaman, agar tidak perlu bolak-balik antar aplikasi.
6. Sebagai **pembeli**, saya ingin menjelajahi katalog, melihat detail produk dengan foto jelas, memilih varian, dan checkout lancar di HP maupun laptop, agar nyaman belanja kapan saja.
6. Sebagai **pembeli**, saya ingin mendapat notifikasi otomatis saat pesanan dibayar, dikemas, dan dikirim, agar tahu status tanpa perlu chat admin.
7. Sebagai **merchant**, saya ingin data pelanggan (nama, kontak, riwayat belanja) tersimpan di sistem saya, agar bisa melakukan retargeting, program loyalitas, atau promosi langsung ke pelanggan lama.
8. Sebagai **merchant**, saya ingin halaman toko terlihat profesional dan estetik fashion (bersih, hangat, "enak dipandang"), agar membangun kepercayaan brand sejak pertama kali dikunjungi.

## Fitur Wajib (Must Have)

### 1. Manajemen Katalog Produk
- Tambah, edit, hapus produk dengan foto multiple, deskripsi, kategori, dan varian (ukuran, warna, dll).
- Pengaturan stok per varian dengan indikator otomatis "habis" / "tersedia".
- Pengelolaan kategori/koleksi (misal: "Musim Panas", "Hijab Cerut", "Dress Formal").

### 2. Tampilan Toko (Storefront) — Web Responsif
- Halaman beranda: hero banner, produk unggulan, kategori populer.
- Halaman katalog: filter kategori, urutkan (terbaru, harga terendah/tertinggi), pencarian nama produk.
- Halaman detail produk: galeri foto zoom, pilihan varian, info stok real-time, tombol "Tambah ke Keranjang", deskripsi lengkap, ulasan pembeli (jika ada).
- Desain mobile-first, estetik fashion wanita (warna netral hangat, tipografi elegan, claymorphism accent pada kartu produk & tombol aksi).

### 3. Keranjang & Checkout
- Keranjang persisten (tersimpan meski tutup browser).
- Ringkasan pesanan: item, qty, subtotal, ongkir estimasi, total bayar.
- Form pengiriman: nama, telepon, alamat lengkap, catatan untuk penjual.
- Pilihan metode pembayaran terintegrasi Midtrans: Virtual Account (BCA, BRI, BNI, Mandiri, Permata), e-wallet (GoPay, ShopeePay, Dana, OVO), QRIS, Retail outlet (Indomaret, Alfamart).
- Validasi form real-time (format telepon, kode pos, field wajib).

### 4. Integrasi Pembayaran Midtrans (End-to-End)
- Redirect/embed halaman pembayaran Midtrans.
- Penanganan callback/webhook otomatis: status transaksi berubah ke "Dibayar" saat pembayaran sukses.
- Halaman konfirmasi pesanan: detail pesanan, bukti pembayaran, estimasi pengiriman, nomor resi (saat tersedia).
- Penanganan kasus gagal/expired: notifikasi ke pembeli + opsi bayar ulang.

### 5. Manajemen Pesanan (Merchant Side)
- Daftar pesanan dengan filter: status (Menunggu Bayar, Dibayar, Dikemas, Dikirim, Selesai, Dibatalkan), rentang tanggal.
- Detail pesanan: item, data pembeli, alamat, metode bayar, bukti bayar, timeline status.
- Aksi: ubah status (Kemas → Kirim), input nomor resi ekspedisi, catatan internal.
- Cetak/unduh struk & label pengiriman (format termal A6/A5).

### 6. Data Pelanggan (CRM Ringan)
- Daftar pelanggan dengan profil: nama, email, telepon, total belanja, frekuensi, terakhir beli.
- Riwayat pesanan per pelanggan.
- Ekspor data pelanggan (CSV/Excel) untuk keperluan marketing (WhatsApp blast, email marketing).

### 7. Notifikasi Otomatis
- Ke pembeli: konfirmasi pesanan, pembayaran berhasil, pesanan dikemas, pesanan dikirim (dengan nomor resi), pesanan selesai.
- Ke merchant: pesanan baru masuk, pembayaran masuk, pesanan butuh tindakan (misal: stok habis).

### 8. Pengaturan Toko Dasar
- Nama toko, logo, favicon, deskripsi singkat.
- Informasi kontak (WhatsApp, email, IG).
- Kebijakan pengembalian & pengiriman.
- Metode pengiriman & ongkir (flat rate, per kota, gratis di atas nilai tertentu).

## Fitur Tambahan (Nice to Have)

1. **Kode Promo / Diskon**: Kode unik, persentase/nominal, syarat minimum belanja, batas penggunaan, tanggal kadaluarsa.
2. **Program Poin Loyalitas**: Poin per belanja, tukar poin jadi potongan harga.
3. **Ulasan Produk**: Pembeli kasih rating + komentar setelah pesanan selesai, tampil di halaman produk.
4. **Wishlist / Simpan untuk Nanti**: Pembeli simpan produk favorit tanpa beli langsung.
5. **Multi-kurir Otomatis**: Integrasi cek ongkir real-time (JNE, J&T, SiCepat, dll) saat checkout.
6. **Dashboard Ringkas**: Grafik penjualan harian/bulanan, produk terlaris, nilai rata-rata transaksi (AOV).
7. **Mode "Catalog Only" (Tanpa Checkout)**: Untuk merchant yang mau tampilin produk tapi transaksi lewat WA/direct — toggle on/off.
8. **Aplikasi Mobile Merchant (React Native)**: Terima notifikasi pesanan baru, ubah status pesanan, cek stok cepat dari HP.
9. **Domain Custom & SSL**: Merchant pakai domain sendiri (toko.brandku.com) dengan SSL otomatis.
10. **Integrasi WhatsApp Business API**: Kirim notifikasi & broadcast promosi lewat WA resmi.

## Kriteria Sukses

- Merchant bisa launch toko online fungsional penuh (katalog → checkout → bayar → kelola pesanan) dalam waktu singkat tanpa bantuan developer.
- Alur pembayaran Midtrans berjalan mulus: > 98% transaksi sukses terverifikasi otomatis via webhook tanpa intervensi manual.
- Toko terlihat profesional dan "enak dipandang" — konsisten dengan estetik fashion wanita — sehingga pembeli percaya bertransaksi.
- Merchant memiliki akses penuh ke data pelanggan sendiri (nama, kontak, riwayat belanja) untuk keperluan retargeting & loyalitas.
- Web responsif lancar di mobile & desktop; loading halaman katalog < 3 detik di jaringan 4G standar.
- Merchant bisa mencetak label pengiriman & struk langsung dari dashboard tanpa copy-paste ke aplikasi lain.
- Notifikasi otomatis terkirim ke pembeli & merchant di setiap tahap kritis pesanan (bayar, kemas, kirim, selesai).

## Riwayat Revisi

| Versi | Tanggal | Perubahan | Diminta oleh |
|-------|---------|-----------|--------------|
| v1 | 2025-08-25 | Draft awal: PRD untuk platform e-commerce mandiri fashion wanita (bukan dummy project), niche modest fashion/general women fashion, payment Midtrans, fokus merchant lepas dari marketplace | User |

---

**Mohon review dan beri persetujuan (Approve) sebelum saya lanjutkan ke tahap desain teknis (Architect).**