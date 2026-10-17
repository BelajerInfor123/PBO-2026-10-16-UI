"""
tambah_barang.py - Modul Penambahan Data Barang Inventaris Gudang.
"""

import csv
import os
import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from ui import (
    buat_header,
    buat_form,
    buat_entry,
    buat_tombol,
    center_window,
    BG_APP
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "barang.csv")


def simpan_barang(entry_nama, entry_kategori, entry_sku):
    nama_barang = entry_nama.get().strip()
    kategori = entry_kategori.get().strip() if hasattr(entry_kategori, 'get') else str(entry_kategori)
    kode_sku = entry_sku.get().strip()

    if not nama_barang or not kategori or not kode_sku:
        messagebox.showwarning(
            "Peringatan",
            "Semua data harus diisi!"
        )
        return False

    # Validasi duplikasi SKU unik (case-insensitive)
    if os.path.exists(CSV_PATH) and os.path.getsize(CSV_PATH) > 0:
        try:
            with open(CSV_PATH, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)
                for row in reader:
                    if len(row) >= 3 and row[2].strip().upper() == kode_sku.upper():
                        messagebox.showerror(
                            "Gagal",
                            f"Kode SKU '{kode_sku}' sudah terdaftar! Gunakan SKU lain."
                        )
                        return False
        except Exception:
            pass

    file_baru = not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0

    with open(
        CSV_PATH,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)

        if file_baru:
            writer.writerow([
                "nama_barang",
                "kategori",
                "kode_sku",
                "status"
            ])

        writer.writerow([
            nama_barang,
            kategori,
            kode_sku,
            "Tersedia"
        ])

    toast_shown = False
    try:
        from ui import show_toast
        t = show_toast(entry_nama, f"Data barang '{nama_barang}' berhasil disimpan!", "success")
        toast_shown = t is not None
    except Exception:
        toast_shown = False

    if not toast_shown:
        messagebox.showinfo(
            "Sukses",
            f"Data barang '{nama_barang}' berhasil disimpan!"
        )

    if hasattr(entry_nama, 'delete'):
        entry_nama.delete(0, tk.END)
    if hasattr(entry_kategori, 'delete'):
        entry_kategori.delete(0, tk.END)
    if hasattr(entry_sku, 'delete'):
        entry_sku.delete(0, tk.END)

    if hasattr(entry_nama, 'focus'):
        entry_nama.focus()

    return True


# ==================================
# WINDOW
# ==================================

root = ctk.CTk()
root.title("Tambah Barang")
root.geometry("740x600")
center_window(root, 740, 600)
root.configure(fg_color=BG_APP)


# ==================================
# HEADER DARI ui.py
# ==================================

buat_header(
    root,
    "TAMBAH DATA BARANG",
    "#059669"
)


# ==================================
# FORM DARI ui.py
# ==================================

form = buat_form(root)


# ==================================
# ENTRY DARI ui.py
# ==================================

entry_nama = buat_entry(
    form,
    "Nama Barang"
)

entry_kategori = buat_entry(
    form,
    "Kategori"
)

entry_sku = buat_entry(
    form,
    "Kode SKU"
)


# ==================================
# FRAME TOMBOL
# ==================================

frm = ctk.CTkFrame(
    form,
    fg_color="transparent"
)

frm.pack(
    fill="x",
    padx=24,
    pady=(16, 0)
)


# ==================================
# BUTTON DARI ui.py
# ==================================

buat_tombol(
    frm,
    "💾 Simpan Barang",
    lambda: simpan_barang(
        entry_nama,
        entry_kategori,
        entry_sku
    ),
    "#059669",
    side="none"
).pack(
    fill="x",
    pady=4
)


if __name__ == "__main__":
    root.mainloop()