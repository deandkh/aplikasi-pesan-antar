"""Satu jendela Tkinter: menu di kiri, form + hasil di kanan, COMMAND di bawah."""
import os
import tkinter as tk
from tkinter import ttk

from backend.sistem import Sistem
from backend.util import PesanError, fmt_ms

WARNA_HEADER = "#2b3a55"
WARNA_AKTIF = "#d6e4f7"
WARNA_GALAT = "#b00020"
WARNA_CATATAN = "#fff6dc"

# jenis isian: ("teks", label, default, bantuan) | ("combo", label, default, pilihan)
F_TAMBAH = (("teks", "Nama pelanggan", "Pelanggan Baru", "nama pesanan yang akan dibuat"),
            ("teks", "Resto", "kafe-teknik", ""),
            ("teks", "Menu", "roti-bakar", ""),
            ("teks", "Harga", "12000", "bilangan bulat > 0"))
F_INDEKS = (("teks", "Indeks (mulai 0)", "0", "posisi pesanan dalam struktur"),)
F_SORT = (("teks", "Jumlah baris diurutkan", "2000", "diambil dari awal data; coba 1.000, 2.000, 4.000"),
          ("combo", "Diurutkan menurut", "harga", ("oid", "harga", "selesai")))
F_OID = (("teks", "Nomor pesanan (oid)", "O-137442", "format O-000001 sampai O-200000"),)
F_DEQ = (("teks", "Berapa kali dequeue", "1", "coba 1 lalu 100 untuk melihat bedanya"),)


class Aplikasi:
    def __init__(self, root, folder_data):
        self.root = root
        self.folder = folder_data
        self.sistem = Sistem()
        self.menu = self._susun_menu()
        self.aktif = -1
        self.tombol = []
        self.widget_isian = []
        root.title("Aplikasi Pesan Antar")
        root.geometry("1220x800")
        root.minsize(1000, 640)
        self._bangun()
        self.pilih(0)

    # ------------------------------------------------------------ definisi menu
    def _susun_menu(self):
        s = self.sistem
        d = self.folder

        def tambah(struktur, jenis):
            return lambda v: s.m1_tambah(struktur, jenis, v[0], v[1], v[2], v[3])

        m = []
        m.append(("bagian", "DATA"))
        m.append(("menu", "load", "Load", "Muat data CSV",
                  "Membaca pesanan.csv (200.000 baris) ke Array, LinkedList, dan kedua antrean.",
                  (), "MUAT", lambda v: s.load(os.path.join(d, "pesanan.csv"))))
        m.append(("menu", "stats", "Statistik", "Statistik sistem",
                  "Panjang, kapasitas, total geseran, kedalaman undo/redo.",
                  (), "TAMPILKAN", lambda v: s.stats()))

        m.append(("bagian", "M1 - DATA PESANAN"))
        for nama_s, kunci_s, awalan in (("ARRAY", "array", "array"), ("LINKEDLIST", "linked", "linked")):
            tampil = "Array" if kunci_s == "array" else "Linked list"
            m.append(("menu", f"{awalan}_lihat", f"{nama_s} - LIHAT PESANAN", f"{tampil}: lihat pesanan ke-i",
                      "Array O(1) langsung ke alamat; linked list O(n) menelusuri simpul.",
                      F_INDEKS, "LIHAT", (lambda ks: (lambda v: s.m1_lihat(ks, v[0])))(kunci_s)))
            for jenis, ket in (("REGULER", "masuk paling belakang"),
                               ("PRIORITAS", "menyerobot ke tengah barisan"),
                               ("VIP", "langsung ke urutan pertama")):
                m.append(("menu", f"{awalan}_{jenis.lower()}", f"{nama_s} - TAMBAH PESANAN {jenis}",
                          f"{tampil}: pesanan {jenis}, {ket}",
                          f"Menyisipkan {ket}. Lihat berapa elemen digeser / simpul ditelusuri.",
                          F_TAMBAH, "TAMBAH", tambah(kunci_s, jenis)))
            m.append(("menu", f"{awalan}_hapus", f"{nama_s} - HAPUS PESANAN", f"{tampil}: hapus pesanan ke-i",
                      "Array menggeser sisa ke kiri; linked list menelusuri lalu menyambung ulang.",
                      F_INDEKS, "HAPUS", (lambda ks: (lambda v: s.m1_hapus(ks, v[0])))(kunci_s)))

        m.append(("bagian", "M2 - STACK DAN QUEUE"))
        m.append(("menu", "stack_postfix", "STACK - POSTFIX (MESIN KASIR)",
                  "Stack: hitung struk lewat postfix",
                  "Struk ditulis infix, diubah ke postfix (tahap 1), lalu dievaluasi (tahap 2), keduanya memakai stack.",
                  (("teks", "Struk belanja (infix)", "( 3 * 12000 ) + ( 2 * 8500 ) - 5000",
                    "angka, + - * / dan tanda kurung, dipisah spasi atau rapat"),), "HITUNG",
                  lambda v: s.m2_postfix(v[0])))
        m.append(("menu", "stack_undo", "STACK - UNDO", "Stack: batalkan aksi antrean terakhir",
                  "Mengambil catatan teratas tumpukan undo, lalu menjalankan kebalikannya.",
                  (), "UNDO", lambda v: s.m2_undo()))
        m.append(("menu", "stack_redo", "STACK - REDO", "Stack: kerjakan lagi aksi yang dibatalkan",
                  "Mengambil catatan teratas tumpukan redo, lalu mengerjakan ulang aksi aslinya.",
                  (), "REDO", lambda v: s.m2_redo()))
        m.append(("menu", "stack_riwayat", "STACK - RIWAYAT", "Stack: isi tumpukan undo",
                  "Daftar aksi yang masih bisa dibatalkan.", (), "TAMPILKAN", lambda v: s.m2_riwayat()))
        m.append(("menu", "queue_enqueue", "QUEUE - ENQUEUE", "Queue: pesanan baru masuk ke belakang",
                  "Menambah pesanan di ujung belakang KEDUA antrean (naif dan circular) sekaligus.",
                  F_TAMBAH, "ENQUEUE", lambda v: s.m2_enqueue(v[0], v[1], v[2], v[3])))
        m.append(("menu", "queue_dequeue_naive", "QUEUE - DEQUEUE NAIF", "Queue naif: ambil dari depan dengan menggeser isi",
                  "Mengambil indeks 0 lalu menggeser seluruh sisa isi satu petak ke kiri. Biayanya O(n) setiap kali.",
                  F_DEQ, "DEQUEUE", lambda v: s.m2_dequeue("naif", v[0])))
        m.append(("menu", "queue_dequeue_circular", "QUEUE - DEQUEUE CIRCULAR", "Queue circular: ambil dari depan dengan memajukan penunjuk",
                  "Hanya penunjuk front yang maju, isi larik tidak digeser sama sekali. O(1).",
                  F_DEQ, "DEQUEUE", lambda v: s.m2_dequeue("circ", v[0])))

        m.append(("bagian", "M3 - SORT DAN SEARCH"))
        m.append(("menu", "insertion_sort", "SORT - INSERTION SORT", "Sort: insertion sort, O(n²)",
                  "Setiap elemen digeser mundur sampai menemukan tempatnya. Sederhana, tetapi kerjanya tumbuh kuadratik.",
                  F_SORT, "URUTKAN", lambda v: s.m3_sort("insertion", v[0], v[1])))
        m.append(("menu", "merge_sort", "SORT - MERGE SORT", "Sort: merge sort, O(n log n)",
                  "Larik dibelah terus-menerus, lalu potongan yang sudah terurut disatukan kembali.",
                  F_SORT, "URUTKAN", lambda v: s.m3_sort("merge", v[0], v[1])))
        m.append(("menu", "linear_search", "SEARCH - LINEAR SEARCH", "Search: linear search, O(n)",
                  "Memeriksa pesanan satu per satu dari depan. Tidak menuntut data terurut.",
                  F_OID, "CARI", lambda v: s.m3_linear(v[0])))
        m.append(("menu", "binary_search", "SEARCH - BINARY SEARCH", "Search: binary search, O(log n)",
                  "Membuang separuh sisa daftar pada setiap perbandingan. Menuntut daftar terurut menurut oid.",
                  F_OID, "CARI", lambda v: s.m3_binary(v[0])))
        return m

    # ------------------------------------------------------------ tata letak
    def _bangun(self):
        r = self.root
        tk.Label(r, text="Aplikasi Pesan Antar", bg=WARNA_HEADER, fg="white",
                 font=("Helvetica", 14, "bold"), anchor="w", padx=12, pady=8).pack(fill="x")

        self.status = tk.Label(r, text="Siap. Pilih menu Load untuk memuat data.", anchor="w",
                               bg="#1f2a40", fg="white", font=("Courier", 10), padx=10, pady=3)
        self.status.pack(side="bottom", fill="x")

        isi = tk.Frame(r)
        isi.pack(fill="both", expand=True)

        # --- kiri: daftar menu yang bisa digulir
        kiri = tk.Frame(isi, width=290)
        kiri.pack(side="left", fill="y")
        kiri.pack_propagate(False)
        self.kanvas = tk.Canvas(kiri, highlightthickness=0, width=270)
        sb = ttk.Scrollbar(kiri, orient="vertical", command=self.kanvas.yview)
        self.kanvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.kanvas.pack(side="left", fill="both", expand=True)
        dalam = tk.Frame(self.kanvas)
        self.kanvas.create_window((0, 0), window=dalam, anchor="nw")
        dalam.bind("<Configure>", lambda e: self.kanvas.configure(scrollregion=self.kanvas.bbox("all")))
        self.kanvas.bind("<Enter>", self._ikat_roda)
        self.kanvas.bind("<Leave>", self._lepas_roda)

        self.tombol = [None] * len(self.menu)
        for i in range(len(self.menu)):
            item = self.menu[i]
            if item[0] == "bagian":
                tk.Label(dalam, text=item[1], font=("Helvetica", 9, "bold"), fg="#44546a",
                         anchor="w").pack(fill="x", padx=6, pady=(10, 2))
            else:
                b = tk.Button(dalam, text=item[2], anchor="w", relief="groove", padx=8,
                              font=("Helvetica", 10), command=lambda k=i: self.pilih(k))
                b.pack(fill="x", padx=6, pady=1)
                self.tombol[i] = b

        # --- kanan
        kanan = tk.Frame(isi, padx=12, pady=8)
        kanan.pack(side="left", fill="both", expand=True)
        self.lbl_judul = tk.Label(kanan, text="", font=("Helvetica", 13, "bold"), anchor="w")
        self.lbl_judul.pack(fill="x")
        self.lbl_desk = tk.Label(kanan, text="", anchor="w", justify="left", fg="#555", wraplength=860)
        self.lbl_desk.pack(fill="x", pady=(0, 6))
        self.bingkai_form = tk.Frame(kanan)
        self.bingkai_form.pack(fill="x")
        self.tombol_jalan = ttk.Button(kanan, text="JALANKAN", command=self.jalankan)
        self.tombol_jalan.pack(anchor="w", pady=6)
        ttk.Separator(kanan).pack(fill="x", pady=4)
        self.lbl_hasil = tk.Label(kanan, text="", anchor="w", justify="left", wraplength=860,
                                  font=("Helvetica", 10))
        self.lbl_hasil.pack(fill="x")

        tabel = tk.Frame(kanan)
        tabel.pack(fill="both", expand=True, pady=4)
        self.tree = ttk.Treeview(tabel, show="headings")
        ys = ttk.Scrollbar(tabel, orient="vertical", command=self.tree.yview)
        xs = ttk.Scrollbar(tabel, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        ys.pack(side="right", fill="y")
        xs.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        tk.Label(kanan, text="COMMAND", font=("Helvetica", 8, "bold"), anchor="w").pack(fill="x")
        kb = tk.Frame(kanan)
        kb.pack(fill="x")
        self.log = tk.Text(kb, height=7, font=("Courier", 9), state="disabled", wrap="none")
        ls = ttk.Scrollbar(kb, orient="vertical", command=self.log.yview)
        self.log.configure(yscrollcommand=ls.set)
        ls.pack(side="right", fill="y")
        self.log.pack(side="left", fill="x", expand=True)
        self.lbl_catatan = tk.Label(kanan, text="", anchor="w", justify="left", bg=WARNA_CATATAN,
                                    wraplength=860, padx=8, pady=4, font=("Helvetica", 9))
        self.lbl_catatan.pack(fill="x", pady=(6, 0))

    def _ikat_roda(self, _e):
        self.kanvas.bind_all("<MouseWheel>", self._roda)
        self.kanvas.bind_all("<Button-4>", lambda e: self.kanvas.yview_scroll(-1, "units"))
        self.kanvas.bind_all("<Button-5>", lambda e: self.kanvas.yview_scroll(1, "units"))

    def _lepas_roda(self, _e):
        self.kanvas.unbind_all("<MouseWheel>")
        self.kanvas.unbind_all("<Button-4>")
        self.kanvas.unbind_all("<Button-5>")

    def _roda(self, e):
        arah = -1 if e.delta > 0 else 1
        self.kanvas.yview_scroll(arah, "units")

    # ------------------------------------------------------------ interaksi
    def pilih(self, i):
        item = self.menu[i]
        if item[0] == "bagian":
            return
        if self.aktif >= 0 and self.tombol[self.aktif] is not None:
            self.tombol[self.aktif].configure(bg=self.root.cget("bg"))
        self.aktif = i
        self.tombol[i].configure(bg=WARNA_AKTIF)
        _, _id, _label, judul, desk, fields, teks_tombol, _h = item
        self.lbl_judul.configure(text=judul)
        self.lbl_desk.configure(text=desk)
        self.tombol_jalan.configure(text=teks_tombol)
        for w in self.bingkai_form.winfo_children():
            w.destroy()
        self.widget_isian = [None] * len(fields)
        for k in range(len(fields)):
            jenis, label, default, extra = fields[k]
            tk.Label(self.bingkai_form, text=label, font=("Helvetica", 9, "bold"),
                     anchor="w").grid(row=2 * k, column=0, sticky="w")
            if jenis == "combo":
                w = ttk.Combobox(self.bingkai_form, values=list(extra), state="readonly", width=24)
                w.set(default)
            else:
                w = ttk.Entry(self.bingkai_form, width=46)
                w.insert(0, default)
                if extra:
                    tk.Label(self.bingkai_form, text=extra, fg="#777", font=("Helvetica", 8),
                             anchor="w").grid(row=2 * k + 1, column=0, sticky="w")
            w.grid(row=2 * k, column=1, sticky="w", padx=8, pady=2)
            self.widget_isian[k] = w
        self._tampil_hasil(None)

    def _baca_isian(self):
        nilai = [None] * len(self.widget_isian)
        for k in range(len(self.widget_isian)):
            nilai[k] = self.widget_isian[k].get()
        return nilai

    def jalankan(self):
        item = self.menu[self.aktif]
        nama, handler = item[1], item[7]
        self.root.configure(cursor="watch")
        self.root.update_idletasks()
        try:
            h = handler(self._baca_isian())
            h.nama = nama
            self._tampil_hasil(h)
            for (n2, modul2, ms2) in h.extra_log:
                self._catat(n2, modul2, ms2)
            self._catat(nama, h.modul, h.ms)
            self.status.configure(text=f"[{h.modul}] {fmt_ms(h.ms)}")
        except PesanError as e:
            self._tampil_galat(str(e))
            self._catat(nama, "GALAT", 0.0)
        except Exception as e:                       # jaring pengaman: jangan matikan jendela
            self._tampil_galat(f"Galat tak terduga: {type(e).__name__}: {e}")
            self._catat(nama, "GALAT", 0.0)
        finally:
            self.root.configure(cursor="")

    def _catat(self, nama, modul, ms):
        baris = f"{nama:<24}-> {modul:<24}{fmt_ms(ms):>11}\n"
        self.log.configure(state="normal")
        self.log.insert("1.0", baris)
        self.log.configure(state="disabled")

    def _tampil_galat(self, pesan):
        self._isi_tabel(None, None)
        self.lbl_hasil.configure(text=pesan, fg=WARNA_GALAT)
        self.lbl_catatan.configure(text="")
        self.status.configure(text="[galat] " + pesan[:100])

    def _tampil_hasil(self, h):
        if h is None:
            self.lbl_hasil.configure(text="", fg="black")
            self.lbl_catatan.configure(text="")
            self._isi_tabel(None, None)
            return
        self.lbl_hasil.configure(text="\n".join(h.ringkas), fg="black")
        self.lbl_catatan.configure(text=h.catatan)
        self._isi_tabel(h.kolom, h.baris)

    def _isi_tabel(self, kolom, baris):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        if kolom is None:
            self.tree["columns"] = ()
            return
        self.tree["columns"] = list(kolom)
        for c in range(len(kolom)):
            lebar = len(kolom[c])
            for r in range(min(len(baris), 60)):
                if len(baris[r][c]) > lebar:
                    lebar = len(baris[r][c])
            px = max(50, min(520, lebar * 8 + 16))
            self.tree.heading(kolom[c], text=kolom[c])
            self.tree.column(kolom[c], width=px, anchor="w", stretch=(c == len(kolom) - 1))
        for r in range(len(baris)):
            self.tree.insert("", "end", values=baris[r])


def jalankan_aplikasi(folder_data):
    root = tk.Tk()
    Aplikasi(root, folder_data)
    root.mainloop()
