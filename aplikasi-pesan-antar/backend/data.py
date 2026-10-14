"""Pembaca CSV buatan sendiri (tanpa csv.DictReader / dict) dan record Pesanan."""
from backend.util import PesanError

NAMA_PRIORITAS = ("", "VIP", "PRIORITAS", "REGULER")
JUMLAH_KOLOM = 9


class Pesanan:
    __slots__ = ("oid", "pelanggan", "resto", "menu", "harga",
                 "prioritas", "masuk", "selesai", "status")

    def __init__(self, oid, pelanggan, resto, menu, harga,
                 prioritas, masuk, selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = harga
        self.prioritas = prioritas
        self.masuk = masuk
        self.selesai = selesai      # int detik, atau None bila belum selesai
        self.status = status


def pecah_csv(baris):
    """Memecah satu baris CSV; mendukung "kolom, berkoma" dan "" di dalam kutip."""
    if '"' not in baris:
        return baris.split(",")
    hasil = []
    buf = ""
    dalam_kutip = False
    i = 0
    n = len(baris)
    while i < n:
        c = baris[i]
        if dalam_kutip:
            if c == '"':
                if i + 1 < n and baris[i + 1] == '"':
                    buf += '"'
                    i += 1
                else:
                    dalam_kutip = False
            else:
                buf += c
        elif c == '"':
            dalam_kutip = True
        elif c == ",":
            hasil.append(buf)
            buf = ""
        else:
            buf += c
        i += 1
    hasil.append(buf)
    return hasil


def baca_pesanan(path):
    """Generator Pesanan dari pesanan.csv (header dilewati)."""
    try:
        f = open(path, encoding="utf-8", newline="")
    except OSError:
        raise PesanError(f"Berkas tidak ditemukan: {path}")
    with f:
        no = 0
        for baris in f:
            no += 1
            baris = baris.rstrip("\r\n")
            if no == 1 or baris == "":
                continue
            k = pecah_csv(baris)
            if len(k) != JUMLAH_KOLOM:
                raise PesanError(f"{path} baris {no}: {len(k)} kolom, seharusnya {JUMLAH_KOLOM}")
            try:
                selesai = int(k[7]) if k[7] != "" else None
                yield Pesanan(k[0], k[1], k[2], k[3], int(k[4]),
                              int(k[5]), int(k[6]), selesai, k[8])
            except ValueError:
                raise PesanError(f"{path} baris {no}: nilai angka tidak valid")
