import unittest
from backend.m2_antrean import (Stack, ke_postfix, hitung, pecah_token,
                                AntreanNaif, AntreanMelingkar, LayananAntrean)
from backend.util import PesanError


def total(s):
    return hitung(ke_postfix(s))


class TestKasir(unittest.TestCase):
    def test_contoh_pdf(self):
        s = "( 3 * 12000 ) + ( 2 * 8500 ) - 5000"
        self.assertEqual(" ".join(ke_postfix(s)), "3 12000 * 2 8500 * + 5000 -")
        self.assertEqual(total(s), 48000)

    def test_token_multi_digit(self):
        self.assertEqual(pecah_token("12000*3"), ["12000", "*", "3"])

    def test_empat_kasus(self):
        self.assertEqual(total("2 + 3 * 4"), 14)             # tanpa kurung
        self.assertEqual(total("( 2 + 3 ) * 4"), 20)         # berkurung
        self.assertEqual(total("10 - 3 - 2"), 5)             # '-' beruntun (kiri ke kanan)
        self.assertEqual(total("2 * ( 3 + ( 4 - 1 ) * 2 )"), 18)  # bersarang

    def test_urutan_pop_minus_dan_bagi(self):
        self.assertEqual(total("20 - 5"), 15)
        self.assertEqual(total("100 / 5 / 2"), 10)
        self.assertEqual(total("100 / ( 5 / 2 )"), 40)
        self.assertEqual(total("7 / 2"), 3.5)

    def test_galat(self):
        for bad in ("", "( 1 + 2", "1 + 2 )", "1 +", "5 / 0", "2 $ 3", "1 2"):
            with self.assertRaises(PesanError, msg=bad):
                total(bad)


class TestAntrean(unittest.TestCase):
    def test_melingkar_putar_k4(self):
        q = AntreanMelingkar(4)
        for x in (1, 2, 3):
            q.enqueue(x)
        self.assertEqual((q.dequeue(), q.dequeue()), (1, 2))
        for x in (4, 5, 6):
            q.enqueue(x)                  # rear berputar melewati ujung
        self.assertEqual(q.kapasitas, 4)
        self.assertEqual(q.isi(), [3, 4, 5, 6])
        q.enqueue(7)                      # penuh -> tumbuh, urutan tetap
        self.assertEqual(q.isi(), [3, 4, 5, 6, 7])
        self.assertEqual(q.kapasitas, 8)

    def test_kosong_dan_penuh_tidak_ambigu(self):
        q = AntreanMelingkar(2)
        self.assertIsNone(q.dequeue())
        q.enqueue(1); q.enqueue(2)
        self.assertEqual(q.front, q.rear)  # penuh, tapi count membedakan
        self.assertFalse(q.kosong())
        q.dequeue(); q.dequeue()
        self.assertTrue(q.kosong())

    def test_naif_sama_dengan_melingkar_dan_hitung_geser(self):
        n, c = AntreanNaif(), AntreanMelingkar()
        for i in range(50):
            n.enqueue(i); c.enqueue(i)
        for _ in range(20):
            self.assertEqual(n.dequeue(), c.dequeue())
        self.assertEqual(n.total_geser, sum(49 - k for k in range(20)))
        self.assertEqual(n.isi(), c.isi())


class P:
    def __init__(self, oid): self.oid = oid


class TestUndoRedo(unittest.TestCase):
    def siap(self, n=10):
        a = LayananAntrean()
        for i in range(n):
            a.isi_awal(P(i))
        return a

    def oids(self, q):
        return [p.oid for p in q.isi()]

    def test_undo_redo_dequeue_urutan_kembali(self):
        a = self.siap()
        awal = self.oids(a.circ)
        daftar, _ = a.dequeue("circ", 4)
        self.assertEqual(len(a.circ), 6)
        a.undo_last()
        self.assertEqual(self.oids(a.circ), awal)          # kembali ke DEPAN, urutan asli
        a.redo_last()
        self.assertEqual(self.oids(a.circ), awal[4:])
        self.assertEqual((len(a.undo), len(a.redo)), (1, 0))

    def test_undo_redo_enqueue(self):
        a = self.siap(3)
        a.enqueue(P(99))
        self.assertEqual((len(a.naif), len(a.circ)), (4, 4))
        a.undo_last()
        self.assertEqual((len(a.naif), len(a.circ)), (3, 3))
        a.redo_last()
        self.assertEqual(self.oids(a.circ)[-1], 99)

    def test_aksi_baru_mengosongkan_redo(self):
        a = self.siap()
        a.dequeue("circ", 2)
        a.undo_last()
        self.assertEqual(len(a.redo), 1)
        a.enqueue(P(50))
        self.assertEqual(len(a.redo), 0)
        self.assertIsNone(a.redo_last())

    def test_undo_kosong(self):
        self.assertIsNone(self.siap().undo_last())

    def test_dequeue_naif_undo(self):
        a = self.siap()
        awal = self.oids(a.naif)
        a.dequeue("naif", 3)
        a.undo_last()
        self.assertEqual(self.oids(a.naif), awal)


if __name__ == "__main__":
    unittest.main()
