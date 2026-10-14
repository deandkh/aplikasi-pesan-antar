"""M1: Array (larik dinamis) vs LinkList (rantai).

Larik dibangun di atas list Python yang hanya dipakai sebagai petak memori
berukuran tetap ([None] * kapasitas). Tidak ada append/insert/pop bawaan list.
Kedua struktur menyimpan `langkah` = jumlah kerja operasi terakhir
(elemen digeser untuk Array, simpul ditelusuri untuk LinkList).
"""


class Array:
    def __init__(self, kapasitas=4):
        self.data = [None] * kapasitas
        self.kapasitas = kapasitas
        self.n = 0
        self.langkah = 0      # elemen digeser pada operasi terakhir
        self.salin = 0        # total elemen disalin saat tumbuh (kumulatif)
        self.tumbuh_terakhir = False

    def __len__(self):
        return self.n

    def _tumbuh(self):
        """Petak penuh -> petak baru 2x, salin isi lama, buang petak lama."""
        baru = [None] * (self.kapasitas * 2)
        for i in range(self.n):
            baru[i] = self.data[i]
        self.salin += self.n
        self.data = baru
        self.kapasitas *= 2
        self.tumbuh_terakhir = True

    def get(self, i):
        if i < 0 or i >= self.n:
            raise IndexError(f"indeks {i} di luar rentang 0..{self.n - 1}")
        self.langkah = 0
        return self.data[i]

    def append(self, v):
        """O(1) amortized."""
        self.tumbuh_terakhir = False
        if self.n == self.kapasitas:
            self._tumbuh()
        self.data[self.n] = v
        self.n += 1
        self.langkah = 0

    def insert(self, i, v):
        """O(n): geser elemen i..n-1 satu langkah ke kanan."""
        if i < 0 or i > self.n:
            raise IndexError(f"posisi sisip {i} di luar rentang 0..{self.n}")
        self.tumbuh_terakhir = False
        if self.n == self.kapasitas:
            self._tumbuh()
        j = self.n
        while j > i:
            self.data[j] = self.data[j - 1]
            j -= 1
        self.data[i] = v
        self.langkah = self.n - i
        self.n += 1

    def remove(self, i):
        """O(n): geser elemen i+1..n-1 satu langkah ke kiri. Mengembalikan nilai."""
        if i < 0 or i >= self.n:
            raise IndexError(f"indeks {i} di luar rentang 0..{self.n - 1}")
        nilai = self.data[i]
        for j in range(i, self.n - 1):
            self.data[j] = self.data[j + 1]
        self.langkah = self.n - 1 - i
        self.n -= 1
        self.data[self.n] = None
        return nilai

    def isi(self):
        """Salinan isi (hanya n elemen pertama) sebagai list."""
        return self.data[:self.n]


class Simpul:
    __slots__ = ("nilai", "next")

    def __init__(self, nilai):
        self.nilai = nilai
        self.next = None


class LinkList:
    def __init__(self):
        self.head = None
        self.tail = None       # disimpan agar append O(1)
        self.n = 0
        self.langkah = 0       # simpul ditelusuri pada operasi terakhir

    def __len__(self):
        return self.n

    def append(self, v):
        """O(1)"""
        baru = Simpul(v)
        if self.tail is None:
            self.head = baru
        else:
            self.tail.next = baru
        self.tail = baru
        self.n += 1
        self.langkah = 0

    def push_front(self, v):
        """O(1): hanya mengubah satu penunjuk."""
        baru = Simpul(v)
        baru.next = self.head
        self.head = baru
        if self.tail is None:
            self.tail = baru
        self.n += 1
        self.langkah = 0

    def get(self, i):
        """O(n): telusuri i simpul."""
        if i < 0 or i >= self.n:
            raise IndexError(f"indeks {i} di luar rentang 0..{self.n - 1}")
        p = self.head
        for _ in range(i):
            p = p.next
        self.langkah = i
        return p.nilai

    def insert(self, i, v):
        """O(n) telusur ke simpul i-1, lalu sambung sekali."""
        if i < 0 or i > self.n:
            raise IndexError(f"posisi sisip {i} di luar rentang 0..{self.n}")
        if i == 0:
            self.push_front(v)
            return
        if i == self.n:
            self.append(v)
            return
        p = self.head
        for _ in range(i - 1):
            p = p.next
        baru = Simpul(v)
        baru.next = p.next
        p.next = baru
        self.n += 1
        self.langkah = i - 1

    def remove(self, i):
        if i < 0 or i >= self.n:
            raise IndexError(f"indeks {i} di luar rentang 0..{self.n - 1}")
        if i == 0:
            nilai = self.head.nilai
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self.n -= 1
            self.langkah = 0
            return nilai
        prev = self.head
        for _ in range(i - 1):
            prev = prev.next
        target = prev.next
        prev.next = target.next
        if target is self.tail:
            self.tail = prev
        self.n -= 1
        self.langkah = i - 1
        return target.nilai
