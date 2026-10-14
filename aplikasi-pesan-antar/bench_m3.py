"""Benchmark M3: tabel n vs perbandingan (insertion vs merge) -> bench_m3.md (+ grafik bila ada matplotlib)."""
import random
import time
from backend.data import baca_pesanan
from backend.m3_laporan import insertion_sort, merge_sort
from backend.util import Hitung, fmt_int, fmt_dec

data = list(baca_pesanan("data/pesanan.csv"))
UKURAN = (500, 1000, 2000, 4000, 8000, 16000)
UKURAN_MERGE = UKURAN + (32000, 64000, 128000, 200000)
baris = []
hasil = {}
for n in UKURAN_MERGE:
    A = data[:n]
    cm = Hitung(); t = time.perf_counter(); merge_sort(A, "harga", cm); tm = (time.perf_counter() - t) * 1000
    ci = None; ti = None
    if n in UKURAN:
        B = data[:n]
        ci = Hitung(); t = time.perf_counter(); insertion_sort(B, "harga", ci); ti = (time.perf_counter() - t) * 1000
    hasil[n] = (ci, ti, cm, tm)
    print(n, ci.perbandingan if ci else "-", cm.perbandingan, flush=True)

out = ["| n | insertion: perbandingan | insertion: ms | merge: perbandingan | merge: ms | rasio perb. (ins/merge) |",
       "|---:|---:|---:|---:|---:|---:|"]
for n in UKURAN_MERGE:
    ci, ti, cm, tm = hasil[n]
    if ci:
        out.append(f"| {fmt_int(n)} | {fmt_int(ci.perbandingan)} | {fmt_dec(ti)} | {fmt_int(cm.perbandingan)} | {fmt_dec(tm)} | {fmt_dec(ci.perbandingan / cm.perbandingan, 1)}x |")
    else:
        out.append(f"| {fmt_int(n)} | (ditolak, > 20.000) | - | {fmt_int(cm.perbandingan)} | {fmt_dec(tm)} | - |")
open("bench_m3.md", "w").write("\n".join(out) + "\n")
print("\n".join(out))

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    xs_i = [n for n in UKURAN]
    plt.figure(figsize=(7, 4.2))
    plt.plot(xs_i, [hasil[n][0].perbandingan for n in xs_i], "o-", label="insertion sort  O(n²)")
    plt.plot(UKURAN_MERGE, [hasil[n][2].perbandingan for n in UKURAN_MERGE], "s-", label="merge sort  O(n log n)")
    plt.xscale("log"); plt.yscale("log")
    plt.xlabel("n (jumlah baris)"); plt.ylabel("jumlah perbandingan"); plt.grid(True, which="both", alpha=.3)
    plt.title("M3: n vs perbandingan"); plt.legend(); plt.tight_layout(); plt.savefig("docs_m3_grafik.png", dpi=130)
    print("grafik ok")
except ImportError:
    print("matplotlib tidak ada, grafik dilewati")
