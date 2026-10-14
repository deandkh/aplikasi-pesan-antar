"""Penghubung backend -> UI. Menyimpan keadaan (data, struktur, antrean) dan
mengubah tiap perintah menjadi objek Hasil yang siap ditampilkan."""
import time

from backend.data import Pesanan, baca_pesanan, NAMA_PRIORITAS
from backend.m1_pesanan import Array, LinkList
from backend.m2_antrean import LayananAntrean, ke_postfix, hitung, deskripsi_aksi
from backend.m3_laporan import (insertion_sort, merge_sort, linear_search,
                                binary_search, KUNCI_VALID)
from backend.util import (PesanError, Hitung, fmt_int, fmt_dec, fmt_rp, jam, ke_int)

BATAS_INSERTION = 20000
BATAS_DEQUEUE_NAIF = 1000
BARIS_TAMPIL = 100
JAM_DEFAULT = 28800          # 08:00:00
KOLOM_PESANAN = ["#", "oid", "pelanggan", "resto", "menu", "harga", "selesai"]


class Hasil:
    def __init__(self, modul, ringkas, kolom=None, baris=None, catatan="",
                 ms=0.0, extra_log=None):
        self.modul = modul
        self.ringkas = ringkas            # list teks
        self.kolom = kolom                # list nama kolom atau None
        self.baris = baris                # list list teks atau None
        self.catatan = catatan
        self.ms = ms
        self.extra_log = extra_log if extra_log is not None else []
        self.nama = ""


def _mulai():
    return time.perf_counter()


def _ms(t0):
    return (time.perf_counter() - t0) * 1000.0


def _detail(p):
    return [["oid", p.oid], ["pelanggan", p.pelanggan], ["resto", p.resto],
            ["menu", p.menu], ["harga", fmt_int(p.harga)],
            ["prioritas", f"{p.prioritas} ({NAMA_PRIORITAS[p.prioritas]})"],
            ["masuk", jam(p.masuk)],
            ["selesai", jam(p.selesai) if p.selesai is not None else "-"],
            ["status", p.status]]


def _tabel_pesanan(daftar, awal=0):
    n = len(daftar)
    if n > BARIS_TAMPIL:
        n = BARIS_TAMPIL
    baris = [None] * n
    for i in range(n):
        p = daftar[i]
        baris[i] = [str(awal + i + 1), p.oid, p.pelanggan, p.resto, p.menu,
                    fmt_int(p.harga), jam(p.selesai) if p.selesai is not None else "-"]
    return baris


def _norm_oid(teks):
    t = teks.strip().upper()
    if t.startswith("O-"):
        t = t[2:]
    if t == "" or not t.isdigit():
        raise PesanError("Format oid salah. Contoh: O-137442 atau 137442.")
    return "O-" + t.zfill(6)


class Sistem:
    def __init__(self):
        self.arr = None
        self.ll = None
        self.antre = None
        self.versi = 0                 # naik tiap Array M1 berubah (membuang indeks oid)
        self.indeks_oid = None
        self.indeks_versi = -1
        self.next_no = 1

    # ------------------------------------------------------------ util
    def _siap(self):
        if self.arr is None:
            raise PesanError("Data belum dimuat. Pilih menu 'Load' dulu.")

    def _baru(self, nama, resto, menu, harga, prioritas):
        nama = nama.strip()
        if nama == "" or resto.strip() == "" or menu.strip() == "":
            raise PesanError("Nama pelanggan, resto, dan menu tidak boleh kosong.")
        h = ke_int(harga, "Harga")
        if h <= 0:
            raise PesanError("Harga harus lebih dari 0.")
        p = Pesanan(f"O-{self.next_no:06d}", nama, resto.strip(), menu.strip(),
                    h, prioritas, JAM_DEFAULT, None, "ANTRE")
        self.next_no += 1
        return p

    # ------------------------------------------------------------ DATA
    def load(self, path):
        t0 = _mulai()
        arr = Array()
        ll = LinkList()
        antre = LayananAntrean()
        maks = 0
        for p in baca_pesanan(path):
            arr.append(p)
            ll.append(p)
            if p.status == "ANTRE":
                antre.isi_awal(p)
            no = int(p.oid[2:]) if p.oid[2:].isdigit() else 0
            if no > maks:
                maks = no
        self.arr, self.ll, self.antre = arr, ll, antre
        self.next_no = maks + 1
        self.versi += 1
        ms = _ms(t0)
        return Hasil("data", [
            f"{fmt_int(arr.n)} pesanan dimuat ke Array dan LinkedList.",
            f"{fmt_int(len(antre.circ))} pesanan berstatus ANTRE masuk ke KEDUA antrean.",
            f"Kapasitas Array {fmt_int(arr.kapasitas)} (disalin {fmt_int(arr.salin)} elemen "
            f"total saat tumbuh = amortized O(1) per append)."], ms=ms,
            catatan="Larik tumbuh 2x saat penuh; salinan jarang terjadi sehingga muat 200.000 baris cepat.")

    def stats(self):
        self._siap()
        baris = [["array_len", fmt_int(self.arr.n)],
                 ["array_capacity", fmt_int(self.arr.kapasitas)],
                 ["array_copied_total", fmt_int(self.arr.salin)],
                 ["linklist_len", fmt_int(self.ll.n)]]
        for nama, nilai in self.antre.stats():
            baris.append([nama, fmt_int(nilai)])
        baris.append(["next_oid", f"O-{self.next_no:06d}"])
        return Hasil("stats", ["Statistik keadaan sistem saat ini."],
                     ["metrik", "nilai"], baris)

    # ------------------------------------------------------------ M1
    def _struktur(self, nama):
        return self.arr if nama == "array" else self.ll

    def m1_lihat(self, struktur, i):
        self._siap()
        i = ke_int(i, "Indeks")
        s = self._struktur(struktur)
        t0 = _mulai()
        try:
            p = s.get(i)
        except IndexError as e:
            raise PesanError(str(e))
        ms = _ms(t0)
        kerja = (f"O(1): langsung ke alamat i, 0 langkah." if struktur == "array"
                 else f"O(n): menelusuri {fmt_int(s.langkah)} simpul dari head.")
        return Hasil("M1 - " + ("array" if struktur == "array" else "linklist"),
                     [f"Pesanan di indeks {fmt_int(i)} (dari {fmt_int(s.n)}). {kerja}"],
                     ["kolom", "isi"], _detail(p), ms=ms)

    def m1_tambah(self, struktur, jenis, nama, resto, menu, harga):
        self._siap()
        prio = 3 if jenis == "REGULER" else (2 if jenis == "PRIORITAS" else 1)
        p = self._baru(nama, resto, menu, harga, prio)
        s = self._struktur(struktur)
        if jenis == "REGULER":
            idx = s.n
        elif jenis == "PRIORITAS":
            idx = s.n // 2
        else:
            idx = 0
        kap0 = s.kapasitas if struktur == "array" else 0
        t0 = _mulai()
        s.insert(idx, p)
        ms = _ms(t0)
        if struktur == "array":
            self.versi += 1
            kerja = f"{fmt_int(s.langkah)} elemen digeser"
            if s.kapasitas != kap0:
                kerja += f"; kapasitas tumbuh {fmt_int(kap0)} -> {fmt_int(s.kapasitas)} (salin isi lama)"
        else:
            kerja = f"{fmt_int(s.langkah)} simpul ditelusuri"
        return Hasil("M1 - " + ("array" if struktur == "array" else "linklist"),
                     [f"{p.oid} ({jenis}) disisipkan di indeks {fmt_int(idx)}.",
                      f"{kerja}. Panjang sekarang {fmt_int(s.n)}."],
                     ["kolom", "isi"], _detail(p), ms=ms,
                     catatan="Bandingkan menu ARRAY vs LINKEDLIST untuk jenis yang sama: "
                             "selisihnya ada pada jumlah geseran vs telusur.")

    def m1_hapus(self, struktur, i):
        self._siap()
        i = ke_int(i, "Indeks")
        s = self._struktur(struktur)
        t0 = _mulai()
        try:
            p = s.remove(i)
        except IndexError as e:
            raise PesanError(str(e))
        ms = _ms(t0)
        if struktur == "array":
            self.versi += 1
            kerja = f"{fmt_int(s.langkah)} elemen digeser ke kiri"
        else:
            kerja = f"{fmt_int(s.langkah)} simpul ditelusuri"
        return Hasil("M1 - " + ("array" if struktur == "array" else "linklist"),
                     [f"{p.oid} dihapus dari indeks {fmt_int(i)}. {kerja}.",
                      f"Panjang sekarang {fmt_int(s.n)}."],
                     ["kolom", "isi"], _detail(p), ms=ms)

    # ------------------------------------------------------------ M2
    def m2_postfix(self, ekspresi):
        t0 = _mulai()
        log = Array()
        postfix = ke_postfix(ekspresi, log)
        total = hitung(postfix, log)
        ms = _ms(t0)
        pf = ""
        for k in range(len(postfix)):
            pf += (" " if k else "") + postfix[k]
        return Hasil("M2 - stack",
                     [f"Struk : {ekspresi.strip()}", f"Postfix: {pf}", f"TOTAL : {fmt_rp(total)}"],
                     ["langkah", "token", "tindakan", "stack", "output"],
                     [list(r) for r in log.isi()], ms=ms,
                     catatan="Baris 1.x = konversi, 2.x = evaluasi. '(' hanya mengatur stack, "
                             "pop pertama adalah operand kanan.")

    def m2_enqueue(self, nama, resto, menu, harga):
        self._siap()
        p = self._baru(nama, resto, menu, harga, 3)
        t0 = _mulai()
        self.antre.enqueue(p)
        ms = _ms(t0)
        return Hasil("M2 - queue",
                     [f"{p.oid} masuk ke barisan paling belakang pada KEDUA antrean.",
                      f"Panjang sekarang: naif {fmt_int(len(self.antre.naif))}, "
                      f"circular {fmt_int(len(self.antre.circ))}."],
                     ["kolom", "isi"], _detail(p), ms=ms,
                     catatan="enqueue murah di kedua versi (menempel di belakang). "
                             "Perbedaan baru muncul saat dequeue.")

    def m2_dequeue(self, versi, jumlah):
        self._siap()
        k = ke_int(jumlah, "Jumlah")
        if k < 1:
            raise PesanError("Jumlah dequeue minimal 1.")
        if versi == "naif" and k > BATAS_DEQUEUE_NAIF:
            raise PesanError(f"DITOLAK: batas dequeue naif {fmt_int(BATAS_DEQUEUE_NAIF)} per perintah "
                             f"(tiap dequeue menggeser seluruh isi).")
        t0 = _mulai()
        daftar, geser = self.antre.dequeue(versi, k)
        ms = _ms(t0)
        q = self.antre.naif if versi == "naif" else self.antre.circ
        n = len(daftar)
        if n == 0:
            return Hasil("M2 - queue " + versi, ["Antrean kosong: dequeue mengembalikan None."], ms=ms)
        if versi == "naif":
            rata = geser // n
            baris = [f"{fmt_int(n)} pesanan keluar dari depan antrean naif.",
                     f"Total {fmt_int(geser)} elemen digeser, rata-rata {fmt_int(rata)} geseran per dequeue.",
                     f"Sisa antrean naif {fmt_int(len(q))}."]
            cat = "Mengambil indeks 0 memaksa seluruh sisa isi bergeser satu petak: O(n) per dequeue."
        else:
            baris = [f"{fmt_int(n)} pesanan keluar dari depan antrean circular.",
                     f"Tidak ada elemen yang digeser. front={fmt_int(q.front)}, rear={fmt_int(q.rear)}, "
                     f"kapasitas={fmt_int(q.kapasitas)}.",
                     f"Sisa antrean circular {fmt_int(len(q))}."]
            cat = "Yang berpindah hanya penunjuk front (dengan modulo): O(1) per dequeue."
        if n > BARIS_TAMPIL:
            baris.append(f"(Tabel menampilkan {BARIS_TAMPIL} pesanan pertama.)")
        return Hasil("M2 - queue " + ("naif" if versi == "naif" else "circular"),
                     baris, KOLOM_PESANAN, _tabel_pesanan(daftar), cat, ms)

    def _lapor_aksi(self, kepala, aksi, ms, arah):
        a = self.antre
        if aksi[0] == "ENQUEUE":
            p = aksi[1]
            if arah == "undo":
                teks = f"Pembatalan enqueue: {p.oid} dikeluarkan lagi dari belakang."
            else:
                teks = f"Enqueue dikerjakan lagi: {p.oid} masuk kembali ke belakang."
            tabel = _tabel_pesanan([p])
        else:
            daftar = aksi[2]
            if arah == "undo":
                teks = (f"{fmt_int(len(daftar))} pesanan dikembalikan ke DEPAN antrean "
                        f"{'circular' if aksi[1] == 'circ' else 'naif'}.")
            else:
                teks = (f"{fmt_int(len(daftar))} pesanan keluar lagi dari antrean "
                        f"{'circular' if aksi[1] == 'circ' else 'naif'}.")
            tabel = _tabel_pesanan(daftar)
        return Hasil("M2 - stack",
                     [teks,
                      f"Panjang antrean sekarang: naif {fmt_int(len(a.naif))}, circular {fmt_int(len(a.circ))}. "
                      f"Tumpukan undo {len(a.undo)}, redo {len(a.redo)}."],
                     KOLOM_PESANAN, tabel, kepala, ms)

    def m2_undo(self):
        self._siap()
        t0 = _mulai()
        aksi = self.antre.undo_last()
        ms = _ms(t0)
        if aksi is None:
            return Hasil("M2 - stack", ["Tumpukan undo kosong, tidak ada yang dibatalkan."], ms=ms)
        return self._lapor_aksi("Undo menjalankan KEBALIKAN aksi (enqueue -> keluarkan dari belakang; "
                                "dequeue -> kembalikan ke depan).", aksi, ms, "undo")

    def m2_redo(self):
        self._siap()
        t0 = _mulai()
        aksi = self.antre.redo_last()
        ms = _ms(t0)
        if aksi is None:
            return Hasil("M2 - stack", ["Tumpukan redo kosong, tidak ada yang diulang."], ms=ms)
        return self._lapor_aksi("Redo mengerjakan ulang aksi ASLINYA (bukan kebalikannya). "
                                "Aksi baru apa pun mengosongkan tumpukan redo.", aksi, ms, "redo")

    def m2_riwayat(self):
        self._siap()
        h = self.antre.history()
        baris = [None] * len(h)
        for i in range(len(h)):
            baris[len(h) - 1 - i] = [str(len(h) - i), h[i]]      # terbaru di atas
        a = self.antre
        return Hasil("M2 - stack",
                     [f"Riwayat aksi: undo {len(a.undo)}, redo {len(a.redo)}. Terbaru di atas."],
                     ["#", "aksi"], baris)

    # ------------------------------------------------------------ M3
    def _jumlah(self, jumlah):
        n = ke_int(jumlah, "Jumlah baris")
        if n < 1:
            raise PesanError("Jumlah baris minimal 1.")
        if n > self.arr.n:
            raise PesanError(f"Jumlah baris melebihi data ({fmt_int(self.arr.n)}).")
        return n

    def m3_sort(self, algo, jumlah, kunci):
        self._siap()
        if kunci not in KUNCI_VALID:
            raise PesanError("Pilih kunci: oid, harga, atau selesai.")
        n = self._jumlah(jumlah)
        if algo == "insertion" and n > BATAS_INSERTION:
            raise PesanError(f"DITOLAK: batasnya {fmt_int(BATAS_INSERTION)} baris, "
                             f"pakai merge sort untuk data besar.")
        A = self.arr.data[:n]          # salinan n baris pertama; data asli tidak berubah
        cnt = Hitung()
        t0 = _mulai()
        if algo == "insertion":
            insertion_sort(A, kunci, cnt)
            hasil = A
            nama = "insertion sort"
        else:
            hasil = merge_sort(A, kunci, cnt)
            nama = "merge sort"
        ms = _ms(t0)
        baris = [f"{fmt_int(n)} pesanan terurut menurut {kunci}.",
                 f"{fmt_int(cnt.perbandingan)} perbandingan, {fmt_int(cnt.pemindahan)} pemindahan."]
        if n > BARIS_TAMPIL:
            baris.append(f"(Tabel menampilkan {BARIS_TAMPIL} baris pertama.)")
        cat = ("Setiap elemen digeser mundur sampai menemukan tempatnya: kerja ~ n^2/4. "
               "Lipatduakan n, perbandingan jadi ~4x." if algo == "insertion" else
               "Dibelah log n tingkat, tiap tingkat digabung O(n). Lipatduakan n, perbandingan ~2x. "
               "Jalankan menu lain pada jumlah & kunci sama, lalu bandingkan angkanya.")
        return Hasil("M3 - " + nama, baris, KOLOM_PESANAN, _tabel_pesanan(hasil), cat, ms)

    def m3_linear(self, oid):
        self._siap()
        target = _norm_oid(oid)
        A = self.arr.isi()
        cnt = Hitung()
        t0 = _mulai()
        i = linear_search(A, target, "oid", cnt)
        ms = _ms(t0)
        if i < 0:
            return Hasil("M3 - linear search",
                         [f"{target} tidak ditemukan.", f"{fmt_int(cnt.perbandingan)} perbandingan "
                          f"(kasus terburuk: seluruh {fmt_int(len(A))} baris)."], ms=ms)
        return Hasil("M3 - linear search",
                     [f"Ditemukan pada indeks {fmt_int(i)}.", f"{fmt_int(cnt.perbandingan)} perbandingan."],
                     ["kolom", "isi"], _detail(A[i]),
                     "Tidak butuh data terurut, tetapi setiap pesanan diperiksa satu per satu dari depan.", ms)

    def m3_binary(self, oid):
        self._siap()
        target = _norm_oid(oid)
        extra = []
        pesan_bangun = []
        if self.indeks_oid is None or self.indeks_versi != self.versi:
            cb = Hitung()
            t0 = _mulai()
            self.indeks_oid = merge_sort(self.arr.isi(), "oid", cb)
            self.indeks_versi = self.versi
            bangun = _ms(t0)
            extra.append(("merge_sort (indeks oid)", "M3 - merge sort", bangun))
            pesan_bangun = [f"Daftar terurut oid dibangun sekali dengan merge sort: "
                            f"{fmt_dec(bangun, 2)} ms ({fmt_int(cb.perbandingan)} perbandingan)."]
        A = self.indeks_oid
        cnt = Hitung()
        t0 = _mulai()
        i = binary_search(A, target, "oid", cnt)
        ms = _ms(t0)
        if i < 0:
            return Hasil("M3 - binary search", pesan_bangun + [f"{target} tidak ditemukan.",
                         f"{fmt_int(cnt.perbandingan)} perbandingan."], ms=ms, extra_log=extra)
        return Hasil("M3 - binary search",
                     pesan_bangun + [f"Ditemukan di baris ke-{fmt_int(i + 1)} dari {fmt_int(len(A))} baris terurut.",
                                     f"{fmt_int(cnt.perbandingan)} perbandingan, bandingkan dengan linear search."],
                     ["kolom", "isi"], _detail(A[i]),
                     "Tiap perbandingan membuang separuh sisa daftar. Syaratnya daftar SUDAH terurut "
                     "menurut kunci yang dicari; ongkos pengurutan dibayar sekali.", ms, extra)
