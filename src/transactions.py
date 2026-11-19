import pickle
from pathlib import Path

import pandas as pd


def explode_author_venue(df: pd.DataFrame) -> pd.DataFrame:
    pa = (
        df[["authors", "year", "venue_code"]]
        .explode("authors")
        .rename(columns={"authors": "author"})
        .dropna(subset=["author", "venue_code"])
    )
    pa = pa[(pa["author"] != "") & (pa["venue_code"] != "")]
    return pa.drop_duplicates(ignore_index=True)


def _group_to_sets(pa: pd.DataFrame, keys: list[str]) -> pd.Series:
    groups: dict = {}
    key_iter = pa[keys[0]] if len(keys) == 1 else zip(*(pa[k] for k in keys))
    for key, venue in zip(key_iter, pa["venue_code"]):
        s = groups.get(key)
        if s is None:
            groups[key] = {venue}
        else:
            s.add(venue)

    index = (
        pd.Index(groups.keys(), name=keys[0])
        if len(keys) == 1
        else pd.MultiIndex.from_tuples(groups.keys(), names=keys)
    )
    return pd.Series(list(groups.values()), index=index, name="venue_code").sort_index()


def build_author_transactions(df: pd.DataFrame, return_keys: bool = False):
    """
    Author-Based: 1 transaksi = semua venue yang pernah didatangi seorang author.

    return_keys=False -> list[set[str]]            (format kontrak)
    return_keys=True  -> pd.Series index=author     (untuk menampilkan contoh)
    """
    tx = _group_to_sets(explode_author_venue(df), ["author"])
    return tx if return_keys else tx.tolist()


def build_author_year_transactions(df: pd.DataFrame, return_keys: bool = False):
    """
    Author-Year-Based: 1 transaksi = venue tempat author publikasi pada satu tahun.

    return_keys=False -> list[set[str]]                    (format kontrak)
    return_keys=True  -> pd.Series index=(author, year)     (untuk menampilkan contoh)
    """
    tx = _group_to_sets(explode_author_venue(df), ["author", "year"])
    return tx if return_keys else tx.tolist()


def save_transactions(transactions: list[set[str]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(transactions, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_transactions(path: str | Path) -> list[set[str]]:
    with open(path, "rb") as f:
        return pickle.load(f)
