# Popularitas konferensi dan pola asosiasi venue di DBLP

Project IF4041 Penambangan Data. Kami mengambil publikasi konferensi dan workshop (`inproceedings`) dari DBLP tahun 2015 sampai 2025, lalu mencari venue yang paling populer dan venue yang sering muncul bersama dalam riwayat publikasi author. Apriori dan FP-Growth kami tulis sendiri di `src/`.

## Persiapan

Project ini diuji dengan Python 3.14.

```powershell
# Windows (PowerShell)
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

```bash
# Linux, macOS, atau WSL
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Kalau ingin menjalankan notebook dari terminal, pasang juga `nbconvert` (`pip install nbconvert`). Di VS Code cukup pilih kernel `.venv` lalu Run All.

## Mendapatkan data

Folder `data/raw/` dan `data/processed/` tidak ikut di Git. Parquet hasil preprocessing berukuran sekitar 203 MB, melebihi batas 100 MB per file di GitHub, jadi kami membagikannya lewat Google Drive.

Ada dua cara menyiapkan data.

1. Unduh file bersama dari Drive tim: `dblp_clean_2015_2025.parquet`, `tx_author_based.pkl`, `tx_author_year_based.pkl`, dan `tx_author_year_years.pkl`. Taruh keempatnya di `data/processed/`. Dengan cara ini kamu bisa langsung menjalankan notebook 02 dan 04 sampai 07 tanpa notebook 01 dan 03.
2. Bangun sendiri dari XML DBLP. Jalankan `python src/download_dblp.py` untuk mengunduh `dblp.xml.gz` (sekitar 1,1 GB) dan `dblp.dtd` ke `data/raw/`, lalu jalankan notebook 01. Notebook ini membaca XML dua kali dan butuh sekitar 10 menit.

DBLP terus menambah data, terutama untuk tahun terbaru, jadi unduhan di tanggal berbeda menghasilkan jumlah paper yang sedikit berbeda. Hasil di `data/results/` dan laporan memakai unduhan 19 November 2026, yaitu 1.997.244 paper setelah preprocessing. Supaya angka antaranggota tim cocok, pakai file dari Drive.

Untuk uji cepat, repo menyertakan `data/sample/dblp_sample_2024.parquet` (213 ribu paper tahun 2024) yang dibuat oleh `src/extract_sample.py`. Ubah `USE_SAMPLE = True` di notebook 03, 04, atau 07, dan semua keluarannya akan diberi akhiran `_sample` sehingga tidak menimpa hasil data penuh.

## Urutan notebook

Jalankan sesuai nomor, karena tiap notebook membaca keluaran notebook sebelumnya.

| Notebook | Soal | Membaca | Menulis |
| --- | --- | --- | --- |
| `01_eda_preprocessing` | Task 1 | `data/raw/dblp.xml.gz` | `data/processed/dblp_clean_2015_2025.parquet`, `task1_*` |
| `02_conference_popularity` | Task 2 | parquet | `task2_*` |
| `03_transactional_db` | Task 3 | parquet | `tx_author_based.pkl`, `tx_author_year_based.pkl`, `tx_author_year_years.pkl`, `task3_*` |
| `04_frequent_patterns` | Task 4 | `tx_author_based.pkl`, `tx_author_year_based.pkl` | `task4_*` |
| `05_association_rules` | Task 5 | `task4_itemsets_minsup_*.csv`, `task3_summary.csv` | `task5_*` |
| `06_temporal_analysis` | Bagian E | `tx_author_year_based.pkl`, `tx_author_year_years.pkl` | `bagianE_*` |
| `07_algorithm_benchmark` | Task 6 | `tx_author_based.pkl` | `task6_*` |

Tabel hasil masuk ke `data/results/` dan grafik ke `figures/`, dengan awalan nama sesuai soal. Untuk menjalankan satu notebook dari terminal:

```bash
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=-1 notebooks/04_frequent_patterns.ipynb
```

Jumlah itemset, rules, dan support selalu sama di setiap run. Angka runtime di Task 4 dan Task 6 bisa bergeser beberapa detik karena bergantung pada beban komputer saat itu.

## Struktur folder

```text
IF4041-project-data-mining/
├── data/
│   ├── raw/          # dblp.xml.gz, dblp.dtd, download_metadata.txt (tidak di Git)
│   ├── processed/    # parquet bersih dan pickle transaksi (tidak di Git)
│   ├── sample/       # sampel 2024 untuk uji cepat
│   └── results/      # tabel hasil tiap soal (.csv)
├── figures/          # grafik untuk laporan (.png)
├── notebooks/        # 01 sampai 07, satu notebook per soal
├── src/              # modul yang dipakai bersama oleh notebook
└── requirements.txt
```

## Modul di `src/`

| File | Isi |
| --- | --- |
| `download_dblp.py` | Mengunduh `dblp.xml.gz` dan `dblp.dtd`, lalu mencatat tanggal unduh di `download_metadata.txt` |
| `extract_sample.py` | Mengambil satu tahun publikasi dari XML sebagai sampel |
| `transactions.py` | `build_author_transactions(df)` dan `build_author_year_transactions(df)`, serta `save_transactions` dan `load_transactions` |
| `apriori.py` | `run_apriori(transactions, min_support)` |
| `fpgrowth.py` | `run_fpgrowth(transactions, min_support)` |
| `association_rules.py` | `generate_rules(frequent_itemsets, total_transactions, min_confidence=0.5)` |

Semua modul memakai format data yang sama:

- Parquet bersih berisi kolom `paper_key`, `title`, `year`, `venue_code`, `venue_name`, dan `authors` (list nama author).
- Transaksi bertipe `list[set[str]]`. Tiap set berisi `venue_code`, satu set per author (Author-Based) atau per pasangan author dan tahun (Author-Year-Based).
- `run_apriori` dan `run_fpgrowth` menerima `min_support` dalam proporsi (0,001 untuk 0,1%) dan mengembalikan `dict[frozenset[str], int]` berisi support count absolut. Notebook 04 dan 07 memeriksa bahwa keduanya menghasilkan dict yang identik.
- `generate_rules` mengembalikan DataFrame dengan kolom `antecedents`, `consequents`, `support`, `confidence`, dan `lift`.

## Catatan tentang data

- Venue diambil dari prefix key DBLP (`conf/<kode>/`). Workshop yang terbit di proceedings sebuah konferensi ikut tercatat dengan kode konferensi itu, dan `hci` mencakup seluruh volume proceedings HCI International.
- Sufiks angka pada nama author, misalnya "Yu Zhang 0189", sengaja dipertahankan. DBLP memakai sufiks ini untuk membedakan orang yang namanya sama.
- Sebagian nama author yang mengandung huruf non-ASCII tersimpan rusak, misalnya "MÃ¼ller" untuk "Müller". Penyebabnya, XML DBLP mendeklarasikan encoding ISO-8859-1 sementara entitas HTML diganti dengan byte UTF-8 saat parsing. Hasil mining tidak terpengaruh karena nama yang rusak tetap konsisten untuk orang yang sama, tetapi contoh nama di laporan perlu dibetulkan manual.
