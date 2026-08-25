# ADR-001: Deployment Strategy

## Status

**Approved** — 2025-08-25

## Context

Platform e-commerce mandiri fashion perlu di-deploy ke production. Keputusan deployment mempengaruhi cost, maintenance, dan skalabilitas di masa depan.

## Keputusan

Deploy ke **VPS lokal Indonesia** dengan spec:
- **2 vCPU, 2 GB RAM, 15 GB SSD**
- **Budget: ~50.000 IDR/bulan**
- **Stack: Nginx + Gunicorn + MySQL (semua di satu VPS)**

### Alternatif yang Dipertimbangkan

| Alternatif | Kelebihan | Kekurangan | Keputusan |
|------------|-----------|------------|-----------|
| **A. VPS lokal, semua di satu mesin** | Murah (~50rb/bulan), simpel, 1 tempat | Kalau VPS mati, semua mati | ✅ **DIPILIH** |
| **B. VPS + managed MySQL** | DB lebih aman, scalable | Lebih mahal (~150-250rb/bulan) | ❌ Terlalu mahal untuk fase awal |
| **C. PaaS (Railway/Render)** | Deploy simpel, auto-scale | Biaya naik cepat, keterbatasan config | ❌ Tidak fleksibel untuk kebutuhan khusus |
| **D. Shared hosting** | Murah | Tidak support Python/Django dengan baik | ❌ Tidak cocok |

### Alasan Memilih VPS Lokal

1. **Cost:** 50rb/bulan sangat terjangkau untuk project multi-merchant
2. **Kontrol penuh:** Bisa install apapun, config apapun
3. **Belajar:** Memahami deployment production dari nol
4. **Skalabilitas:** Bisa upgrade VPS (RAM/CPU) saat traffic naik tanpa rewrite kode

## Stack Deployment

```
Internet → Nginx (80/443)
              ├── /static/  → CSS/JS dari disk
              ├── /media/   → foto produk dari disk
              └── /         → Gunicorn:8000 → Django
                                      ↓
                                MySQL:3306 (localhost only)
```

## Security

- MySQL: hanya listen localhost
- Gunicorn: hanya listen localhost:8000
- SSH: key-based auth, non-root
- Firewall: buka port 80, 443, 22 saja

## Domain & SSL

- Fase awal: akses via IP langsung
- SSL: Let's Encrypt via Certbot (saat domain sudah ada)
- Domain: belum ditentukan

## File Gambar

- Development: placeholder dari internet (unsplash/placeholder.com)
- Production: upload ke disk VPS (`media/products/`)
- Scale: migrasi ke S3-compatible storage

## Backup

- Database: cron harian `mysqldump` → kompres → upload ke Google Drive/S3
- Media files: rsync mingguan ke storage backup

## Consequences

1. ✅ Cost sangat rendah (~50rb/bulan)
2. ✅ Satu tempat untuk semua komponen
3. ✅ Deploy manual pertama kali, tapi setelah itu stable
4. ⚠️ Single point of failure — VPS mati = semua mati
5. ⚠️ Backup manual perlu disiplin
6. 📌 Nanti bisa upgrade ke VPS lebih besar atau managed DB tanpa rewrite kode

---

**Dokumen terkait:** `architecture.md` section 7e
