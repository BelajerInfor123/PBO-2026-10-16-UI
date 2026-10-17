"""
Main.py - Modul Utama Dashboard Sistem Inventaris Gudang Berbasis CustomTkinter.
"""

import subprocess
import sys
import os
import customtkinter as ctk

from ui import (
    buat_header,
    buat_menu_button,
    buat_dashboard_stats,
    buat_maskot_gudang,
    center_window,
    BG_APP,
    FONT_SECTION
)


def buka_tambah_barang():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "tambah_barang.py")],
        cwd=base_dir
    )


def buka_tampil_barang():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "tampil_barang.py")],
        cwd=base_dir
    )


def keluar(root):
    root.destroy()


# ==================================
# WINDOW
# ==================================

root = ctk.CTk()
root.title("Inventaris Gudang")
root.geometry("860x660")
center_window(root, 860, 660)
root.configure(fg_color=BG_APP)


# ==================================
# HEADER DARI ui.py
# ==================================

buat_header(
    root,
    "MENU INVENTARIS GUDANG"
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
    padx=32,
    pady=(8, 12)
)

# Dashboard Stats KPI Banner
stats = buat_dashboard_stats(content)

# Auto-refresh live stats saat window kembali fokus
root.bind("<FocusIn>", lambda e: stats.refresh(from_zero=True) if e.widget == root and hasattr(stats, "refresh") else None)

ctk.CTkLabel(
    content,
    text="❖  Silakan pilih modul pengurusan inventaris di bawah  ❖",
    font=FONT_SECTION,
    text_color="#CBD5E1"
).pack(
    pady=(6, 6)
)


# ==================================
# BUTTON DARI ui.py
# ==================================

buat_menu_button(
    content,
    "📦 Tambah Barang",
    buka_tambah_barang,
    "#059669"
).pack(
    fill="x",
    pady=3
)

buat_menu_button(
    content,
    "📋 Tampilkan Barang",
    buka_tampil_barang,
    "#2563EB"
).pack(
    fill="x",
    pady=3
)

buat_menu_button(
    content,
    "🚪 Keluar",
    lambda: keluar(root),
    "#DC2626"
).pack(
    fill="x",
    pady=3
)

# ==================================
# MASKOT GUDANG INTERAKTIF "BOXY"
# ==================================

buat_maskot_gudang(content).pack(
    fill="both",
    expand=True,
    pady=(6, 0)
)


if __name__ == "__main__":
    root.mainloop()