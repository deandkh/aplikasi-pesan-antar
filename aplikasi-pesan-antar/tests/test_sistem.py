import os
import unittest
from backend.sistem import Sistem
from backend.util import PesanError

CSV = os.path.join(os.path.dirname(__file__), "..", "data", "pesanan.csv")


class TestSistem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = Sistem()
        cls.s.load(CSV)

    def test_load_sesuai_pdf(self):
        self.assertEqual(self.s.arr.n, 200000)
        self.assertEqual(self.s.ll.n, 200000)
        self.assertEqual(self.s.antre.stats()[0][1], 19850 + (len(self.s.antre.naif) - 19850))

    def test_nama_dengan_koma(self):
        self.assertEqual(self.s.arr.get(3).pelanggan, "Oskar Puspita, S.Sos")

    def test_belum_load(self):
        with self.assertRaises(PesanError):
            Sistem().m1_lihat("array", "0")

    def test_search_cocok_dan_perbandingan(self):
        h = self.s.m3_linear("O-137442")
        self.assertTrue("137.441" in h.ringkas[0] and "137.442 perbandingan" in h.ringkas[1])
        h = self.s.m3_binary("137442")
        self.assertTrue(any("perbandingan" in r for r in h.ringkas))
        self.assertEqual(h.baris[0][1], "O-137442")
        with self.assertRaises(PesanError):
            self.s.m3_linear("abc")

    def test_insertion_ditolak(self):
        with self.assertRaises(PesanError):
            self.s.m3_sort("insertion", "20001", "harga")

    def test_alur_undo(self):
        s = Sistem(); s.load(CSV)
        n0 = len(s.antre.circ)
        s.m2_enqueue("Pelanggan Baru", "kafe-teknik", "roti-bakar", "12000")
        s.m2_dequeue("circ", "100")
        s.m2_undo(); s.m2_redo()
        s.m2_enqueue("Pencabang", "kafe-teknik", "roti-bakar", "12000")
        self.assertIn("kosong", s.m2_redo().ringkas[0])
        self.assertEqual(len(s.antre.circ), n0 + 2 - 100)


if __name__ == "__main__":
    unittest.main()
