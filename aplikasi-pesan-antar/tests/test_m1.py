import unittest
from backend.m1_pesanan import Array, LinkList


def isi_ll(ll):
    out = []
    p = ll.head
    while p is not None:
        out.append(p.nilai)
        p = p.next
    return out


class TestArray(unittest.TestCase):
    def test_append_tumbuh_dua_kali_dan_amortized(self):
        a = Array(4)
        for i in range(1000):
            a.append(i)
        self.assertEqual(a.isi(), list(range(1000)))
        self.assertEqual(a.kapasitas, 1024)
        self.assertLess(a.salin, 2 * 1000)          # bukan salin tiap append

    def test_insert_remove_get(self):
        a = Array()
        for i in range(5):
            a.append(i)
        a.insert(0, 99)
        self.assertEqual(a.langkah, 5)
        a.insert(3, 77)
        self.assertEqual(a.isi(), [99, 0, 1, 77, 2, 3, 4])
        self.assertEqual(a.remove(0), 99)
        self.assertEqual(a.langkah, 6)             # n=7 -> 6 elemen bergeser ke kiri
        self.assertEqual(a.remove(a.n - 1), 4)
        self.assertEqual(a.langkah, 0)
        self.assertEqual(a.get(2), 77)
        with self.assertRaises(IndexError):
            a.get(99)
        with self.assertRaises(IndexError):
            a.insert(99, 1)


class TestLinkList(unittest.TestCase):
    def test_sama_dengan_array(self):
        a, ll = Array(), LinkList()
        for i in range(10):
            a.append(i)
            ll.append(i)
        for (i, v) in ((0, 100), (5, 101), (a.n, 102), (3, 103)):
            a.insert(i, v)
            ll.insert(i, v)
        self.assertEqual(isi_ll(ll), a.isi())
        for pilih in ("awal", "tengah", "akhir", "tengah"):
            i = 0 if pilih == "awal" else (a.n - 1 if pilih == "akhir" else a.n // 2)
            self.assertEqual(ll.remove(i), a.remove(i))
        self.assertEqual(isi_ll(ll), a.isi())
        self.assertEqual(ll.n, a.n)

    def test_tail_tetap_benar(self):
        ll = LinkList()
        ll.append(1); ll.append(2); ll.append(3)
        ll.remove(2)                       # buang tail
        ll.append(9)
        self.assertEqual(isi_ll(ll), [1, 2, 9])
        ll.remove(0); ll.remove(0); ll.remove(0)
        self.assertIsNone(ll.head); self.assertIsNone(ll.tail)
        ll.append(5)
        self.assertEqual(isi_ll(ll), [5])

    def test_langkah(self):
        ll = LinkList()
        for i in range(100):
            ll.append(i)
        ll.push_front(-1); self.assertEqual(ll.langkah, 0)
        ll.get(50); self.assertEqual(ll.langkah, 50)
        ll.insert(50, 7); self.assertEqual(ll.langkah, 49)


if __name__ == "__main__":
    unittest.main()
