"""
tampil_barang.py - Modul Penampilan & Eksplorasi Inventaris Gudang.
"""

import csv
import os
import sys
import customtkinter as ctk

from ui import (
    buat_header,
    buat_treeview,
    buat_tombol,
    buat_label_total,
    center_window,
    BG_APP
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "barang.csv")


def tampilkan_barang(tree, label):
    # Hapus data lama
    for item in tree.get_children():
        tree.delete(item)

    jumlah_barang = 0

    # Cek apakah file ada
    if not os.path.exists(CSV_PATH):
        label.configure(text="📦 Total Barang: 0")
        return

    with open(CSV_PATH, "r", encoding="utf-8") as file:
        reader = csv.reader(file)

        # Lewati header
        next(reader, None)

        for no, row in enumerate(reader, start=1):
            if len(row) >= 4 and any(c.strip() for c in row):
                tree.insert(
                    "",
                    "end",
                    values=(
                        no,
                        row[0].strip(),  # nama_barang
                        row[1].strip(),  # kategori
                        row[2].strip(),  # kode_sku
                        row[3].strip()   # status
                    )
                )
                jumlah_barang += 1

    label.configure(text=f"📦 Total Barang: {jumlah_barang}")


# ==================================
# WINDOW
# ==================================

root = ctk.CTk()
root.title("Daftar Inventaris Gudang")
root.geometry("1020x620")
center_window(root, 1020, 620)
root.configure(fg_color=BG_APP)


# ==================================
# HEADER DARI ui.py
# ==================================

buat_header(
    root,
    "DAFTAR INVENTARIS GUDANG",
    "#2563EB"
)


# ==================================
# CONTENT
# ==================================

content = ctk.CTkFrame(
    root,
    fg_color="transparent"
)

content.pack(
    fill="both",
    expand=True,
    padx=28,
    pady=16
)


# ==================================
# TABEL
# ==================================

tabel = ctk.CTkFrame(
    content,
    fg_color="transparent"
)

tabel.pack(
    fill="both",
    expand=True
)

tree = buat_treeview(tabel)


# ==================================
# FOOTER
# ==================================

footer = ctk.CTkFrame(
    content,
    fg_color="transparent"
)

footer.pack(
    fill="x",
    pady=(14, 0)
)

label_total = buat_label_total(footer)
if hasattr(tree, "set_total_label"):
    tree.set_total_label(label_total)


# ==================================
# BUTTON DARI ui.py
# ==================================

def segarkan_data():
    tampilkan_barang(tree, label_total)
    try:
        from ui import show_toast
        show_toast(root, "Data inventaris berhasil diperbarui!", "info")
    except Exception:
        pass

buat_tombol(
    footer,
    "🔄 Refresh Data",
    segarkan_data,
    "#2563EB",
    width=15,
    side="right"
)


# Tampilkan data saat program dibuka
tampilkan_barang(tree, label_total)

if __name__ == "__main__":
    root.mainloop()