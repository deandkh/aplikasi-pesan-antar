"""M2: Stack (kasir + undo/redo) dan dua versi Queue (naif vs melingkar)."""
from backend.m1_pesanan import Array
from backend.util import PesanError

DIGIT = "0123456789"
OPERATOR = ("+", "-", "*", "/")


# ------------------------------------------------------------------ Stack
class Stack:
    """Tumpukan (LIFO) di atas Array milik sendiri."""

    def __init__(self):
        self.a = Array()

    def push(self, x):
        self.a.append(x)

    def pop(self):
        if self.a.n == 0:
            raise IndexError("stack kosong")
        return self.a.remove(self.a.n - 1)

    def peek(self):
        if self.a.n == 0:
            raise IndexError("stack kosong")
        return self.a.data[self.a.n - 1]

    def kosong(self):
        return self.a.n == 0

    def __len__(self):
        return self.a.n

    def isi(self):
        """Dari dasar ke puncak."""
        return self.a.isi()


# ----------------------------------------------------- kasir: infix -> total
def pecah_token(teks):
    """'( 3*12000 )' -> ['(', '3', '*', '12000', ')'] ; angka berdigit banyak = 1 token."""
    t = Array()
    i = 0
    n = len(teks)
    butuh_operand = True
    while i < n:
        c = teks[i]
        if c == " " or c == "\t":
            i += 1
        elif c in DIGIT or (c == "-" and butuh_operand and i + 1 < n and teks[i + 1] in DIGIT):
            j = i + 1
            while j < n and (teks[j] in DIGIT or teks[j] == "."):
                j += 1
            t.append(teks[i:j])
            i = j
            butuh_operand = False
        elif c in OPERATOR:
            t.append(c)
            i += 1
            butuh_operand = True
        elif c == "(":
            t.append(c)
            i += 1
            butuh_operand = True
        elif c == ")":
            t.append(c)
            i += 1
            butuh_operand = False
        else:
            raise PesanError(f"Karakter tidak dikenal di struk: '{c}'")
    return t.isi()


def _prioritas(op):
    return 2 if (op == "*" or op == "/") else 1


def _adalah_angka(tok):
    return tok != "(" and tok != ")" and tok not in OPERATOR


def _ke_angka(tok):
    try:
        return float(tok) if "." in tok else int(tok)
    except ValueError:
        raise PesanError(f"Angka tidak valid: {tok}")


def _teks_angka(x):
    if isinstance(x, float):
        return str(int(x)) if x == int(x) else f"{x:.4f}".rstrip("0")
    return str(x)


def _teks_stack(st, angka=False):
    isi = st.isi()
    if len(isi) == 0:
        return "kosong"
    out = ""
    for k in range(len(isi)):
        out += (" " if k else "") + (_teks_angka(isi[k]) if angka else isi[k])
    return out


def _teks_larik(a):
    isi = a.isi()
    out = ""
    for k in range(len(isi)):
        out += (" " if k else "") + isi[k]
    return out


def ke_postfix(ekspresi, log=None):
    """Infix -> postfix (list token). Bila `log` (Array) diberikan, tiap langkah dicatat
    sebagai tuple (langkah, token, tindakan, isi_stack, keluaran)."""
    tokens = pecah_token(ekspresi)
    if len(tokens) == 0:
        raise PesanError("Struk kosong.")
    ops = Stack()
    out = Array()
    for no in range(len(tokens)):
        tok = tokens[no]
        if _adalah_angka(tok):
            out.append(tok)
            aksi = "angka, langsung keluar"
        elif tok == "(":
            ops.push(tok)
            aksi = "push ( ke stack"
        elif tok == ")":
            while True:
                if ops.kosong():
                    raise PesanError("Kurung tutup ')' tanpa pasangan.")
                x = ops.pop()
                if x == "(":
                    break
                out.append(x)
            aksi = "pop sampai ( , buang ("
        else:
            keluar = ""
            while (not ops.kosong()) and ops.peek() != "(" \
                    and _prioritas(ops.peek()) >= _prioritas(tok):
                x = ops.pop()
                out.append(x)
                keluar += (" " if keluar else "") + x
            ops.push(tok)
            aksi = f"pop {keluar} (lebih kuat/sama), push {tok}" if keluar else f"push {tok}"
        if log is not None:
            log.append((f"1.{no + 1}", tok, aksi, _teks_stack(ops), _teks_larik(out)))
    while not ops.kosong():
        x = ops.pop()
        if x == "(":
            raise PesanError("Kurung buka '(' tanpa pasangan.")
        out.append(x)
    if log is not None:
        log.append(("1.akhir", "-", "pop sisa stack", "kosong", _teks_larik(out)))
    return out.isi()


def hitung(postfix, log=None):
    """Evaluasi postfix dengan stack angka. Pop pertama = operand KANAN."""
    st = Stack()
    for no in range(len(postfix)):
        tok = postfix[no]
        if _adalah_angka(tok):
            st.push(_ke_angka(tok))
            aksi = f"operand, push {tok}"
        else:
            if len(st) < 2:
                raise PesanError("Struk tidak valid: operand kurang.")
            b = st.pop()
            a = st.pop()
            if tok == "+":
                r = a + b
            elif tok == "-":
                r = a - b
            elif tok == "*":
                r = a * b
            else:
                if b == 0:
                    raise PesanError("Pembagian dengan nol.")
                r = a / b
                if r == int(r):
                    r = int(r)
            aksi = f"pop {_teks_angka(b)} dan {_teks_angka(a)} -> {_teks_angka(a)} {tok} {_teks_angka(b)} = {_teks_angka(r)}"
            st.push(r)
        if log is not None:
            log.append((f"2.{no + 1}", tok, aksi, _teks_stack(st, True), "-"))
    if len(st) != 1:
        raise PesanError("Struk tidak valid: operator kurang.")
    return st.pop()


# ------------------------------------------------------------------ Queue
class AntreanNaif:
    """Antrean di atas Array biasa; dequeue = ambil indeks 0 lalu geser sisa, O(n)."""

    def __init__(self):
        self.a = Array()
        self.total_geser = 0

    def __len__(self):
        return self.a.n

    def enqueue(self, x):
        self.a.append(x)

    def dequeue(self):
        if self.a.n == 0:
            return None
        x = self.a.remove(0)
        self.total_geser += self.a.langkah
        return x

    def pop_back(self):
        if self.a.n == 0:
            return None
        return self.a.remove(self.a.n - 1)

    def push_front(self, x):
        self.a.insert(0, x)
        self.total_geser += self.a.langkah

    def isi(self):
        return self.a.isi()


class AntreanMelingkar:
    """Antrean melingkar: data, front, rear, count. Dequeue hanya memajukan front, O(1).

    Keputusan: bila penuh, enqueue MENUMBUHKAN kapasitas 2x (salin berurutan dari front,
    lalu front=0). Pencacah `count` dipakai agar kosong vs penuh tidak ambigu."""

    def __init__(self, kapasitas=4):
        self.data = [None] * kapasitas
        self.kapasitas = kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0

    def __len__(self):
        return self.count

    def kosong(self):
        return self.count == 0

    def _tumbuh(self):
        baru = [None] * (self.kapasitas * 2)
        for i in range(self.count):
            baru[i] = self.data[(self.front + i) % self.kapasitas]
        self.data = baru
        self.kapasitas *= 2
        self.front = 0
        self.rear = self.count

    def enqueue(self, x):
        if self.count == self.kapasitas:
            self._tumbuh()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.kapasitas
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.kapasitas
        self.count -= 1
        return x

    def pop_back(self):
        if self.count == 0:
            return None
        self.rear = (self.rear - 1) % self.kapasitas
        x = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return x

    def push_front(self, x):
        if self.count == self.kapasitas:
            self._tumbuh()
        self.front = (self.front - 1) % self.kapasitas
        self.data[self.front] = x
        self.count += 1

    def isi(self):
        out = [None] * self.count
        for i in range(self.count):
            out[i] = self.data[(self.front + i) % self.kapasitas]
        return out


# ------------------------------------------------------- undo / redo + layanan
class LayananAntrean:
    """Dua antrean berisi pesanan yang sama + tumpukan undo/redo.

    Catatan aksi (disimpan secukupnya untuk dibalik):
      ("ENQUEUE", pesanan)               -> kebalikan: keluarkan dari BELAKANG kedua antrean
      ("DEQUEUE", versi, [pesanan...])   -> kebalikan: kembalikan seluruh daftar ke DEPAN antrean itu
    """

    def __init__(self):
        self.naif = AntreanNaif()
        self.circ = AntreanMelingkar()
        self.undo = Stack()
        self.redo = Stack()

    def isi_awal(self, p):
        """Memuat data awal ke kedua antrean (tidak dicatat di riwayat)."""
        self.naif.enqueue(p)
        self.circ.enqueue(p)

    def _antrean(self, versi):
        return self.naif if versi == "naif" else self.circ

    def enqueue(self, p):
        self.naif.enqueue(p)
        self.circ.enqueue(p)
        self.undo.push(("ENQUEUE", p))
        self.redo = Stack()                      # aksi baru mengosongkan redo

    def dequeue(self, versi, jumlah):
        """Mengembalikan (daftar_keluar, geser). Dicatat di undo bila ada yang keluar."""
        q = self._antrean(versi)
        geser0 = self.naif.total_geser
        buf = [None] * jumlah
        k = 0
        while k < jumlah:
            x = q.dequeue()
            if x is None:
                break
            buf[k] = x
            k += 1
        daftar = buf[:k]
        if k > 0:
            self.undo.push(("DEQUEUE", versi, daftar))
            self.redo = Stack()
        return daftar, self.naif.total_geser - geser0

    def undo_last(self):
        """Mengembalikan aksi yang dibatalkan, atau None bila tidak ada."""
        if self.undo.kosong():
            return None
        aksi = self.undo.pop()
        if aksi[0] == "ENQUEUE":
            self.naif.pop_back()
            self.circ.pop_back()
        else:
            q = self._antrean(aksi[1])
            daftar = aksi[2]
            for i in range(len(daftar) - 1, -1, -1):   # urutan asli kembali di depan
                q.push_front(daftar[i])
        self.redo.push(aksi)
        return aksi

    def redo_last(self):
        if self.redo.kosong():
            return None
        aksi = self.redo.pop()
        if aksi[0] == "ENQUEUE":                      # kerjakan aksi ASLI, bukan kebalikannya
            self.naif.enqueue(aksi[1])
            self.circ.enqueue(aksi[1])
        else:
            q = self._antrean(aksi[1])
            for _ in range(len(aksi[2])):
                q.dequeue()
        self.undo.push(aksi)                          # tidak mengosongkan redo
        return aksi

    def history(self):
        """Deskripsi aksi dari yang terlama ke terbaru."""
        isi = self.undo.isi()
        out = [None] * len(isi)
        for i in range(len(isi)):
            out[i] = deskripsi_aksi(isi[i])
        return out

    def stats(self):
        return (
            ("queue_len naif", len(self.naif)),
            ("queue_len circular", len(self.circ)),
            ("queue_capacity naif", self.naif.a.kapasitas),
            ("queue_capacity circular", self.circ.kapasitas),
            ("total geseran (naif)", self.naif.total_geser),
            ("undo_depth", len(self.undo)),
            ("redo_depth", len(self.redo)),
        )


def deskripsi_aksi(aksi):
    if aksi[0] == "ENQUEUE":
        return f"ENQUEUE {aksi[1].oid}"
    return f"DEQUEUE x{len(aksi[2])} ({aksi[1]})"
