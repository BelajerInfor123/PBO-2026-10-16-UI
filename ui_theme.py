"""
ui_theme.py - Konfigurasi Tema, Palet Warna, dan Utilitas UI Sistem Inventaris.
"""

import customtkinter as ctk
from customtkinter.windows.widgets.core_widget_classes.ctk_base_class import CTkBaseClass

# Pastikan backward-compatibility untuk pemanggilan .config() dan subscripting di CTk widgets
CTkBaseClass.config = lambda self, *args, **kwargs: self.configure(*args, **kwargs)
CTkBaseClass.__getitem__ = lambda self, key: self.cget(key)
CTkBaseClass.__setitem__ = lambda self, key, value: self.configure(**{key: value})

# Tangani pembatalan timer pending saat window dihancurkan agar aman di unit test
try:
    _orig_destroy = ctk.CTk.destroy
    def _safe_destroy_method(self):
        try:
            for after_id in self.tk.eval('after info').split():
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass
        except Exception:
            pass
        try:
            return _orig_destroy(self)
        except Exception:
            pass
    ctk.CTk.destroy = _safe_destroy_method
    if hasattr(ctk, "CTkToplevel"):
        _orig_toplevel_destroy = ctk.CTkToplevel.destroy
        def _safe_toplevel_destroy(self):
            try:
                for after_id in self.tk.eval('after info').split():
                    try:
                        self.after_cancel(after_id)
                    except Exception:
                        pass
            except Exception:
                pass
            try:
                return _orig_toplevel_destroy(self)
            except Exception:
                pass
        ctk.CTkToplevel.destroy = _safe_toplevel_destroy
except Exception:
    pass

# Inisialisasi tema global CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ==============================================================================
# PALET WARNA EXECUTIVE MODERN (Obsidian Slate Theme)
# ==============================================================================
BG_APP = "#0F172A"         # Slate 900 - Latar belakang utama aplikasi
BG_CARD = "#1E293B"        # Slate 800 - Permukaan kartu & formulir
BG_CARD_HOVER = "#27354A"  # Slate Card Hover
BG_INPUT = "#0B132B"       # Deep Slate Input Field
BORDER = "#334155"         # Slate 700 - Garis batas halus
BORDER_FOCUS = "#3B82F6"   # Electric Blue - Garis batas aktif/fokus

# Aksen Warna Fungsional
ACCENT_EMERALD = "#10B981" # Hijau Sukses / Tambah Barang
ACCENT_BLUE = "#3B82F6"    # Biru Modern / Navigasi & Tabel
ACCENT_ROSE = "#EF4444"    # Merah Bahaya / Hapus & Keluar
ACCENT_AMBER = "#F59E0B"   # Kuning Emas / Peringatan & Inden
ACCENT_PURPLE = "#8B5CF6"  # Ungu Stat / Metrik Kategori

# Tipografi Warna
TEXT_MAIN = "#F8FAFC"      # Slate 50 - Teks utama putih kontras
TEXT_MUTED = "#94A3B8"     # Slate 400 - Teks deskripsi & label sekunder
TEXT_SUBTLE = "#64748B"    # Slate 500 - Teks redup & placeholder

# Tipografi Skala Modern (Segoe UI Standard)
FONT_FAMILY = "Segoe UI"
FONT_MONO = "Consolas"

# Hierarki Tipografi Eksekutif
FONT_HEADER_TITLE = (FONT_FAMILY, 20, "bold")
FONT_HEADER_SUB = (FONT_FAMILY, 12)
FONT_BADGE = (FONT_FAMILY, 11, "bold")

FONT_KPI_TITLE = (FONT_FAMILY, 11, "bold")
FONT_KPI_VAL = (FONT_FAMILY, 24, "bold")
FONT_KPI_NOTE = (FONT_FAMILY, 10)

FONT_SECTION = (FONT_FAMILY, 12, "bold")

FONT_MENU_TITLE = (FONT_FAMILY, 16, "bold")
FONT_MENU_SUB = (FONT_FAMILY, 12)

FONT_FORM_TITLE = (FONT_FAMILY, 15, "bold")
FONT_FORM_SUB = (FONT_FAMILY, 12)
FONT_LABEL = (FONT_FAMILY, 12, "bold")
FONT_ENTRY = (FONT_FAMILY, 12)
FONT_BUTTON = (FONT_FAMILY, 12, "bold")

FONT_TABLE_SEARCH = (FONT_FAMILY, 12)
FONT_TABLE_HEADER = (FONT_FAMILY, 12, "bold")
FONT_TABLE_ROW = (FONT_FAMILY, 12)
FONT_TABLE_BADGE = (FONT_FAMILY, 10, "bold")
FONT_TABLE_MONO = (FONT_MONO, 11, "bold")


def center_window(window, width, height):
    """Posisikan jendela tepat di tengah layar pengguna dengan adaptasi High-DPI."""
    try:
        window.update_idletasks()
        scaling = getattr(window, "_get_window_scaling", lambda: 1.0)()
        phys_w = int(width * scaling)
        phys_h = int(height * scaling)
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = max(0, (screen_width - phys_w) // 2)
        y = max(0, (screen_height - phys_h) // 2 - 20)
        # Pastikan jendela tidak tertutup taskbar Windows
        if y + phys_h > screen_height - 40:
            y = max(0, screen_height - phys_h - 45)
        window.geometry(f"{width}x{height}+{x}+{y}")
        window.update()
    except Exception:
        window.geometry(f"{width}x{height}")


def format_rupiah(nilai):
    """Format angka menjadi string mata uang Rupiah standar."""
    try:
        val = float(nilai)
        formatted = f"{val:,.0f}".replace(",", ".")
        return f"Rp {formatted}"
    except (ValueError, TypeError):
        return "Rp 0"
