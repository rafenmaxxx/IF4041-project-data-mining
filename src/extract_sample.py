import gzip
import html
import io
import os
import re
import pandas as pd
from lxml import etree
from tqdm import tqdm

XML_GZ_PATH = "data/raw/dblp.xml.gz"
TARGET_YEAR = 2024 # ubah ke tahun yang mau dijadikan sample
SAMPLE_OUT_PATH = f"data/sample/dblp_sample_{TARGET_YEAR}.parquet"

ENTITY_PATTERN = re.compile(r"&([a-zA-Z]+);")
STANDARD_XML_ENTITIES = {"amp", "lt", "gt", "quot", "apos"}

def replace_html_entities(line: bytes) -> bytes:
    """
    ubah entitas karakter HTML DBLP (mis. &uuml;) menjadi karakter UTF-8
    """
    if b"&" not in line:
        return line
    text = line.decode("utf-8", errors="replace")
    def _sub(match):
        ent = match.group(1)
        if ent in STANDARD_XML_ENTITIES:
            return match.group(0)
        return html.unescape(match.group(0))
    return ENTITY_PATTERN.sub(_sub, text).encode("utf-8")

class DblpCleanStream:
    """wrapper stream"""
    def __init__(self, gz_file, raw_file, pbar):
        self.gz_file = gz_file
        self.raw_file = raw_file
        self.pbar = pbar
        self.last_pos = 0
        self.buffer = io.BytesIO()

    def read(self, size=-1):
        while size < 0 or self.buffer.tell() < size:
            line = self.gz_file.readline()
            if not line:
                break
            if line.startswith(b"<!DOCTYPE"):
                continue
            self.buffer.write(replace_html_entities(line))

        # update progress bar
        current_pos = self.raw_file.tell()
        if current_pos > self.last_pos:
            self.pbar.update(current_pos - self.last_pos)
            self.last_pos = current_pos

        data = self.buffer.getvalue()
        self.buffer = io.BytesIO()
        return data

def extract_venue_code(key: str) -> str:
    """
    ambil prefix konferensi dari key DBLP ('conf/cvpr/Smith24' -> 'cvpr')
    """
    if not key:
        return ""
    parts = key.split("/")
    if len(parts) >= 2 and parts[0] == "conf":
        return parts[1].lower().strip()
    return ""

def generate_sample():
    if not os.path.exists(XML_GZ_PATH):
        raise FileNotFoundError(f"File {XML_GZ_PATH} not found, run download_dblp.py first.")

    total_gz_bytes = os.path.getsize(XML_GZ_PATH)
    print(f"extracting year {TARGET_YEAR} from {XML_GZ_PATH}...")
    records = []

    with open(XML_GZ_PATH, "rb") as raw_f, tqdm(
        total=total_gz_bytes,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
        desc="Scanning DBLP XML",
    ) as pbar:
        with gzip.open(raw_f, "rb") as gz_f:
            clean_stream = DblpCleanStream(gz_f, raw_f, pbar)
            context = etree.iterparse(
                clean_stream,
                events=("end",),
                tag="inproceedings",
                recover=True
            )

            for _, elem in context:
                year_text = elem.findtext("year")
                if year_text and year_text.isdigit() and int(year_text) == TARGET_YEAR:
                    key = elem.get("key", "")
                    venue_code = extract_venue_code(key)

                    authors = [
                        re.sub(r"\s+", " ", a.text.strip())
                        for a in elem.findall("author")
                        if a.text and a.text.strip()
                    ]

                    title_elem = elem.find("title")
                    title = "".join(title_elem.itertext()).strip() if title_elem is not None else ""
                    venue_name = elem.findtext("booktitle", "").strip()

                    if venue_code and authors and title:
                        records.append({
                            "paper_key": key,
                            "title": title,
                            "year": TARGET_YEAR,
                            "venue_code": venue_code,
                            "venue_name": venue_name,
                            "authors": authors
                        })

                # release xml element memory
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

    os.makedirs(os.path.dirname(SAMPLE_OUT_PATH), exist_ok=True)
    df_sample = pd.DataFrame(records).drop_duplicates(subset=["paper_key"])
    df_sample.to_parquet(SAMPLE_OUT_PATH, index=False)
    print("first 3 rows:")
    print(df_sample[["paper_key", "year", "venue_code", "authors"]].head(3))

if __name__ == "__main__":
    generate_sample()