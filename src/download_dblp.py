import os
import ssl
import urllib.request
from datetime import datetime
from tqdm import tqdm

try:
    import certifi
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl._create_unverified_context()

RAW_DIR = "data/raw"
FILES = {
    "dblp.xml.gz": "https://dblp.org/xml/dblp.xml.gz",
    "dblp.dtd": "https://dblp.org/xml/dblp.dtd",
}

def download_file_stream(url: str, dest_path: str, desc: str):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, context=SSL_CONTEXT) as response:
        total_size = int(response.headers.get("Content-Length", 0))
        with open(dest_path, "wb") as out_file, tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=desc,
        ) as pbar:
            while True:
                chunk = response.read(1024 * 1024)  # 1 mb per chunk
                if not chunk:
                    break
                out_file.write(chunk)
                pbar.update(len(chunk))

def download_files():
    os.makedirs(RAW_DIR, exist_ok=True)
    download_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    any_downloaded = False

    for filename, url in FILES.items():
        dest_path = os.path.join(RAW_DIR, filename)
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
            print(f"{filename} already exists in {RAW_DIR}, skipping download.")
            continue

        print(f"downloading {filename} from {url}")
        try:
            download_file_stream(url, dest_path, filename)
        except ssl.SSLError:
            # fallback otomatis jika certifi masih ditolak oleh firewall/antivirus lokal
            global SSL_CONTEXT
            SSL_CONTEXT = ssl._create_unverified_context()
            download_file_stream(url, dest_path, filename)
        any_downloaded = True

    # metadata untuk task 1
    meta_path = os.path.join(RAW_DIR, "download_metadata.txt")
    if any_downloaded or not os.path.exists(meta_path):
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write("dataset source: https://dblp.org/xml/\n")
            f.write(f"download date: {download_date}\n")
            for filename in FILES:
                size_mb = os.path.getsize(os.path.join(RAW_DIR, filename)) / (1024 * 1024)
                f.write(f"File: {filename} ({size_mb:.2f} MB)\n")


if __name__ == "__main__":
    download_files()

'''
atau:
curl -L https://dblp.org/xml/dblp.xml.gz -o data/raw/dblp.xml.gz
curl -L https://dblp.org/xml/dblp.dtd -o data/raw/dblp.dtd
'''