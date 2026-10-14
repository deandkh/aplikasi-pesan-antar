"""Utilitas bersama: galat, pencacah, dan format angka gaya Indonesia."""


class PesanError(Exception):
    """Galat yang pesannya aman ditampilkan langsung ke pengguna."""


class Hitung:
    """Pencacah sederhana yang dititipkan ke algoritma (M3)."""

    def __init__(self):
        self.perbandingan = 0
        self.pemindahan = 0


def fmt_int(n):
    """12345 -> '12.345'"""
    s = str(abs(int(n)))
    k = len(s)
    out = ""
    for i in range(k):
        if i > 0 and (k - i) % 3 == 0:
            out += "."
        out += s[i]
    return "-" + out if n < 0 else out


def fmt_dec(x, d=2):
    """3.14159 -> '3,14'"""
    return f"{x:.{d}f}".replace(".", ",")


def fmt_ms(ms):
    if ms >= 1000:
        return fmt_dec(ms / 1000.0, 2) + " s"
    return fmt_dec(ms, 2) + " ms"


def fmt_rp(x):
    if isinstance(x, float) and x != int(x):
        bulat = int(x)
        sisa = abs(x - bulat)
        return "Rp " + fmt_int(bulat) + "," + f"{sisa:.2f}"[2:]
    return "Rp " + fmt_int(int(x))


def jam(detik):
    """detik sejak 00:00 -> 'HH:MM:SS'"""
    d = int(detik) % 86400
    return f"{d // 3600:02d}:{(d % 3600) // 60:02d}:{d % 60:02d}"


def ke_int(teks, nama):
    try:
        return int(str(teks).strip())
    except ValueError:
        raise PesanError(f"{nama} harus berupa bilangan bulat.")
