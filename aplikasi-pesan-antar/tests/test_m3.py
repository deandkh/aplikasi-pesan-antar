import random
import unittest
from backend.data import Pesanan
from backend.m3_laporan import insertion_sort, merge_sort, linear_search, binary_search
from backend.util import Hitung


def buat(kunci_harga):
    return [Pesanan(f"O-{i + 1:06d}", "x", "r", "m", h, 3, 0, None, "ANTRE")
            for i, h in enumerate(kunci_harga)]


def terurut(A, f):
    return all(f(A[i]) <= f(A[i + 1]) for i in range(len(A) - 1))


def stabil(A):
    """Harga sama -> oid (urutan masuk) harus tetap menaik."""
    return all(not (A[i].harga == A[i + 1].harga and A[i].oid > A[i + 1].oid)
               for i in range(len(A) - 1))


class TestSort(unittest.TestCase):
    def kasus(self):
        random.seed(1)
        n = 300
        return [
            [random.randint(1, 10**6) for _ in range(n)],        # acak
            list(range(n)),                                        # terurut
            list(range(n, 0, -1)),                                 # terbalik
            [random.choice((5, 6, 7)) for _ in range(n)],          # banyak duplikat
            [], [1], [2, 1],
        ]

    def test_dua_sort_benar_stabil_dan_identik(self):
        for harga in self.kasus():
            A = buat(harga)
            B = A[:]
            insertion_sort(B, "harga", Hitung())
            C = merge_sort(A, "harga", Hitung())
            self.assertTrue(terurut(B, lambda p: p.harga))
            self.assertTrue(stabil(B)); self.assertTrue(stabil(C))
            self.assertEqual([p.oid for p in B], [p.oid for p in C])
            self.assertEqual(len(C), len(harga))                  # tidak ada data hilang

    def test_merge_tidak_mengubah_input(self):
        A = buat([3, 1, 2])
        merge_sort(A, "harga", Hitung())
        self.assertEqual([p.harga for p in A], [3, 1, 2])

    def test_pola_perbandingan(self):
        random.seed(2)
        def hitung(n):
            A = buat([random.randint(1, 10**6) for _ in range(n)])
            ci, cm = Hitung(), Hitung()
            B = A[:]
            insertion_sort(B, "harga", ci)
            merge_sort(A, "harga", cm)
            return ci.perbandingan, cm.perbandingan
        i1, m1 = hitung(1000)
        i2, m2 = hitung(2000)
        self.assertTrue(3.5 < i2 / i1 < 4.5)      # kuadratik: ~4x
        self.assertTrue(1.9 < m2 / m1 < 2.3)      # n log n: ~2x

    def test_kunci_selesai_kosong_di_akhir(self):
        A = buat([1, 1, 1])
        A[0].selesai = None; A[1].selesai = 50; A[2].selesai = 10
        C = merge_sort(A, "selesai", Hitung())
        self.assertEqual([p.oid for p in C], ["O-000003", "O-000002", "O-000001"])


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.A = buat([0] * 1000)          # oid O-000001..O-001000 terurut

    def cari(self, fn, oid):
        c = Hitung()
        return fn(self.A, oid, "oid", c), c.perbandingan

    def test_empat_kasus_dan_kosong(self):
        for oid, idx in (("O-000500", 499), ("O-000001", 0), ("O-001000", 999), ("O-009999", -1)):
            self.assertEqual(self.cari(binary_search, oid)[0], idx)
            self.assertEqual(self.cari(linear_search, oid)[0], idx)
        self.assertEqual(binary_search([], "O-000001", "oid", Hitung()), -1)
        self.assertEqual(linear_search([], "O-000001", "oid", Hitung()), -1)

    def test_jumlah_perbandingan(self):
        self.assertEqual(self.cari(linear_search, "O-000500")[1], 500)
        self.assertLessEqual(self.cari(binary_search, "O-000500")[1], 10)
        self.assertLessEqual(self.cari(binary_search, "O-009999")[1], 10)


if __name__ == "__main__":
    unittest.main()
