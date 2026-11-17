## Kontrak Data & Fungsi Antar-Anggota

1. **Dataset Bersih (`data/sample/` & `data/processed/`)**:
* Format: Apache Parquet (`.parquet`)
* Kolom: `paper_key` (str), `title` (str), `year` (int), `venue_code` (str), `venue_name` (str), `authors` (list[str])

2. **Format Transaksi (Orang B)**:
* Tipe data: `list[set[str]]` (setiap elemen adalah himpunan `venue_code`)

3. **Algoritma Mining (Orang B - Apriori, Orang C - FP-Growth)**:
* Input: `(transactions: list[set[str]], min_support: float)` -> *min_support dalam proporsi (misal 0.01 untuk 1%)*
* Output: `dict[frozenset[str], int]` (mapping itemset ke **support count** absolut)

4. **Association Rule Mining (Orang C)**:
* Input: `(frequent_itemsets: dict[frozenset[str], int], total_transactions: int, min_confidence: float = 0.5)`
* Output: `pd.DataFrame` dengan kolom `['antecedents', 'consequents', 'support', 'confidence', 'lift']`

## Struktur Direktori Proyek

```text
IF4041-project-data-mining/
├── data/                        # Penyimpanan data (diabaikan oleh Git, kecuali hasil kecil)
│   ├── raw/                     # Dataset mentah DBLP (dblp.xml.gz & dblp.dtd) — [Orang A]
│   ├── sample/                  # Data sampel 1 tahun (dblp_sample_2024.parquet) untuk testing cepat
│   ├── processed/               # Dataset bersih & transactional DB siap pakai
│   │   ├── dblp_clean_2015_2025.parquet   # Dataset utama hasil Task 1 — [Orang A]
│   │   ├── tx_author_based.pkl            # Output Task 3A — [Orang B]
│   │   └── tx_author_year_based.pkl       # Output Task 3B — [Orang B]
│   └── results/                 # Tabel ringkasan (.csv) untuk bahan laporan & grafik
│
├── src/                         # Kode modular (fungsi inti yang diimpor antar anggota)
│   ├── __init__.py
│   ├── download_dblp.py         # Script unduh dataset DBLP — [Orang A]
│   ├── extract_sample.py        # Script ekstraksi data sampel — [Orang A]
│   ├── transactions.py          # Fungsi pembentuk Transactional DB — [Orang B]
│   ├── apriori.py               # Implementasi algoritma Apriori — [Orang B]
│   ├── fpgrowth.py              # Implementasi algoritma FP-Growth — [Orang C]
│   └── association_rules.py     # Fungsi pembangkit Association Rules — [Orang C]
│
├── notebooks/                   # Tempat menjalankan eksperimen & membuat visualisasi
│   ├── 01_eda_preprocessing.ipynb      # Task 1 — [Orang A]
│   ├── 02_conference_popularity.ipynb  # Task 2 — [Orang A]
│   ├── 03_transactional_db.ipynb       # Task 3 — [Orang B]
│   ├── 04_frequent_patterns.ipynb      # Task 4 — [Orang B]
│   ├── 05_association_rules.ipynb      # Task 5 — [Orang C]
│   ├── 06_temporal_analysis.ipynb      # Bagian E — [Orang C]
│   └── 07_algorithm_benchmark.ipynb    # Task 6 — [Orang A]
│
├── figures/                     # Folder penyimpanan semua grafik (.png) untuk laporan
├── report/                      # Draft dokumen laporan akhir & slide presentasi
├── .gitignore                   # Pengaturan file yang tidak di-push ke Git
├── requirements.txt             # Daftar library Python yang dibutuhkan
└── README.md                    # Panduan proyek & kontrak fungsi tim
```

---
## Next Step

> Gunakan `data/sample/dblp_sample_2024.parquet` terlebih dahulu saat mengembangkan dan mengetes kode agar proses *debugging* berjalan cepat (dalam hitungan detik). Setelah kode terbukti berjalan tanpa error, baru arahkan input ke dataset penuh `data/processed/dblp_clean_2015_2025.parquet`.

### Orang B (Transaksi & Apriori)

1. **Buat Modul Transaksi (`src/transactions.py`):**
* Buat fungsi yang membaca DataFrame hasil preprocessing (kolom `year`, `venue_code`, `authors`) dan mengubahnya menjadi dua representasi transaksi bertipe `list[set[str]]`:
* `build_author_transactions(df)` $\rightarrow$ 1 `set` per `author` (semua `venue_code` yang pernah diikuti author pada 2015–2025).
* `build_author_year_transactions(df)` $\rightarrow$ 1 `set` per kombinasi `(author, year)`.

2. **Jalankan & Analisis Task 3 (`notebooks/03_transactional_db.ipynb`):**
* Bangun kedua *transactional database* dari data penuh lalu simpan hasilnya ke `data/processed/tx_author_based.pkl` dan `data/processed/tx_author_year_based.pkl` agar bisa langsung dipakai oleh Orang A dan C.
* Tampilkan minimal 10 contoh transaksi, jumlah transaksi, jumlah item unik, distribusi panjang item per transaksi, serta analisis kelebihan/kekurangan kedua representasi.

3. **Buat Implementasi Apriori (`src/apriori.py`):**
* Buat fungsi dengan signature wajib: `run_apriori(transactions: list[set[str]], min_support: float) -> dict[frozenset[str], int]`.
* *Tips optimasi:* Lakukan *integer encoding* pada nama `venue_code` sebelum proses pencarian itemset agar algoritma tidak lambat pada `min_support = 0.001` (0,1%).

4. **Jalankan & Analisis Task 4 (`notebooks/04_frequent_patterns.ipynb`):**
* Gunakan `tx_author_based.pkl` untuk menjalankan `run_apriori` (dan `run_fpgrowth` dari `src/fpgrowth.py` milik C) pada 4 nilai `min_support`: `0.001` (0,1%), `0.005` (0,5%), `0.01` (1%), dan `0.02` (2%).
* Analisis frequent 1-, 2-, 3-itemsets, Top-10 itemset, serta pengaruh perubahan *minimum support*. Simpan grafik ke `figures/` dengan awalan `task4_`.

---

### Orang C (FP-Growth, Association Rules, & Temporal Analysis)

1. **Buat Implementasi FP-Growth (`src/fpgrowth.py`):**
* Buat fungsi dengan signature wajib: `run_fpgrowth(transactions: list[set[str]], min_support: float) -> dict[frozenset[str], int]`.
* Pastikan output-nya (pasangan `frozenset` dan `support_count` absolut) **100% sama** dengan output `run_apriori` milik Orang B.

2. **Buat Fungsi Association Rules (`src/association_rules.py`):**
* Buat fungsi dengan signature wajib: `generate_rules(frequent_itemsets: dict[frozenset[str], int], total_transactions: int, min_confidence: float = 0.5) -> pd.DataFrame`.
* Kembalikan DataFrame berisi kolom `['antecedents', 'consequents', 'support', 'confidence', 'lift']`. Fungsi ini juga akan diimpor oleh Orang A untuk benchmarking Task 6.

3. **Jalankan & Analisis Task 5 (`notebooks/05_association_rules.ipynb`):**
* Muat `tx_author_based.pkl` (dari Orang B), jalankan `run_fpgrowth`, lalu bangkitkan *rules* dengan `min_confidence = 0.5` (50%).
* Identifikasi Top-10 *rules* berdasarkan nilai `lift` tertinggi, evaluasi hubungan antara *support* tinggi dan *lift*, serta jelaskan pola asosiasi antar-konferensi. Simpan grafik ke `figures/` dengan awalan `task5_`.

4. **Jalankan & Analisis Bagian E (`notebooks/06_temporal_analysis.ipynb`):**
* Gunakan dataset bersih (`dblp_clean_2015_2025.parquet`) yang dibagi ke dalam 4 periode: `2015–2017`, `2018–2020`, `2021–2023`, dan `2024–2025`.
* Bangun transaksi **Author-Year-Based** untuk masing-masing periode (menggunakan fungsi `build_author_year_transactions` dari `src/transactions.py` milik B), jalankan FP-Growth dan ARM, lalu bandingkan pola asosiasi yang bertahan maupun yang berubah antar-periode. Simpan grafik ke `figures/` dengan awalan `bagianE_`.