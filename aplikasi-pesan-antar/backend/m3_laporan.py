"""M3: insertion sort, merge sort (stabil), linear search, binary search.

Semua algoritma melaporkan jumlah perbandingan (dan pemindahan) lewat pencacah `Hitung`.
Kunci pengurutan: "oid", "harga", "selesai" (selesai kosong dianggap paling akhir).
"""
from backend.util import PesanError

KUNCI_VALID = ("oid", "harga", "selesai")
BESAR = 10 ** 9


def ambil_kunci(p, kunci):
    if kunci == "oid":
        return p.oid
    if kunci == "harga":
        return p.harga
    if kunci == "selesai":
        return p.selesai if p.selesai is not None else BESAR
    raise PesanError(f"Kunci tidak dikenal: {kunci}")


def _kunci_larik(A, kunci):
    n = len(A)
    K = [None] * n
    for i in range(n):
        K[i] = ambil_kunci(A[i], kunci)
    return K


def insertion_sort(A, kunci, cnt):
    """Di tempat, stabil. Menggeser hanya bila K[j] > kunci (BUKAN >=). O(n^2)."""
    n = len(A)
    K = _kunci_larik(A, kunci)
    perb = 0
    pindah = 0
    for i in range(1, n):
        k = K[i]
        x = A[i]
        j = i - 1
        while j >= 0:
            perb += 1
            if K[j] > k:
                K[j + 1] = K[j]
                A[j + 1] = A[j]
                pindah += 1
                j -= 1
            else:
                break
        if j + 1 != i:
            K[j + 1] = k
            A[j + 1] = x
            pindah += 1
    cnt.perbandingan += perb
    cnt.pemindahan += pindah


def merge_sort(A, kunci, cnt):
    """Bottom-up, stabil (kiri didahulukan saat sama: <=). Mengembalikan list baru. O(n log n).
    Yang diurutkan adalah larik indeks `idx` menurut K; A sendiri tidak diubah."""
    n = len(A)
    K = _kunci_larik(A, kunci)
    src = [0] * n
    for i in range(n):
        src[i] = i
    dst = [0] * n
    perb = 0
    pindah = 0
    lebar = 1
    while lebar < n:
        lo = 0
        while lo < n:
            mid = lo + lebar
            hi = lo + 2 * lebar
            if mid > n:
                mid = n
            if hi > n:
                hi = n
            i = lo
            j = mid
            k = lo
            while i < mid and j < hi:
                perb += 1
                if K[src[i]] <= K[src[j]]:
                    dst[k] = src[i]
                    i += 1
                else:
                    dst[k] = src[j]
                    j += 1
                k += 1
            while i < mid:               # sisa kiri (jangan sampai tidak disalin)
                dst[k] = src[i]
                i += 1
                k += 1
            while j < hi:                # sisa kanan
                dst[k] = src[j]
                j += 1
                k += 1
            pindah += hi - lo
            lo = hi
        src, dst = dst, src
        lebar *= 2
    cnt.perbandingan += perb
    cnt.pemindahan += pindah
    hasil = [None] * n
    for i in range(n):
        hasil[i] = A[src[i]]
    return hasil


def linear_search(A, target, kunci, cnt):
    """Telusuri satu per satu. Mengembalikan indeks atau -1. O(n)."""
    for i in range(len(A)):
        cnt.perbandingan += 1
        if ambil_kunci(A[i], kunci) == target:
            return i
    return -1


def binary_search(A, target, kunci, cnt):
    """A WAJIB sudah terurut menurut `kunci`. lo <= hi (bukan <). O(log n)."""
    lo = 0
    hi = len(A) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        cnt.perbandingan += 1
        v = ambil_kunci(A[mid], kunci)
        if v == target:
            return mid
        if v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
