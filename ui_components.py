"""
ui_components.py - Komponen Antarmuka CustomTkinter Modern & Fleksibel.
Mencakup dashboard statistik, tabel interaktif dengan live-search, kartu navigasi,
dan form modern dengan validasi visual.
"""

import os
import sys
import csv
import math
import time
import random
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from ui_theme import (
    BG_APP, BG_CARD, BG_CARD_HOVER, BG_INPUT, BORDER, BORDER_FOCUS,
    ACCENT_EMERALD, ACCENT_BLUE, ACCENT_ROSE, ACCENT_AMBER, ACCENT_PURPLE,
    TEXT_MAIN, TEXT_MUTED, TEXT_SUBTLE, format_rupiah,
    FONT_FAMILY, FONT_MONO,
    FONT_HEADER_TITLE, FONT_HEADER_SUB, FONT_BADGE,
    FONT_KPI_TITLE, FONT_KPI_VAL, FONT_KPI_NOTE,
    FONT_MENU_TITLE, FONT_MENU_SUB,
    FONT_FORM_TITLE, FONT_FORM_SUB, FONT_LABEL, FONT_ENTRY, FONT_BUTTON,
    FONT_TABLE_SEARCH, FONT_TABLE_HEADER, FONT_TABLE_ROW, FONT_TABLE_BADGE, FONT_TABLE_MONO
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "barang.csv")


def load_ctk_image(filename, size=(32, 32)):
    """Memuat asset gambar dari folder assets/ dengan dukungan High-DPI CTkImage."""
    try:
        from PIL import Image
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "assets", filename)
        if os.path.exists(path):
            img = Image.open(path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        pass
    return None


# ==============================================================================
# ANIMATION & EVENT LOOP UTILITIES (NON-BLOCKING TIMERS)
# ==============================================================================

def safe_after(widget, delay_ms, callback):
    """
    Menjadwalkan eksekusi callback dengan aman pada widget Tkinter/CTk.
    Mencegah memory leak atau exception jika widget telah dihancurkan sebelum callback dieksekusi.
    """
    if not widget:
        return None
    try:
        if not widget.winfo_exists():
            return None
    except Exception:
        return None

    timer_box = [None]

    def _safe_wrapper():
        timer_box[0] = None
        try:
            if widget.winfo_exists():
                callback()
        except (tk.TclError, Exception):
            pass

    try:
        t_id = widget.after(delay_ms, _safe_wrapper)
        timer_box[0] = t_id
        return t_id
    except (tk.TclError, Exception):
        return None


def cancel_timer(widget, timer_id):
    """Membatalkan timer pending secara aman tanpa exception."""
    if not widget or not timer_id:
        return
    try:
        widget.after_cancel(timer_id)
    except Exception:
        pass


# ==============================================================================
# KLASIFIKASI KATEGORI & STATUS (DOMAIN UI UTILITIES)
# ==============================================================================

class KategoriBarang:
    """Daftar referensi kategori barang gudang standar."""

    ELEKTRONIK = "Elektronik"
    ALAT_TULIS = "Alat Tulis"
    PERKAKAS = "Perkakas & Teknik"
    BAHAN_BAKU = "Bahan Baku"
    KEMASAN = "Kemasan & Logistik"
    FURNITUR = "Furnitur & Kantor"
    LAIN_LAIN = "Lain-lain"

    DAFTAR = [
        ELEKTRONIK,
        ALAT_TULIS,
        PERKAKAS,
        BAHAN_BAKU,
        KEMASAN,
        FURNITUR,
        LAIN_LAIN
    ]

    PREFIX_MAP = {
        ELEKTRONIK: "ELE",
        ALAT_TULIS: "ATK",
        PERKAKAS: "TKN",
        BAHAN_BAKU: "BBK",
        KEMASAN: "KMS",
        FURNITUR: "FRN",
        LAIN_LAIN: "GUD"
    }

    WARNA_MAP = {
        ELEKTRONIK: "#38BDF8",
        ALAT_TULIS: "#F59E0B",
        PERKAKAS: "#EC4899",
        BAHAN_BAKU: "#8B5CF6",
        KEMASAN: "#10B981",
        FURNITUR: "#6366F1",
        LAIN_LAIN: "#94A3B8"
    }

    IKON_MAP = {
        ELEKTRONIK: "💻",
        ALAT_TULIS: "✏️",
        PERKAKAS: "🔧",
        BAHAN_BAKU: "📦",
        KEMASAN: "🏷️",
        FURNITUR: "🪑",
        LAIN_LAIN: "📁"
    }

    @classmethod
    def normalize_kategori(cls, kat):
        kat_clean = str(kat).strip().lower()
        for k in cls.DAFTAR:
            if k.lower() == kat_clean:
                return k
        return str(kat).strip().title() if kat else cls.LAIN_LAIN

    @classmethod
    def get_prefix(cls, kategori):
        kat_norm = cls.normalize_kategori(kategori)
        return cls.PREFIX_MAP.get(kat_norm, "GUD")

    @classmethod
    def get_warna(cls, kategori):
        kat_norm = cls.normalize_kategori(kategori)
        return cls.WARNA_MAP.get(kat_norm, "#94A3B8")

    @classmethod
    def get_ikon(cls, kategori):
        kat_norm = cls.normalize_kategori(kategori)
        return cls.IKON_MAP.get(kat_norm, "📁")


class StatusStok:
    """Konstanta status stok barang."""

    TERSEDIA = "Tersedia"
    HABIS = "Habis"
    INDEN = "Inden"

    @classmethod
    def normalize_status(cls, status):
        s = str(status).strip().lower()
        if s == "tersedia":
            return cls.TERSEDIA
        elif s == "habis":
            return cls.HABIS
        elif s == "inden":
            return cls.INDEN
        return status.strip().capitalize() if status else cls.TERSEDIA


def adjust_color_brightness(hex_color, factor=1.15):
    """Mengubah kecerahan warna HEX untuk efek hover dinamis."""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return "#3B82F6"
    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return f"#{hex_color}"


# ==============================================================================
# HEADER MODERN
# ==============================================================================
def create_modern_header(parent, title, subtitle_or_color="", warna_badge=None):
    """
    Membuat header banner modern dengan aksen warna atas, tipografi bold,
    serta indikator status sistem.
    Mendukung pemanggilan fleksibel 2 atau 3 argumen.
    """
    if str(subtitle_or_color).startswith("#"):
        chosen_accent = subtitle_or_color
        subtitle = ""
    else:
        subtitle = str(subtitle_or_color) if subtitle_or_color else ""
        chosen_accent = warna_badge

    title_upper = title.upper()
    if not chosen_accent:
        if "TAMBAH" in title_upper:
            chosen_accent = ACCENT_EMERALD
        elif "DAFTAR" in title_upper or "TAMPIL" in title_upper:
            chosen_accent = ACCENT_BLUE
        else:
            chosen_accent = "#3B82F6"

    if not subtitle:
        if "TAMBAH" in title_upper:
            subtitle = "Entri data item baru ke dalam basis data gudang"
        elif "DAFTAR" in title_upper or "TAMPIL" in title_upper:
            subtitle = "Katalog dan status inventaris barang gudang secara terperinci"
        elif "MENU" in title_upper:
            subtitle = "Sistem Manajemen Stok & Pergudangan Digital"
        else:
            subtitle = "Sistem Manajemen Inventaris & Logistik Gudang"

    header_frame = ctk.CTkFrame(
        parent,
        fg_color=BG_CARD,
        corner_radius=0,
        height=82
    )
    header_frame.pack(fill="x", side="top")

    # Garis aksen tipis di puncak header
    accent_bar = ctk.CTkFrame(
        header_frame,
        fg_color=chosen_accent,
        height=3,
        corner_radius=0
    )
    accent_bar.pack(fill="x", side="top")

    content_box = ctk.CTkFrame(header_frame, fg_color="transparent")
    content_box.pack(fill="both", expand=True, padx=32, pady=10)

    # Ikon Badge Kiri
    icon_char = "📦"
    if "TAMBAH" in title_upper:
        icon_char = "✨"
    elif "DAFTAR" in title_upper or "TAMPIL" in title_upper:
        icon_char = "📋"
    elif "MENU" in title_upper:
        icon_char = "🏢"

    icon_badge = ctk.CTkFrame(
        content_box,
        fg_color=BG_APP,
        corner_radius=10,
        border_width=1,
        border_color=BORDER,
        width=44,
        height=44
    )
    icon_badge.pack(side="left", padx=(0, 14))
    icon_badge.pack_propagate(False)

    lbl_icon = None
    try:
        logo_img = load_ctk_image("logo.png", size=(28, 28))
        if logo_img:
            lbl_icon = ctk.CTkLabel(icon_badge, image=logo_img, text="")
    except Exception:
        lbl_icon = None

    if lbl_icon is None:
        lbl_icon = ctk.CTkLabel(
            icon_badge,
            text=icon_char,
            font=("Segoe UI", 18)
        )
    lbl_icon.place(relx=0.5, rely=0.5, anchor="center")

    # Judul & Subjudul
    text_container = ctk.CTkFrame(content_box, fg_color="transparent")
    text_container.pack(side="left", fill="y")

    lbl_title = ctk.CTkLabel(
        text_container,
        text=title,
        font=FONT_HEADER_TITLE,
        text_color=TEXT_MAIN,
        anchor="w"
    )
    lbl_title.pack(anchor="w")

    lbl_sub = ctk.CTkLabel(
        text_container,
        text=subtitle,
        font=FONT_HEADER_SUB,
        text_color=TEXT_MUTED,
        anchor="w"
    )
    lbl_sub.pack(anchor="w", pady=(2, 0))

    # Badge Kanan (Status Sistem Realtime)
    right_badge = ctk.CTkFrame(
        content_box,
        fg_color=BG_APP,
        corner_radius=8,
        border_width=1,
        border_color="#134E4A"
    )
    right_badge.pack(side="right", pady=4)

    lbl_status = ctk.CTkLabel(
        right_badge,
        text="🟢 SISTEM AKTIF",
        font=FONT_BADGE,
        text_color=ACCENT_EMERALD
    )
    lbl_status.pack(padx=12, pady=5)

    # Animasi Pulsing / Breathing "Sistem Aktif" Status Badge
    pulse_frames = [
        ("#10B981", "#134E4A"),
        ("#18BF86", "#145953"),
        ("#22C78C", "#17655F"),
        ("#2DCE93", "#1A726B"),
        ("#34D399", "#1E8078"),  # Peak neon emerald
        ("#2DCE93", "#1A726B"),
        ("#22C78C", "#17655F"),
        ("#18BF86", "#145953"),
    ]
    lbl_status._pulse_timer = None

    def _pulse_step(step_idx=0):
        if not lbl_status.winfo_exists() or not right_badge.winfo_exists():
            return
        txt_color, border_color = pulse_frames[step_idx % len(pulse_frames)]
        try:
            lbl_status.configure(text_color=txt_color)
            right_badge.configure(border_color=border_color)
        except Exception:
            return
        next_idx = (step_idx + 1) % len(pulse_frames)
        lbl_status._pulse_timer = safe_after(lbl_status, 140, lambda: _pulse_step(next_idx))

    _pulse_step(0)

    def _cancel_pulse(e=None):
        if e is not None:
            w = getattr(e, "widget", None)
            valid = (
                header_frame, getattr(header_frame, "_canvas", None),
                right_badge, getattr(right_badge, "_canvas", None),
                lbl_status, getattr(lbl_status, "_canvas", None)
            )
            if w not in valid and not any(str(w) == str(t) for t in (header_frame, right_badge, lbl_status)):
                return
        cancel_timer(lbl_status, getattr(lbl_status, "_pulse_timer", None))
        lbl_status._pulse_timer = None

    header_frame.bind("<Destroy>", _cancel_pulse, add="+")
    right_badge.bind("<Destroy>", _cancel_pulse, add="+")
    lbl_status.bind("<Destroy>", _cancel_pulse, add="+")

    return header_frame


# ==============================================================================
# DASHBOARD STATS ROW (KARTU KPI METRIK GUDANG)
# ==============================================================================
def create_dashboard_stats(parent):
    """
    Menampilkan ringkasan metrik inventaris (KPI Dashboard Cards)
    yang membaca langsung dari data barang.csv dengan fungsi auto-refresh.
    """
    stats_container = ctk.CTkFrame(parent, fg_color="transparent")
    stats_container.pack(fill="x", pady=(0, 10))

    val_labels = {}

    def _read_data():
        csv_file = globals().get("CSV_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "barang.csv"))

        total_items = 0
        tersedia_count = 0

        if os.path.exists(csv_file):
            try:
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Lewati header
                    for row in reader:
                        if len(row) >= 4 and any(c.strip() for c in row):
                            total_items += 1
                            if row[3].strip().lower() == "tersedia":
                                tersedia_count += 1
            except Exception:
                pass
        return total_items, tersedia_count

    def _animate_counter(label, target_val, suffix="", from_zero=False):
        if not label:
            return
        try:
            if not label.winfo_exists():
                return
        except Exception:
            return

        old_timer = getattr(label, "_counter_timer", None)
        if old_timer:
            cancel_timer(label, old_timer)
            label._counter_timer = None

        if from_zero:
            start_val = 0
        else:
            start_val = getattr(label, "_current_numeric_val", 0)
        label._target_numeric_val = target_val

        if target_val == 0:
            label._current_numeric_val = 0
            try:
                label.configure(text=f"0 {suffix}".strip())
            except Exception:
                pass
            return

        if start_val == target_val and not from_zero:
            label._current_numeric_val = target_val
            try:
                label.configure(text=f"{target_val} {suffix}".strip())
            except Exception:
                pass
            return

        duration_ms = 350
        steps = 14
        step_ms = max(15, duration_ms // steps)
        state = [0]

        def _step():
            if not label.winfo_exists():
                return
            state[0] += 1
            progress = min(1.0, state[0] / steps)
            ease = 1.0 - (1.0 - progress) * (1.0 - progress)
            curr = int(round(start_val + (target_val - start_val) * ease))
            label._current_numeric_val = curr

            try:
                label.configure(text=f"{curr} {suffix}".strip())
            except Exception:
                return

            if progress < 1.0:
                label._counter_timer = safe_after(label, step_ms, _step)
            else:
                label._counter_timer = None
                label._current_numeric_val = target_val
                try:
                    label.configure(text=f"{target_val} {suffix}".strip())
                except Exception:
                    pass

        _step()

    def refresh(from_zero=True):
        total_items, tersedia_count = _read_data()
        if "total" in val_labels:
            _animate_counter(val_labels["total"], total_items, "SKU", from_zero=from_zero)
        if "tersedia" in val_labels:
            _animate_counter(val_labels["tersedia"], tersedia_count, "Siap", from_zero=from_zero)

    stats_container.refresh = refresh

    def _cancel_all_counters(e=None):
        if e is not None:
            w = getattr(e, "widget", None)
            if w not in (stats_container, getattr(stats_container, "_canvas", None)) and str(w) != str(stats_container):
                return
        for lbl in val_labels.values():
            cancel_timer(lbl, getattr(lbl, "_counter_timer", None))
            lbl._counter_timer = None

    stats_container.bind("<Destroy>", _cancel_all_counters, add="+")

    total_items, tersedia_count = _read_data()
    cards_data = [
        ("total", "📦", "TOTAL BARANG", "0 SKU", "Katalog Terdaftar", ACCENT_BLUE, total_items, "SKU"),
        ("tersedia", "✅", "STOK TERSEDIA", "0 Siap", "Stok Siap Distribusi", ACCENT_EMERALD, tersedia_count, "Siap"),
        ("status", "⚡", "DATABASE CSV", "Sinkron", "Auto-Save Otomatis", ACCENT_AMBER, None, "")
    ]

    for i, (key, icon, title, val, note, accent, num_val, suffix) in enumerate(cards_data):
        card = ctk.CTkFrame(
            stats_container,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            height=102
        )
        card.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 10, 0))

        # Top accent
        accent_strip = ctk.CTkFrame(card, fg_color=accent, height=3, corner_radius=0)
        accent_strip.pack(fill="x", side="top")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=10)

        top_row = ctk.CTkFrame(body, fg_color="transparent")
        top_row.pack(fill="x")

        lbl_top = ctk.CTkLabel(
            top_row,
            text=f"{icon}  {title}",
            font=FONT_KPI_TITLE,
            text_color=TEXT_MUTED
        )
        lbl_top.pack(side="left")

        lbl_val = ctk.CTkLabel(
            body,
            text=val,
            font=FONT_KPI_VAL,
            text_color=TEXT_MAIN,
            anchor="w"
        )
        lbl_val.pack(fill="x", pady=(4, 2))
        val_labels[key] = lbl_val

        if num_val is not None:
            lbl_val._current_numeric_val = 0
            lbl_val._counter_timer = None
            lbl_val.bind("<Destroy>", lambda e, l=lbl_val: cancel_timer(l, getattr(l, "_counter_timer", None)), add="+")
            _animate_counter(lbl_val, num_val, suffix, from_zero=True)

        lbl_subnote = ctk.CTkLabel(
            body,
            text=note,
            font=FONT_KPI_NOTE,
            text_color=TEXT_SUBTLE,
            anchor="w"
        )
        lbl_subnote.pack(fill="x")

        # Card hover effect (glow border & card hover bg on enter, restore on leave)
        # Note: Click handler removed to disable clicking and repeated count-up refresh
        def _bind_card_events(c, acc, sub_widgets):
            def _is_inside():
                try:
                    x, y = c.winfo_pointerxy()
                    rx = c.winfo_rootx()
                    ry = c.winfo_rooty()
                    rw = c.winfo_width()
                    rh = c.winfo_height()
                    return (rx <= x < rx + rw) and (ry <= y < ry + rh)
                except Exception:
                    return False

            def _c_enter(e=None):
                c.configure(border_color=acc, fg_color=BG_CARD_HOVER)

            def _c_leave(e=None):
                if e is not None and _is_inside():
                    return
                c.configure(border_color=BORDER, fg_color=BG_CARD)

            for w in [c, accent_strip] + sub_widgets:
                w.bind("<Enter>", _c_enter)
                w.bind("<Leave>", _c_leave)
            c._on_enter = lambda: _c_enter(None)
            c._on_leave = lambda: _c_leave(None)

        _bind_card_events(card, accent, [body, top_row, lbl_top, lbl_val, lbl_subnote])

    return stats_container


# ==============================================================================
# MENU BUTTON CARD (KARTU MENU UTAMA DASHBOARD)
# ==============================================================================
def create_menu_card(parent, text, subtitle_or_cmd=None, command=None, bg_color="#059669", hover_color=None):
    """
    Membuat kartu navigasi interaktif untuk Main.py dengan animasi hover,
    garis aksen, dan deskripsi modul.
    Mendukung pemanggilan 4-argumen gaya GitHub (parent, text, cmd, color)
    maupun 5-argumen lengkap (parent, text, subtitle, cmd, color).
    """
    if callable(subtitle_or_cmd):
        cmd = subtitle_or_cmd
        sub = ""
        accent = command or bg_color
    else:
        sub = str(subtitle_or_cmd) if subtitle_or_cmd else ""
        cmd = command
        accent = bg_color

    # Inferensi otomatis deskripsi dan aksen bila tidak disediakan eksplisit
    if not sub:
        if "Tambah" in text:
            sub = "Entri barang baru ke dalam basis data gudang dengan validasi otomatis"
            if accent in ("#059669", "#34495E") or not accent:
                accent = ACCENT_EMERALD
        elif "Tampil" in text:
            sub = "Katalog interaktif, pencarian cepat, filter kategori, dan status stok"
            if accent in ("#059669", "#2C3E50") or not accent:
                accent = ACCENT_BLUE
        elif "Keluar" in text:
            sub = "Tutup sesi aplikasi inventaris gudang dan simpan seluruh data"
            if accent in ("#059669", "#7F8C8D") or not accent:
                accent = ACCENT_ROSE

    card = ctk.CTkFrame(
        parent,
        fg_color=BG_CARD,
        corner_radius=12,
        border_width=1,
        border_color=BORDER,
        cursor="hand2"
    )

    # Garis aksen kiri (tinggi fleksibel mengikuti isi kartu tanpa memaksa 200px)
    left_strip = ctk.CTkFrame(
        card,
        fg_color=accent,
        width=6,
        height=1,
        corner_radius=3
    )
    left_strip.pack(side="left", fill="y", padx=(0, 14))

    # Icon visual di samping kiri teks
    icon_asset = None
    if "Tambah" in text:
        icon_asset = load_ctk_image("icon_add.png", size=(28, 28))
    elif "Tampil" in text:
        icon_asset = load_ctk_image("icon_table.png", size=(28, 28))
    elif "Keluar" in text:
        icon_asset = load_ctk_image("icon_exit.png", size=(28, 28))

    icon_box = ctk.CTkFrame(
        card,
        fg_color=BG_APP,
        corner_radius=10,
        border_width=1,
        border_color=BORDER,
        width=40,
        height=40
    )
    icon_box.pack_propagate(False)
    icon_box.pack(side="left", padx=(0, 14), pady=10)

    lbl_img = None
    if icon_asset:
        try:
            lbl_img = ctk.CTkLabel(icon_box, image=icon_asset, text="")
            lbl_img.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            lbl_img = None

    if lbl_img is None:
        icon_char = "📦"
        if "Tambah" in text:
            icon_char = "✨"
        elif "Tampil" in text:
            icon_char = "📋"
        elif "Keluar" in text:
            icon_char = "🚪"
        lbl_img = ctk.CTkLabel(
            icon_box,
            text=icon_char,
            font=("Segoe UI", 18)
        )
        lbl_img.place(relx=0.5, rely=0.5, anchor="center")

    # Arrow kanan (pack dengan side="right" SEBELUM center frame agar menempel di kanan)
    arrow_frame = ctk.CTkFrame(
        card,
        fg_color=BG_APP,
        corner_radius=8,
        border_width=1,
        border_color=BORDER,
        width=34,
        height=34
    )
    arrow_frame.pack_propagate(False)
    arrow_frame.pack(side="right", padx=16, pady=10)

    arrow_lbl = ctk.CTkLabel(
        arrow_frame,
        text="➔",
        font=("Segoe UI", 12, "bold"),
        text_color=accent
    )
    arrow_lbl.place(relx=0.5, rely=0.5, anchor="center", x=0)
    arrow_lbl._current_x = 0
    arrow_lbl._slide_timer = None

    card._press_timer = None

    def animate_arrow(target_x):
        if not arrow_lbl.winfo_exists():
            return
        if getattr(arrow_lbl, "_slide_timer", None):
            cancel_timer(arrow_lbl, arrow_lbl._slide_timer)
            arrow_lbl._slide_timer = None

        def _slide_step():
            if not arrow_lbl.winfo_exists():
                return
            cur = getattr(arrow_lbl, "_current_x", 0)
            if cur < target_x:
                next_x = min(target_x, cur + 1)
            elif cur > target_x:
                next_x = max(target_x, cur - 1)
            else:
                arrow_lbl._slide_timer = None
                return

            arrow_lbl._current_x = next_x
            try:
                arrow_lbl.place_configure(x=next_x)
            except Exception:
                return

            if next_x != target_x:
                arrow_lbl._slide_timer = safe_after(arrow_lbl, 18, _slide_step)
            else:
                arrow_lbl._slide_timer = None

        _slide_step()

    def _cancel_card_timers(e=None):
        if e is not None:
            w = getattr(e, "widget", None)
            valid = (
                card, getattr(card, "_canvas", None),
                arrow_frame, getattr(arrow_frame, "_canvas", None),
                arrow_lbl, getattr(arrow_lbl, "_canvas", None)
            )
            if w not in valid and not any(str(w) == str(t) for t in (card, arrow_frame, arrow_lbl)):
                return
        cancel_timer(arrow_lbl, getattr(arrow_lbl, "_slide_timer", None))
        arrow_lbl._slide_timer = None
        cancel_timer(card, getattr(card, "_press_timer", None))
        card._press_timer = None

    card.bind("<Destroy>", _cancel_card_timers, add="+")
    arrow_lbl.bind("<Destroy>", _cancel_card_timers, add="+")
    arrow_frame.bind("<Destroy>", _cancel_card_timers, add="+")

    # Kontainer teks di tengah (vertically centered)
    center = ctk.CTkFrame(card, fg_color="transparent")
    center.pack(side="left", fill="x", expand=True, pady=8)

    lbl_title = ctk.CTkLabel(
        center,
        text=text,
        font=FONT_MENU_TITLE,
        text_color=TEXT_MAIN,
        anchor="w"
    )
    lbl_title.pack(fill="x")

    lbl_sub = None
    if sub:
        lbl_sub = ctk.CTkLabel(
            center,
            text=sub,
            font=FONT_MENU_SUB,
            text_color=TEXT_MUTED,
            anchor="w"
        )
        lbl_sub.pack(fill="x", pady=(2, 0))

    def _is_pointer_inside():
        try:
            x, y = card.winfo_pointerxy()
            rx = card.winfo_rootx()
            ry = card.winfo_rooty()
            rw = card.winfo_width()
            rh = card.winfo_height()
            return (rx <= x < rx + rw) and (ry <= y < ry + rh)
        except Exception:
            return False

    def on_enter(e=None):
        card.is_hover = True
        card.configure(fg_color=BG_CARD_HOVER, border_color=accent)
        arrow_frame.configure(border_color=accent, fg_color=accent)
        arrow_lbl.configure(text_color="#FFFFFF")
        icon_box.configure(border_color=accent)
        animate_arrow(5)

    def on_leave(e=None):
        if e is not None and _is_pointer_inside():
            return
        card.is_hover = False
        card.configure(fg_color=BG_CARD, border_color=BORDER)
        arrow_frame.configure(border_color=BORDER, fg_color=BG_APP)
        arrow_lbl.configure(text_color=accent)
        icon_box.configure(border_color=BORDER)
        animate_arrow(0)

    def on_press(e=None):
        card._is_pressed = True
        card.configure(fg_color="#182335")
        try:
            arrow_lbl.place_configure(x=7)
        except Exception:
            pass

    def on_release(e=None):
        card._is_pressed = False
        cancel_timer(card, getattr(card, "_press_timer", None))
        card._press_timer = None
        if getattr(card, "is_hover", False):
            card.configure(fg_color=BG_CARD_HOVER, border_color=accent)
            animate_arrow(5)
        else:
            card.configure(fg_color=BG_CARD, border_color=BORDER)
            animate_arrow(0)

    def on_click(e=None):
        on_press(e)
        cancel_timer(card, getattr(card, "_press_timer", None))
        card._press_timer = safe_after(card, 90, lambda: on_release(None))
        if cmd:
            cmd()

    widgets_to_bind = [card, center, lbl_title, arrow_frame, arrow_lbl, left_strip, icon_box, lbl_img]
    if lbl_sub:
        widgets_to_bind.append(lbl_sub)

    for w in widgets_to_bind:
        if w is not None:
            w.bind("<Button-1>", on_click)
            w.bind("<ButtonRelease-1>", on_release)
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    card.is_hover = False
    card._on_enter = lambda: on_enter(None)
    card._on_leave = lambda: on_leave(None)
    card._on_click = lambda: on_click(None)

    return card


# ==============================================================================
# MASKOT GUDANG INTERAKTIF "BOXY"
# ==============================================================================
def create_warehouse_mascot(parent):
    """
    Membuat widget maskot gudang interaktif "Boxy" - karakter kardus imut bertema logistik
    dengan helm proyek keselamatan kuning, pipi merona, dan sepatu bot pekerja.
    Fitur utama:
    - Karakter Lucu & Menggemaskan:
      * Desain kardus paket logistik dengan detail lipatan, pita perekat, dan stempel hati/fragile.
      * Helm keselamatan kuning berpelindung dengan stiker lencana bintang keselamatan dan kilau reflektif.
      * Mata anime chibi bersinar dengan catchlight ganda yang dapat berkedip dan melirik kursor.
      * Pipi merona merah muda (rosy blushing cheeks) dan senyum ceria.
      * Sepatu bot pekerja dengan animasi langkah melangkah dinamis (bouncy steps).
    - Berbagai Pose Dinamis:
      * Idle Breathing: Bernapas lembut turun-naik dengan kedipan mata periodik.
      * Walking / Patrol: Berpatroli menyusuri lantai gudang dengan langkah kaki bergantian dan ayunan tangan.
      * Waving / Menyapa: Melambaikan tangan saat kursor berada di dekatnya atau saat disapa.
      * Carrying Mini Box: Membawa paket mini lucu di tangannya saat mengantar barang.
      * Happy Jump: Melompat tinggi gembira saat diklik dengan partikel cinta & bintang bertaburan.
      * Sleeping (zZz): Tertidur lelap dengan mata terpejam dan gelembung huruf zZz saat dibiarkan menganggur.
    - Interaktivitas Maksimal:
      * Klik pada Boxy: Memicu lompatan ceria, semburan partikel hati/bintang, dan balon percakapan
        berisi pesan logistik ceria (e.g., 'Stok aman, Bos! ✨', 'Semangat kerjanya! 📦', dll).
      * Klik di lantai kanvas: Memanggil Boxy berjalan ke posisi koordinat X yang diklik dengan indikator ripple lantai.
      * Hover mouse: Kursor berubah menjadi hand2 saat menyentuh Boxy, Boxy melirik dan merespons.
      * Tombol Aksi Cepat: '👋 Sapa', '📦 Paket', '💤 Tidur' di bilah atas untuk interaksi langsung.
    - Bersih & Aman Memori:
      * Timer non-blocking widget.after() dibatalkan otomatis saat event <Destroy> tanpa kebocoran memori.
    """
    ornament = ctk.CTkFrame(
        parent,
        fg_color=BG_CARD,
        corner_radius=12,
        border_width=1,
        border_color=BORDER,
        height=138
    )

    # Hover glow border pada kontainer
    def _on_orn_enter(e=None):
        try:
            ornament.configure(border_color="#F59E0B")
        except Exception:
            pass

    def _on_orn_leave(e=None):
        try:
            ornament.configure(border_color=BORDER)
        except Exception:
            pass

    ornament.bind("<Enter>", _on_orn_enter, add="+")
    ornament.bind("<Leave>", _on_orn_leave, add="+")

    # --------------------------------------------------------------------------
    # TOP STATUS STRIP
    # --------------------------------------------------------------------------
    top_strip = ctk.CTkFrame(ornament, fg_color="transparent", height=28)
    top_strip.pack(fill="x", side="top", padx=14, pady=(6, 2))

    left_box = ctk.CTkFrame(top_strip, fg_color="transparent")
    left_box.pack(side="left")

    lbl_avatar = ctk.CTkLabel(
        left_box,
        text="📦",
        font=("Segoe UI Emoji", 14),
        width=20
    )
    lbl_avatar.pack(side="left", padx=(0, 4))

    lbl_name = ctk.CTkLabel(
        left_box,
        text="BOXY — MASKOT GUDANG CILIK",
        font=FONT_KPI_TITLE,
        text_color=TEXT_MAIN
    )
    lbl_name.pack(side="left", padx=(0, 8))

    badge_status = ctk.CTkLabel(
        left_box,
        text="● Siaga",
        font=("Segoe UI", 9, "bold"),
        text_color=ACCENT_EMERALD,
        fg_color="#064E3B",
        corner_radius=6,
        padx=7,
        pady=1
    )
    badge_status.pack(side="left")

    right_box = ctk.CTkFrame(top_strip, fg_color="transparent")
    right_box.pack(side="right")

    btn_sapa = ctk.CTkButton(
        right_box,
        text="👋 Sapa",
        width=64,
        height=22,
        font=("Segoe UI", 10, "bold"),
        fg_color="#1E293B",
        hover_color="#334155",
        text_color="#F8FAFC",
        corner_radius=6
    )
    btn_sapa.pack(side="left", padx=3)

    btn_paket = ctk.CTkButton(
        right_box,
        text="📦 Paket",
        width=68,
        height=22,
        font=("Segoe UI", 10, "bold"),
        fg_color="#1E293B",
        hover_color="#334155",
        text_color="#F8FAFC",
        corner_radius=6
    )
    btn_paket.pack(side="left", padx=3)

    btn_tidur = ctk.CTkButton(
        right_box,
        text="💤 Tidur",
        width=64,
        height=22,
        font=("Segoe UI", 10, "bold"),
        fg_color="#1E293B",
        hover_color="#334155",
        text_color="#F8FAFC",
        corner_radius=6
    )
    btn_tidur.pack(side="left", padx=3)

    # --------------------------------------------------------------------------
    # BOTTOM STATUS STRIP (Packed with side='bottom' before canvas_box to avoid collapse)
    # --------------------------------------------------------------------------
    bot_strip = ctk.CTkFrame(ornament, fg_color="transparent", height=20)
    bot_strip.pack(fill="x", side="bottom", padx=14, pady=(2, 6))

    lbl_hint = ctk.CTkLabel(
        bot_strip,
        text="💡 Klik Boxy untuk interaksi ceria, atau klik di lantai untuk memanggilnya ke sana!",
        font=("Segoe UI", 9),
        text_color=TEXT_MUTED
    )
    lbl_hint.pack(side="left")

    lbl_loc = ctk.CTkLabel(
        bot_strip,
        text="📍 Gudang Sektor A",
        font=("Consolas", 9),
        text_color=TEXT_SUBTLE
    )
    lbl_loc.pack(side="right")

    # --------------------------------------------------------------------------
    # CANVAS WAREHOUSE ENVIRONMENT
    # --------------------------------------------------------------------------
    canvas_box = ctk.CTkFrame(
        ornament,
        fg_color="#080E1A",
        corner_radius=8,
        border_width=1,
        border_color="#1E293B"
    )
    canvas_box.pack(fill="both", expand=True, padx=12, pady=2)

    canvas = tk.Canvas(
        canvas_box,
        bg="#080E1A",
        highlightthickness=0,
        bd=0,
        cursor="arrow"
    )
    canvas.pack(fill="both", expand=True, padx=2, pady=2)

    # 1. Background elements
    bg_floor_rect = canvas.create_rectangle(0, 0, 0, 0, fill="#0F172A", outline="")
    bg_floor_line = canvas.create_line(0, 0, 0, 0, fill="#1E293B", width=2)
    bg_planks = [canvas.create_line(0, 0, 0, 0, fill="#162236", dash=(2, 4)) for _ in range(16)]
    bg_shelf = [
        canvas.create_rectangle(0, 0, 0, 0, fill="#152136", outline="#22324D"),
        canvas.create_rectangle(0, 0, 0, 0, fill="#18253D", outline="#22324D")
    ]
    bg_lamp_lines = [
        canvas.create_line(0, 0, 0, 0, fill="#334155"),
        canvas.create_line(0, 0, 0, 0, fill="#334155")
    ]
    bg_lamp_bulbs = [
        canvas.create_oval(0, 0, 0, 0, fill="#F59E0B", outline=""),
        canvas.create_oval(0, 0, 0, 0, fill="#F59E0B", outline="")
    ]
    bg_label = canvas.create_text(0, 0, text="SEKTOR LOGISTIK A-1", font=("Consolas", 8, "bold"), fill="#182338", anchor="e")

    # 2. Floor destination marker
    dest_marker = canvas.create_oval(0, 0, 0, 0, outline="#F59E0B", width=2, state="hidden")
    dest_pin = canvas.create_text(0, 0, text="📍", font=("Segoe UI Emoji", 10), state="hidden")

    # 3. Boxy: Shadow
    shadow_id = canvas.create_oval(0, 0, 0, 0, fill="#04070F", outline="")

    # 4. Boxy: Boots / Legs
    boot_l_id = canvas.create_oval(0, 0, 0, 0, fill="#334155", outline="#1E293B")
    boot_l_sole = canvas.create_line(0, 0, 0, 0, fill="#0F172A", width=2)
    boot_r_id = canvas.create_oval(0, 0, 0, 0, fill="#334155", outline="#1E293B")
    boot_r_sole = canvas.create_line(0, 0, 0, 0, fill="#0F172A", width=2)

    # 5. Boxy: Body & Box Details
    body_id = canvas.create_polygon([0] * 16, fill="#E2A066", outline="#B46E3A", width=1.5)
    tape_id = canvas.create_rectangle(0, 0, 0, 0, fill="#CCA076", outline="")
    crease_top = canvas.create_line(0, 0, 0, 0, fill="#C78D5B", width=1)
    crease_vert = canvas.create_line(0, 0, 0, 0, fill="#B46E3A", width=1)
    stamp_id = canvas.create_text(0, 0, text="❤️", font=("Segoe UI Emoji", 7), fill="#E11D48")

    # 6. Boxy: Arms / Hands
    arm_l_id = canvas.create_line(0, 0, 0, 0, fill="#B46E3A", width=3, capstyle="round")
    hand_l_id = canvas.create_oval(0, 0, 0, 0, fill="#F59E0B", outline="#D97706")
    arm_r_id = canvas.create_line(0, 0, 0, 0, fill="#B46E3A", width=3, capstyle="round")
    hand_r_id = canvas.create_oval(0, 0, 0, 0, fill="#F59E0B", outline="#D97706")

    # 7. Boxy: Mini Package (Carry mode)
    carry_box = canvas.create_rectangle(0, 0, 0, 0, fill="#D97706", outline="#92400E", width=1, state="hidden")
    carry_tape = canvas.create_line(0, 0, 0, 0, fill="#EF4444", width=1.5, state="hidden")
    carry_ribbon = canvas.create_line(0, 0, 0, 0, fill="#EF4444", width=1.5, state="hidden")

    # 8. Boxy: Safety Hardhat
    hardhat_dome = canvas.create_arc(0, 0, 0, 0, start=0, extent=180, fill="#FBBF24", outline="#D97706", width=1.5, style="chord")
    hardhat_brim = canvas.create_line(0, 0, 0, 0, fill="#F59E0B", width=4, capstyle="round")
    hardhat_shine = canvas.create_arc(0, 0, 0, 0, start=45, extent=90, style="arc", outline="#FEF08A", width=2)
    hardhat_badge = canvas.create_text(0, 0, text="⭐", font=("Segoe UI Emoji", 7), fill="#FFFFFF")

    # 9. Boxy: Face Elements
    # Eyes normal
    eye_l_oval = canvas.create_oval(0, 0, 0, 0, fill="#0F172A", outline="#020617")
    eye_l_hl1 = canvas.create_oval(0, 0, 0, 0, fill="#FFFFFF", outline="")
    eye_l_hl2 = canvas.create_oval(0, 0, 0, 0, fill="#FFFFFF", outline="")
    eye_r_oval = canvas.create_oval(0, 0, 0, 0, fill="#0F172A", outline="#020617")
    eye_r_hl1 = canvas.create_oval(0, 0, 0, 0, fill="#FFFFFF", outline="")
    eye_r_hl2 = canvas.create_oval(0, 0, 0, 0, fill="#FFFFFF", outline="")
    # Eyes closed / sleeping / blinking
    eye_l_arc = canvas.create_arc(0, 0, 0, 0, start=0, extent=180, style="arc", outline="#0F172A", width=2, state="hidden")
    eye_r_arc = canvas.create_arc(0, 0, 0, 0, start=0, extent=180, style="arc", outline="#0F172A", width=2, state="hidden")
    # Cheeks
    cheek_l = canvas.create_oval(0, 0, 0, 0, fill="#FB7185", outline="")
    cheek_r = canvas.create_oval(0, 0, 0, 0, fill="#FB7185", outline="")
    # Mouth
    mouth_smile = canvas.create_arc(0, 0, 0, 0, start=180, extent=180, style="arc", outline="#78350F", width=1.5)
    mouth_open = canvas.create_oval(0, 0, 0, 0, fill="#BE123C", outline="#881337", state="hidden")

    # 10. Speech Bubble
    bubble_bg = canvas.create_polygon([0] * 14, fill="#1E293B", outline="#38BDF8", width=1.5, state="hidden")
    bubble_txt = canvas.create_text(0, 0, text="", font=("Segoe UI", 9, "bold"), fill="#F8FAFC", state="hidden")

    # State variables
    mascot_state = {
        "x": 380.0,
        "y": 60.0,
        "by1": 20.0,
        "current": "idle",       # "idle", "walk", "jump", "carry", "sleep", "wave"
        "prev_state": "idle",
        "facing": 1,             # 1 for right, -1 for left
        "target_x": 380.0,
        "walk_phase": 0.0,
        "jump_y": 0.0,
        "jump_vel": 0.0,
        "carrying": False,
        "waving_ticks": 0,
        "idle_ticks": 0,
        "user_inactivity_ticks": 0,
        "startled_ticks": 0,
        "blink_counter": 0,
        "is_blinking": False,
        "speed": 2.6
    }

    mouse_state = {
        "x": -100.0,
        "y": -100.0,
        "active": False,
        "hover_boxy": False
    }

    floor_marker_state = {
        "active": False,
        "x": 380.0,
        "r": 2.0
    }

    speech_state = {
        "active": False,
        "text": "",
        "timer": None,
        "ticks_left": 0
    }

    active_particles = []
    anim_state = {"tick": 0, "timer": None, "destroyed": False}

    SPEECH_QUOTES = [
        "Stok aman, Bos! ✨",
        "Semangat kerjanya! 📦",
        "Aduh geli hihi! 😄",
        "Siap kirim paket! 🚚",
        "Gudang rapi, hati senang! 🌟",
        "Boxy selalu siap sedia! 🫡",
        "Semua barang tercatat rapi! 📋",
        "Paket masuk siap diinput! 🏷️",
        "Hai! Selamat datang di gudang! 👋",
        "Semua sistem logistik optimal! 🚀"
    ]

    def _clear_floor_marker():
        floor_marker_state["active"] = False
        try:
            canvas.itemconfig(dest_marker, state="hidden")
            canvas.itemconfig(dest_pin, state="hidden")
        except Exception:
            pass

    def _update_status_badge(custom_text=None):
        if anim_state["destroyed"] or not ornament.winfo_exists():
            return
        if custom_text:
            badge_status.configure(text=custom_text, fg_color="#831843", text_color="#F472B6")
            return
        st = mascot_state["current"]
        if mascot_state["carrying"]:
            badge_status.configure(text="📦 Kirim Paket", fg_color="#451A03", text_color="#FBBF24")
        elif st == "idle":
            badge_status.configure(text="● Siaga", fg_color="#064E3B", text_color="#34D399")
        elif st == "walk":
            badge_status.configure(text="🚶 Patroli", fg_color="#1E3A8A", text_color="#60A5FA")
        elif st == "jump":
            badge_status.configure(text="✨ Ceria!", fg_color="#831843", text_color="#F472B6")
        elif st == "wave":
            badge_status.configure(text="👋 Menyapa", fg_color="#14532D", text_color="#4ADE80")
        elif st == "sleep":
            badge_status.configure(text="💤 Istirahat", fg_color="#3B0764", text_color="#C084FC")

    def _show_speech(text):
        speech_state["active"] = True
        speech_state["text"] = text
        speech_state["ticks_left"] = 75  # ~2.5 seconds
        canvas.itemconfig(bubble_bg, state="normal")
        canvas.itemconfig(bubble_txt, text=text, state="normal")

    def _hide_speech():
        speech_state["active"] = False
        canvas.itemconfig(bubble_bg, state="hidden")
        canvas.itemconfig(bubble_txt, state="hidden")

    def _spawn_burst(ox, oy):
        symbols = [("❤️", "#F43F5E"), ("✨", "#FBBF24"), ("⭐", "#F59E0B"), ("💖", "#EC4899"), ("📦", "#E0A96D")]
        for _ in range(7):
            sym, col = random.choice(symbols)
            ang = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            spd = random.uniform(2.2, 4.6)
            p_id = canvas.create_text(
                ox, oy,
                text=sym,
                font=("Segoe UI Emoji", random.randint(9, 13)),
                fill=col
            )
            active_particles.append({
                "id": p_id,
                "x": ox,
                "y": oy,
                "vx": math.cos(ang) * spd,
                "vy": math.sin(ang) * spd,
                "life": 1.0,
                "decay": random.uniform(0.028, 0.045)
            })

    def _spawn_sleep_particle(ox, oy):
        p_id = canvas.create_text(
            ox, oy,
            text=random.choice(["z", "Z", "zZz"]),
            font=("Segoe UI", random.randint(9, 12), "bold"),
            fill="#C084FC"
        )
        active_particles.append({
            "id": p_id,
            "x": ox,
            "y": oy,
            "vx": random.uniform(0.2, 0.6),
            "vy": random.uniform(-0.9, -0.6),
            "life": 1.0,
            "decay": 0.022
        })

    def _trigger_boxy_click():
        _clear_floor_marker()
        mascot_state["user_inactivity_ticks"] = 0
        was_asleep = (mascot_state["current"] == "sleep")
        mascot_state["current"] = "jump"
        mascot_state["jump_vel"] = -5.2
        mascot_state["idle_ticks"] = 0
        mascot_state["startled_ticks"] = 28
        _spawn_burst(mascot_state["x"], mascot_state["by1"] - 8)
        if was_asleep:
            _show_speech(random.choice(["Hoam~ Siap kerja lagi! ☕✨", "Waa! Aku bangun! 📦", "Siap patroli lagi, Bos! 🫡"]))
        else:
            _show_speech(random.choice(SPEECH_QUOTES))
        _update_status_badge("✨ Ceria!")

    def _trigger_floor_click(click_x, is_autonomous=False):
        if not is_autonomous:
            mascot_state["user_inactivity_ticks"] = 0

        cw = canvas.winfo_width()
        w = cw if cw > 50 else 760
        target = max(40.0, min(float(w - 40), float(click_x)))
        if mascot_state["current"] == "sleep":
            mascot_state["current"] = "idle"

        mascot_state["target_x"] = float(target)
        mascot_state["facing"] = 1 if target >= mascot_state["x"] else -1
        mascot_state["current"] = "walk"
        mascot_state["idle_ticks"] = 0

        floor_marker_state["active"] = True
        floor_marker_state["x"] = float(target)
        floor_marker_state["r"] = 2.0
        _update_status_badge()

    def _trigger_greet():
        _clear_floor_marker()
        mascot_state["user_inactivity_ticks"] = 0
        if mascot_state["current"] == "sleep":
            mascot_state["current"] = "idle"
        mascot_state["waving_ticks"] = 50
        mascot_state["current"] = "wave"
        mascot_state["idle_ticks"] = 0
        _spawn_burst(mascot_state["x"], mascot_state["by1"] - 8)
        _show_speech(random.choice(SPEECH_QUOTES))
        _update_status_badge()

    def _toggle_carry():
        mascot_state["user_inactivity_ticks"] = 0
        if mascot_state["current"] == "sleep":
            mascot_state["current"] = "idle"
        mascot_state["carrying"] = not mascot_state["carrying"]
        mascot_state["idle_ticks"] = 0
        if mascot_state["carrying"]:
            _show_speech("Paket siap diantar! 📦")
        else:
            _show_speech("Paket tersimpan aman! ✅")
        _update_status_badge()

    def _trigger_sleep():
        _clear_floor_marker()
        mascot_state["current"] = "sleep"
        mascot_state["idle_ticks"] = 300
        mascot_state["user_inactivity_ticks"] = 300
        _hide_speech()
        _update_status_badge()

    btn_sapa.configure(command=_trigger_greet)
    btn_paket.configure(command=_toggle_carry)
    btn_tidur.configure(command=_trigger_sleep)

    def _on_mouse_move(e):
        mascot_state["user_inactivity_ticks"] = 0
        mouse_state["x"] = float(e.x)
        mouse_state["y"] = float(e.y)
        mouse_state["active"] = True

        if mascot_state["current"] == "sleep":
            mascot_state["current"] = "idle"
            mascot_state["idle_ticks"] = 0
            _update_status_badge()

        mascot_state["idle_ticks"] = 0

        bx = mascot_state["x"]
        by = mascot_state["y"]
        if abs(e.x - bx) <= 28 and abs(e.y - by) <= 28:
            canvas.configure(cursor="hand2")
            mouse_state["hover_boxy"] = True
        else:
            canvas.configure(cursor="arrow")
            mouse_state["hover_boxy"] = False

        if mascot_state["current"] == "idle":
            if e.x > bx + 24:
                mascot_state["facing"] = 1
            elif e.x < bx - 24:
                mascot_state["facing"] = -1

    def _on_mouse_leave(e):
        mouse_state["active"] = False
        mouse_state["hover_boxy"] = False
        try:
            canvas.configure(cursor="arrow")
        except Exception:
            pass

    def _on_canvas_click(e):
        mascot_state["user_inactivity_ticks"] = 0
        mouse_state["x"] = float(e.x)
        mouse_state["y"] = float(e.y)
        mouse_state["active"] = True
        bx = mascot_state["x"]
        by = mascot_state["y"]
        if abs(e.x - bx) <= 28 and abs(e.y - by) <= 28:
            _trigger_boxy_click()
        else:
            _trigger_floor_click(e.x)

    canvas.bind("<Motion>", _on_mouse_move, add="+")
    canvas.bind("<B1-Motion>", _on_mouse_move, add="+")
    canvas.bind("<Leave>", _on_mouse_leave, add="+")
    canvas.bind("<Button-1>", _on_canvas_click, add="+")

    def _render():
        if anim_state["destroyed"] or not ornament.winfo_exists():
            return

        anim_state["tick"] += 1
        t = anim_state["tick"]

        try:
            cw = canvas.winfo_width()
            w = cw if cw > 50 else 760
            ch = canvas.winfo_height()
            h = ch if ch > 50 else 98
            y_floor = max(42, h - 18)
            scale = min(1.0, max(0.8, (h - 20) / 60.0))

            bw = int(38 * scale)
            bh = int(32 * scale)

            # ----------------------------------------------------------
            # UPDATE BACKGROUND ELEMENTS
            # ----------------------------------------------------------
            canvas.coords(bg_floor_rect, 0, y_floor, w, h)
            canvas.coords(bg_floor_line, 0, y_floor, w, y_floor)

            # Planks
            spacing = max(40, w // len(bg_planks))
            for i, p_id in enumerate(bg_planks):
                px = i * spacing + 20
                if px < w:
                    canvas.coords(p_id, px, y_floor, px, h)
                    canvas.itemconfig(p_id, state="normal")
                else:
                    canvas.itemconfig(p_id, state="hidden")

            # Warehouse crates backdrop (left)
            canvas.coords(bg_shelf[0], 18, y_floor - int(18 * scale), 42, y_floor)
            canvas.coords(bg_shelf[1], 24, y_floor - int(32 * scale), 38, y_floor - int(18 * scale))

            # Hanging warm lamps
            lamp_x1 = int(w * 0.32)
            lamp_x2 = int(w * 0.68)
            canvas.coords(bg_lamp_lines[0], lamp_x1, 0, lamp_x1, 10)
            canvas.coords(bg_lamp_bulbs[0], lamp_x1 - 3, 10, lamp_x1 + 3, 16)
            canvas.coords(bg_lamp_lines[1], lamp_x2, 0, lamp_x2, 10)
            canvas.coords(bg_lamp_bulbs[1], lamp_x2 - 3, 10, lamp_x2 + 3, 16)

            canvas.coords(bg_label, w - 16, 12)

            # ----------------------------------------------------------
            # UPDATE FLOOR DESTINATION MARKER
            # ----------------------------------------------------------
            cur_state = mascot_state["current"]

            if floor_marker_state["active"] and cur_state == "walk":
                floor_marker_state["r"] += 1.0
                fr = floor_marker_state["r"]
                fx = floor_marker_state["x"]
                fy = y_floor
                canvas.coords(dest_marker, fx - fr, fy - fr * 0.35, fx + fr, fy + fr * 0.35)
                canvas.itemconfig(dest_marker, state="normal")
                bounce_pin = int(math.sin(t * 0.25) * 2)
                canvas.coords(dest_pin, fx, fy - 14 + bounce_pin)
                canvas.itemconfig(dest_pin, state="normal")
                if fr > 22.0:
                    floor_marker_state["r"] = 2.0
            else:
                canvas.itemconfig(dest_marker, state="hidden")
                canvas.itemconfig(dest_pin, state="hidden")

            # ----------------------------------------------------------
            # MASCOT STATE MACHINE LOGIC
            # ----------------------------------------------------------
            mascot_state["user_inactivity_ticks"] += 1
            if mascot_state["startled_ticks"] > 0:
                mascot_state["startled_ticks"] -= 1

            # Blinking logic
            mascot_state["blink_counter"] += 1
            if mascot_state["blink_counter"] > 80:
                mascot_state["is_blinking"] = True
                if mascot_state["blink_counter"] > 86:
                    mascot_state["is_blinking"] = False
                    mascot_state["blink_counter"] = random.randint(0, 30)

            # Idle logic
            if cur_state == "idle":
                mascot_state["idle_ticks"] += 1
                # If idle untouched by user for > 8s (~240 ticks), fall asleep
                if mascot_state["user_inactivity_ticks"] > 240:
                    mascot_state["current"] = "sleep"
                    _clear_floor_marker()
                    _update_status_badge()
                # Autonomous patrol every ~4s if user has interacted recently
                elif mascot_state["idle_ticks"] >= 120:
                    mascot_state["idle_ticks"] = 0
                    new_target = random.randint(50, max(80, w - 50))
                    _trigger_floor_click(new_target, is_autonomous=True)

            # Walking logic
            elif cur_state == "walk":
                mascot_state["idle_ticks"] = 0
                tx = mascot_state["target_x"]
                cx = mascot_state["x"]
                dist = tx - cx
                if abs(dist) <= max(3.5, mascot_state["speed"]):
                    mascot_state["x"] = tx
                    mascot_state["current"] = "idle"
                    _clear_floor_marker()
                    # Small happy arrival hop
                    mascot_state["jump_vel"] = -3.2
                    _update_status_badge()
                else:
                    mascot_state["facing"] = 1 if dist > 0 else -1
                    mascot_state["x"] += mascot_state["speed"] * mascot_state["facing"]
                    mascot_state["walk_phase"] += 0.28

            # Waving logic
            elif cur_state == "wave":
                mascot_state["waving_ticks"] -= 1
                if mascot_state["waving_ticks"] <= 0:
                    mascot_state["current"] = "idle"
                    _update_status_badge()

            # Sleeping logic
            elif cur_state == "sleep":
                if t % 32 == 0:
                    _spawn_sleep_particle(mascot_state["x"] + 10, mascot_state["by1"] - 4)

            # Jump physics
            jump_h = 0.0
            if mascot_state["jump_vel"] != 0.0 or mascot_state["jump_y"] > 0:
                mascot_state["jump_y"] -= mascot_state["jump_vel"]
                mascot_state["jump_vel"] += 0.55  # smooth gravity
                if mascot_state["jump_y"] <= 0.0:
                    mascot_state["jump_y"] = 0.0
                    mascot_state["jump_vel"] = 0.0
                    if mascot_state["current"] == "jump":
                        mascot_state["current"] = "idle"
                        _update_status_badge()
                jump_h = mascot_state["jump_y"]

            # Compute positions
            bx = mascot_state["x"]
            bx = max(35.0, min(float(w - 35), bx))
            mascot_state["x"] = bx

            facing = mascot_state["facing"]

            # Idle bobbing breathing
            idle_bob = math.sin(t * 0.12) * 1.5 if cur_state in ("idle", "wave") else 0.0
            walk_bounce = abs(math.sin(mascot_state["walk_phase"])) * 2.5 if cur_state == "walk" else 0.0

            base_y = y_floor - int(5 * scale)
            if cur_state == "sleep":
                base_y = y_floor - int(2 * scale)

            by2 = base_y - int(jump_h) - int(idle_bob) - int(walk_bounce)
            by1 = by2 - bh
            by = (by1 + by2) // 2
            mascot_state["y"] = by
            mascot_state["by1"] = by1

            bx1 = bx - bw // 2
            bx2 = bx + bw // 2

            # ----------------------------------------------------------
            # DRAW SHADOW
            # ----------------------------------------------------------
            sw = max(6, int((18 - jump_h * 0.4) * scale))
            canvas.coords(shadow_id, bx - sw, y_floor - 3, bx + sw, y_floor + 3)

            # ----------------------------------------------------------
            # DRAW BOOTS / LEGS (RESTING DIRECTLY ON FLOOR LINE)
            # ----------------------------------------------------------
            leg_spacing = int(9 * scale)
            lx = bx - leg_spacing
            rx = bx + leg_spacing
            lift_l, lift_r = 0.0, 0.0
            swing_l, swing_r = 0.0, 0.0

            if cur_state == "walk":
                wp = mascot_state["walk_phase"]
                swing = math.sin(wp) * 6 * scale
                swing_l = swing
                swing_r = -swing
                lift_l = max(0.0, -math.sin(wp)) * 5 * scale
                lift_r = max(0.0, math.sin(wp)) * 5 * scale

            bw_boot = int(5 * scale)
            bh_boot = int(3 * scale)
            ly = y_floor - bh_boot - int(jump_h) - int(lift_l)
            ry = y_floor - bh_boot - int(jump_h) - int(lift_r)

            canvas.coords(boot_l_id, lx + swing_l - bw_boot, ly - bh_boot, lx + swing_l + bw_boot, ly + bh_boot)
            canvas.coords(boot_l_sole, lx + swing_l - bw_boot, ly + bh_boot, lx + swing_l + bw_boot, ly + bh_boot)
            canvas.coords(boot_r_id, rx + swing_r - bw_boot, ry - bh_boot, rx + swing_r + bw_boot, ry + bh_boot)
            canvas.coords(boot_r_sole, rx + swing_r - bw_boot, ry + bh_boot, rx + swing_r + bw_boot, ry + bh_boot)

            # ----------------------------------------------------------
            # DRAW BODY (CARDBOARD BOX)
            # ----------------------------------------------------------
            bev = int(4 * scale)
            body_poly = [
                bx1 + bev, by1,
                bx2 - bev, by1,
                bx2, by1 + bev,
                bx2, by2 - bev,
                bx2 - bev, by2,
                bx1 + bev, by2,
                bx1, by2 - bev,
                bx1, by1 + bev
            ]
            canvas.coords(body_id, *body_poly)

            # Packaging tape down the center
            tw = int(4 * scale)
            canvas.coords(tape_id, bx - tw, by1, bx + tw, by2)

            # Crease lines
            canvas.coords(crease_top, bx1 + 2, by1 + int(9 * scale), bx2 - 2, by1 + int(9 * scale))
            canvas.coords(crease_vert, bx, by1, bx, by1 + int(9 * scale))

            # Fragile / Love stamp
            stamp_x = bx1 + int(7 * scale) if facing >= 0 else bx2 - int(7 * scale)
            canvas.coords(stamp_id, stamp_x, by2 - int(7 * scale))

            # ----------------------------------------------------------
            # DRAW ARMS / HANDS (DIRECTION-AWARE WAVING)
            # ----------------------------------------------------------
            is_waving = (cur_state == "wave") or (mouse_state["hover_boxy"] and cur_state != "sleep")
            is_carrying = mascot_state["carrying"] and (cur_state != "sleep")

            if is_carrying:
                canvas.coords(arm_l_id, bx1 + int(4 * scale), by + int(4 * scale), bx - int(10 * scale), by + int(6 * scale))
                canvas.coords(hand_l_id, bx - int(12 * scale), by + int(4 * scale), bx - int(8 * scale), by + int(8 * scale))
                canvas.coords(arm_r_id, bx2 - int(4 * scale), by + int(4 * scale), bx + int(10 * scale), by + int(6 * scale))
                canvas.coords(hand_r_id, bx + int(8 * scale), by + int(4 * scale), bx + int(12 * scale), by + int(8 * scale))

                pbw = int(9 * scale)
                pbh = int(7 * scale)
                canvas.coords(carry_box, bx - pbw, by + int(2 * scale), bx + pbw, by + int(2 * scale) + pbh * 2)
                canvas.coords(carry_tape, bx, by + int(2 * scale), bx, by + int(2 * scale) + pbh * 2)
                canvas.coords(carry_ribbon, bx - pbw, by + int(2 * scale) + pbh, bx + pbw, by + int(2 * scale) + pbh)
                canvas.itemconfig(carry_box, state="normal")
                canvas.itemconfig(carry_tape, state="normal")
                canvas.itemconfig(carry_ribbon, state="normal")
            elif is_waving:
                canvas.itemconfig(carry_box, state="hidden")
                canvas.itemconfig(carry_tape, state="hidden")
                canvas.itemconfig(carry_ribbon, state="hidden")

                wave_ang = math.sin(t * 0.35) * 5 * scale
                if facing >= 0:
                    canvas.coords(arm_l_id, bx1, by, bx1 - int(4 * scale), by + int(7 * scale))
                    canvas.coords(hand_l_id, bx1 - int(6 * scale), by + int(5 * scale), bx1 - int(2 * scale), by + int(9 * scale))
                    wax = bx2 + int(3 * scale) + wave_ang
                    way = by1 + int(2 * scale)
                    canvas.coords(arm_r_id, bx2, by, wax, way)
                    canvas.coords(hand_r_id, wax - int(3 * scale), way - int(3 * scale), wax + int(3 * scale), way + int(3 * scale))
                else:
                    canvas.coords(arm_r_id, bx2, by, bx2 + int(4 * scale), by + int(7 * scale))
                    canvas.coords(hand_r_id, bx2 + int(2 * scale), by + int(5 * scale), bx2 + int(6 * scale), by + int(9 * scale))
                    wax = bx1 - int(3 * scale) - wave_ang
                    way = by1 + int(2 * scale)
                    canvas.coords(arm_l_id, bx1, by, wax, way)
                    canvas.coords(hand_l_id, wax - int(3 * scale), way - int(3 * scale), wax + int(3 * scale), way + int(3 * scale))
            else:
                canvas.coords(arm_l_id, bx1, by, bx1 - int(4 * scale), by + int(7 * scale))
                canvas.coords(hand_l_id, bx1 - int(6 * scale), by + int(5 * scale), bx1 - int(2 * scale), by + int(9 * scale))
                canvas.coords(arm_r_id, bx2, by, bx2 + int(4 * scale), by + int(7 * scale))
                canvas.coords(hand_r_id, bx2 + int(2 * scale), by + int(5 * scale), bx2 + int(6 * scale), by + int(9 * scale))

                canvas.itemconfig(carry_box, state="hidden")
                canvas.itemconfig(carry_tape, state="hidden")
                canvas.itemconfig(carry_ribbon, state="hidden")

            # ----------------------------------------------------------
            # DRAW HARDHAT
            # ----------------------------------------------------------
            h_dw = int(16 * scale)
            h_dh = int(12 * scale)
            canvas.coords(hardhat_dome, bx - h_dw, by1 - h_dh, bx + h_dw, by1 + int(5 * scale))
            canvas.coords(hardhat_brim, bx - h_dw - int(4 * scale), by1, bx + h_dw + int(4 * scale), by1)
            canvas.coords(hardhat_shine, bx - int(11 * scale), by1 - int(10 * scale), bx + int(3 * scale), by1 + int(2 * scale))
            canvas.coords(hardhat_badge, bx, by1 - int(5 * scale))

            # ----------------------------------------------------------
            # DRAW FACE (EYES, CHEEKS, MOUTH, STARTLED REACTION)
            # ----------------------------------------------------------
            eye_off_x = int(8 * scale)
            if facing >= 0:
                ex1 = bx - eye_off_x + int(1 * scale)
                ex2 = bx + eye_off_x + int(3 * scale)
            else:
                ex1 = bx - eye_off_x - int(3 * scale)
                ex2 = bx + eye_off_x - int(1 * scale)

            ey = by1 + int(14 * scale)

            pupil_ox = 0.0
            pupil_oy = 0.0
            if mouse_state["active"] and cur_state != "sleep":
                dx_m = mouse_state["x"] - bx
                dy_m = mouse_state["y"] - ey
                pupil_ox = max(-1.6, min(1.6, dx_m * 0.012))
                pupil_oy = max(-1.2, min(1.2, dy_m * 0.012))

            er_w = int(3.2 * scale)
            er_h = int(4.5 * scale)

            is_sleeping = (cur_state == "sleep")
            is_blinking = mascot_state["is_blinking"]
            is_startled = (mascot_state["startled_ticks"] > 0)

            if is_sleeping or is_blinking:
                canvas.itemconfig(eye_l_oval, state="hidden")
                canvas.itemconfig(eye_l_hl1, state="hidden")
                canvas.itemconfig(eye_l_hl2, state="hidden")
                canvas.itemconfig(eye_r_oval, state="hidden")
                canvas.itemconfig(eye_r_hl1, state="hidden")
                canvas.itemconfig(eye_r_hl2, state="hidden")

                arc_col = "#334155" if is_sleeping else "#0F172A"
                canvas.coords(eye_l_arc, ex1 - er_w, ey - er_h, ex1 + er_w, ey + er_h)
                canvas.coords(eye_r_arc, ex2 - er_w, ey - er_h, ex2 + er_w, ey + er_h)
                canvas.itemconfig(eye_l_arc, state="normal", outline=arc_col)
                canvas.itemconfig(eye_r_arc, state="normal", outline=arc_col)
            else:
                canvas.itemconfig(eye_l_arc, state="hidden")
                canvas.itemconfig(eye_r_arc, state="hidden")

                cur_er_w = er_w + (1 if is_startled else 0)
                cur_er_h = er_h + (1 if is_startled else 0)

                canvas.coords(eye_l_oval, ex1 + pupil_ox - cur_er_w, ey + pupil_oy - cur_er_h, ex1 + pupil_ox + cur_er_w, ey + pupil_oy + cur_er_h)
                canvas.coords(eye_l_hl1, ex1 + pupil_ox + 0.5, ey + pupil_oy - 2.5, ex1 + pupil_ox + 2.5, ey + pupil_oy - 0.5)
                canvas.coords(eye_l_hl2, ex1 + pupil_ox - 1.8, ey + pupil_oy + 1.2, ex1 + pupil_ox - 0.5, ey + pupil_oy + 2.5)

                canvas.coords(eye_r_oval, ex2 + pupil_ox - cur_er_w, ey + pupil_oy - cur_er_h, ex2 + pupil_ox + cur_er_w, ey + pupil_oy + cur_er_h)
                canvas.coords(eye_r_hl1, ex2 + pupil_ox + 0.5, ey + pupil_oy - 2.5, ex2 + pupil_ox + 2.5, ey + pupil_oy - 0.5)
                canvas.coords(eye_r_hl2, ex2 + pupil_ox - 1.8, ey + pupil_oy + 1.2, ex2 + pupil_ox - 0.5, ey + pupil_oy + 2.5)

                canvas.itemconfig(eye_l_oval, state="normal")
                canvas.itemconfig(eye_l_hl1, state="normal")
                canvas.itemconfig(eye_l_hl2, state="normal")
                canvas.itemconfig(eye_r_oval, state="normal")
                canvas.itemconfig(eye_r_hl1, state="normal")
                canvas.itemconfig(eye_r_hl2, state="normal")

            # Cheeks (blush intensifies when startled)
            cr_w = int(3.5 * scale)
            cr_h = int(2.5 * scale)
            cheek_col = "#F43F5E" if is_startled else "#FB7185"
            canvas.itemconfig(cheek_l, fill=cheek_col)
            canvas.itemconfig(cheek_r, fill=cheek_col)
            canvas.coords(cheek_l, ex1 - int(4 * scale) - cr_w, ey + int(6 * scale) - cr_h, ex1 - int(4 * scale) + cr_w, ey + int(6 * scale) + cr_h)
            canvas.coords(cheek_r, ex2 + int(4 * scale) - cr_w, ey + int(6 * scale) - cr_h, ex2 + int(4 * scale) + cr_w, ey + int(6 * scale) + cr_h)

            # Mouth
            my = ey + int(7 * scale)
            if cur_state in ("jump", "wave") or speech_state["active"] or is_startled:
                canvas.itemconfig(mouth_smile, state="hidden")
                canvas.coords(mouth_open, bx - int(3 * scale), my - int(1 * scale), bx + int(3 * scale), my + int(5 * scale))
                canvas.itemconfig(mouth_open, state="normal")
            else:
                canvas.itemconfig(mouth_open, state="hidden")
                canvas.coords(mouth_smile, bx - int(3.5 * scale), my - int(2 * scale), bx + int(3.5 * scale), my + int(3 * scale))
                canvas.itemconfig(mouth_smile, state="normal")

            # ----------------------------------------------------------
            # DRAW SPEECH BUBBLE (BOUNDS CLAMPED - ZERO CLIPPING)
            # ----------------------------------------------------------
            if speech_state["active"]:
                speech_state["ticks_left"] -= 1
                if speech_state["ticks_left"] <= 0:
                    _hide_speech()
                else:
                    stxt = speech_state["text"]
                    tw = min(max(90, len(stxt) * 7 + 16), max(100, w - 16))
                    th = 24
                    bcx = max(tw // 2 + 8, min(w - tw // 2 - 8, int(bx)))
                    x1 = bcx - tw // 2
                    x2 = bcx + tw // 2
                    # Guaranteed on-screen clamping vertically
                    y1 = max(4, min(by1 - int(14 * scale) - th, max(4, h - th - 6)))
                    y2 = y1 + th
                    tx_tail = max(x1 + 8, min(x2 - 8, int(bx)))
                    ty_tail = max(y2 + 2, min(by1 - int(2 * scale), y2 + 8))

                    poly = [
                        x1, y1,
                        x2, y1,
                        x2, y2,
                        tx_tail + 5, y2,
                        tx_tail, ty_tail,
                        tx_tail - 5, y2,
                        x1, y2
                    ]
                    canvas.coords(bubble_bg, *poly)
                    canvas.coords(bubble_txt, bcx, (y1 + y2) // 2)

            # ----------------------------------------------------------
            # UPDATE PARTICLES
            # ----------------------------------------------------------
            surviving = []
            for p in active_particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.08
                p["life"] -= p["decay"]
                if p["life"] > 0:
                    canvas.coords(p["id"], p["x"], p["y"])
                    surviving.append(p)
                else:
                    try:
                        canvas.delete(p["id"])
                    except Exception:
                        pass
            active_particles[:] = surviving

        except Exception:
            pass

        anim_state["timer"] = safe_after(ornament, 32, _render)

    # Memulai loop animasi
    anim_state["timer"] = safe_after(ornament, 32, _render)

    # Cleanup aman saat widget dihancurkan
    def _destroy_handler(e=None):
        if e is not None:
            w = getattr(e, "widget", None)
            if w not in (ornament, getattr(ornament, "_canvas", None)) and str(w) != str(ornament):
                return
        anim_state["destroyed"] = True
        _clear_floor_marker()
        if anim_state["timer"]:
            cancel_timer(ornament, anim_state["timer"])
            anim_state["timer"] = None
        for p in active_particles:
            try:
                canvas.delete(p["id"])
            except Exception:
                pass
        active_particles.clear()

    ornament.bind("<Destroy>", _destroy_handler, add="+")

    # Public API on widget
    ornament.boxy_state = mascot_state
    ornament.get_state = lambda: mascot_state["current"]
    ornament.trigger_jump = _trigger_boxy_click
    ornament.walk_to = _trigger_floor_click
    ornament.trigger_sleep = _trigger_sleep
    ornament.toggle_carry = _toggle_carry
    ornament.say = _show_speech
    ornament.canvas = canvas
    ornament.btn_sapa = btn_sapa
    ornament.btn_paket = btn_paket
    ornament.btn_tidur = btn_tidur

    return ornament


def buat_maskot_gudang(parent):
    """Alias bahasa Indonesia untuk create_warehouse_mascot."""
    return create_warehouse_mascot(parent)


def create_animated_dashboard_ornament(parent):
    """Alias kompatibilitas untuk create_warehouse_mascot."""
    return create_warehouse_mascot(parent)


def buat_ornamen_dashboard(parent):
    """Alias kompatibilitas untuk buat_maskot_gudang."""
    return buat_maskot_gudang(parent)


# ==============================================================================
# FORM CONTAINER
# ==============================================================================
def create_modern_form(parent):
    """Membuat panel kontainer formulir dengan sudut membulat dan kartu bayangan."""
    form_frame = ctk.CTkFrame(
        parent,
        fg_color=BG_CARD,
        corner_radius=14,
        border_width=1,
        border_color=BORDER
    )
    form_frame.pack(fill="both", expand=True, padx=36, pady=20)

    # Sub-header kartu formulir
    form_header = ctk.CTkFrame(form_frame, fg_color="transparent")
    form_header.pack(fill="x", padx=24, pady=(18, 12))

    ctk.CTkLabel(
        form_header,
        text="📝  Formulir Parameter Data Barang",
        font=FONT_FORM_TITLE,
        text_color=TEXT_MAIN,
        anchor="w"
    ).pack(anchor="w")

    ctk.CTkLabel(
        form_header,
        text="Lengkapi seluruh field di bawah ini sebelum menyimpan ke basis data",
        font=FONT_FORM_SUB,
        text_color=TEXT_MUTED,
        anchor="w"
    ).pack(anchor="w", pady=(3, 0))

    # Garis pembatas tipis
    ctk.CTkFrame(
        form_frame,
        fg_color=BORDER,
        height=1
    ).pack(fill="x", padx=24, pady=(0, 14))

    return form_frame


# ==============================================================================
# ENTRY MODERN DENGAN LABEL
# ==============================================================================
def create_modern_entry(parent, label_text, placeholder=""):
    """
    Membuat input teks modern dengan label di atasnya, sudut membulat,
    serta efek highlight border fokus.
    """
    box = ctk.CTkFrame(parent, fg_color="transparent")
    box.pack(fill="x", padx=24, pady=8)

    lbl = ctk.CTkLabel(
        box,
        text=label_text,
        font=FONT_LABEL,
        text_color=TEXT_MUTED,
        anchor="w"
    )
    lbl.pack(anchor="w", pady=(0, 5))

    if not placeholder:
        lbl_lower = label_text.lower()
        if "nama" in lbl_lower:
            placeholder = "Contoh: Laptop Asus VivoBook 15"
        elif "kategori" in lbl_lower:
            placeholder = "Contoh: Elektronik, Alat Tulis, Perkakas"
        elif "sku" in lbl_lower:
            placeholder = "Contoh: ELE-001, ATK-105"

    entry = ctk.CTkEntry(
        box,
        placeholder_text=placeholder,
        height=44,
        corner_radius=8,
        fg_color=BG_INPUT,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT_MAIN,
        placeholder_text_color=TEXT_SUBTLE,
        font=FONT_ENTRY
    )
    entry.pack(fill="x")

    def on_focus_in(e=None):
        entry.configure(border_color=BORDER_FOCUS, border_width=2)

    def on_focus_out(e=None):
        entry.configure(border_color=BORDER, border_width=1)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

    return entry


# ==============================================================================
# BUTTON UMUM MODERN
# ==============================================================================
def create_modern_button(parent, text, command, bg_color="#2563EB", width=140, side="left"):
    """Membuat tombol aksi modern dengan sudut membulat, efek hover, feedback tekan interaktif, dan ukuran adaptif."""
    pixel_width = max(width * 10, 120) if (width and width < 50) else (width or 140)
    hover_col = adjust_color_brightness(bg_color, 1.15)
    press_col = adjust_color_brightness(bg_color, 0.82)

    btn = ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=bg_color,
        hover_color=hover_col,
        height=42,
        width=pixel_width,
        corner_radius=8,
        font=FONT_BUTTON,
        text_color="#FFFFFF"
    )

    def on_btn_press(e=None):
        try:
            btn.configure(fg_color=press_col)
        except Exception:
            pass

    def on_btn_release(e=None):
        try:
            x, y = btn.winfo_pointerxy()
            bx = btn.winfo_rootx()
            by = btn.winfo_rooty()
            bw = btn.winfo_width()
            bh = btn.winfo_height()
            is_hovered = (bx <= x < bx + bw) and (by <= y < by + bh)
            btn.configure(fg_color=hover_col if is_hovered else bg_color)
        except Exception:
            try:
                btn.configure(fg_color=bg_color)
            except Exception:
                pass

    btn.bind("<ButtonPress-1>", on_btn_press, add="+")
    btn.bind("<ButtonRelease-1>", on_btn_release, add="+")

    if side and side != "none":
        btn.pack(side=side, padx=6, pady=4)
    return btn


# ==============================================================================
# MODERN TABLE (PENGGANTI TREEVIEW DENGAN PENCARIAN REAL-TIME & BADGES)
# ==============================================================================
class ModernTable(ctk.CTkFrame):
    """
    Tabel modern berbasis CustomTkinter dengan:
    1. Search bar real-time
    2. Filter kategori dropdown
    3. Status pill badges
    4. Tombol aksi hapus dengan konfirmasi dan sinkronisasi CSV
    5. Dukungan penuh kompatibilitas Treeview:
       get_children(), delete(*items), insert(parent, index, iid=None, values=..., tags=..., **kw),
       clear(), item(row_id, option=None), heading(col, **kw), column(col, **kw),
       tag_configure(tag, **kw), selection(), selection_set(*items), focus(item=None).
    """

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.pack(fill="both", expand=True)

        self._rows = {}
        self._counter = 0
        self._selected_rows = []
        self._total_label = None
        self._headings = {}
        self._columns = {}
        self._tags = {}

        # Toolbar Atas: Search & Filter Kategori
        self._create_toolbar()

        # Header Kolom Tabel
        self._create_table_header()

        # Area Baris (Scrollable Frame)
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=8
        )
        self.scroll.pack(fill="both", expand=True, pady=(6, 0))

        # Kartu Kosong (Empty State)
        self.empty_card = ctk.CTkFrame(
            self.scroll,
            fg_color=BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=BORDER,
            height=160
        )
        lbl_empty_icon = None
        try:
            empty_img = load_ctk_image("empty_box.png", size=(52, 52))
            if empty_img:
                lbl_empty_icon = ctk.CTkLabel(self.empty_card, image=empty_img, text="")
        except Exception:
            lbl_empty_icon = None

        if lbl_empty_icon is None:
            lbl_empty_icon = ctk.CTkLabel(
                self.empty_card,
                text="📦",
                font=("Segoe UI", 32)
            )
        lbl_empty_icon.pack(pady=(22, 6))
        lbl_empty_msg = ctk.CTkLabel(
            self.empty_card,
            text="Belum ada data barang atau hasil pencarian kosong",
            font=("Segoe UI", 12, "bold"),
            text_color=TEXT_MUTED
        )
        lbl_empty_msg.pack(pady=(0, 24))

        self._update_empty_state()

    def set_total_label(self, label):
        """Menghubungkan label total barang agar otomatis diperbarui setiap ada perubahan."""
        self._total_label = label
        self._update_total_label()

    def _update_total_label(self):
        if self._total_label is not None:
            count = len(self._rows)
            try:
                self._total_label.configure(text=f"📦 Total Barang: {count}")
            except Exception:
                try:
                    self._total_label.config(text=f"📦 Total Barang: {count}")
                except Exception:
                    pass

    def _create_toolbar(self):
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, 8))

        # Search Box
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍 Cari berdasarkan Nama Barang, Kategori, atau SKU...",
            height=42,
            corner_radius=8,
            fg_color=BG_CARD,
            border_color=BORDER,
            text_color=TEXT_MAIN,
            placeholder_text_color=TEXT_SUBTLE,
            font=FONT_TABLE_SEARCH
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search_entry.bind("<KeyRelease>", lambda e: self._apply_filter())

        # Category Filter Dropdown
        categories = ["Semua Kategori"] + KategoriBarang.DAFTAR
        self.cat_menu = ctk.CTkOptionMenu(
            toolbar,
            values=categories,
            command=lambda v: self._apply_filter(),
            height=42,
            corner_radius=8,
            fg_color=BG_CARD,
            button_color=BORDER,
            button_hover_color=BORDER_FOCUS,
            text_color=TEXT_MAIN,
            dropdown_fg_color=BG_CARD,
            dropdown_text_color=TEXT_MAIN,
            font=FONT_TABLE_SEARCH
        )
        self.cat_menu.pack(side="right")

    def _create_table_header(self):
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color="#182234",
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
            height=42
        )
        self.header_frame.pack(fill="x", padx=(0, 16))
        self.header_frame.grid_columnconfigure(0, weight=1, minsize=60)   # No
        self.header_frame.grid_columnconfigure(1, weight=5, minsize=210)  # Nama Barang
        self.header_frame.grid_columnconfigure(2, weight=3, minsize=145)  # Kategori
        self.header_frame.grid_columnconfigure(3, weight=3, minsize=135)  # SKU
        self.header_frame.grid_columnconfigure(4, weight=2, minsize=115)  # Status
        self.header_frame.grid_columnconfigure(5, weight=1, minsize=65)   # Aksi

        self._header_labels = {}
        headers = [
            (0, "no", "NO", "center"),
            (1, "nama_barang", "NAMA BARANG", "w"),
            (2, "kategori", "KATEGORI", "w"),
            (3, "kode_sku", "KODE SKU", "w"),
            (4, "status", "STATUS", "center"),
            (5, "aksi", "AKSI", "center")
        ]

        for col_idx, col_key, text, anchor in headers:
            lbl = ctk.CTkLabel(
                self.header_frame,
                text=text,
                font=FONT_TABLE_HEADER,
                text_color=TEXT_MUTED,
                anchor=anchor
            )
            lbl.grid(row=0, column=col_idx, padx=8, pady=8, sticky="ew")
            self._header_labels[col_key] = lbl

    def heading(self, column, text=None, **kw):
        """Kompatibilitas Treeview.heading."""
        if text is not None:
            self._headings[column] = text
            if column in self._header_labels:
                self._header_labels[column].configure(text=text)
        elif "text" in kw:
            t = kw["text"]
            self._headings[column] = t
            if column in self._header_labels:
                self._header_labels[column].configure(text=t)
        return self._headings.get(column, "")

    def column(self, column, width=None, **kw):
        """Kompatibilitas Treeview.column."""
        if width is not None:
            self._columns[column] = width
        return self._columns.get(column, {})

    def tag_configure(self, tagname, **kw):
        """Kompatibilitas Treeview.tag_configure."""
        self._tags[tagname] = kw
        return kw

    def selection(self):
        """Mengembalikan tuple id baris yang sedang dipilih."""
        return tuple(self._selected_rows)

    def selection_set(self, *items):
        """Menyetel baris yang dipilih."""
        self._selected_rows = list(items)
        for r_id, r_info in self._rows.items():
            if r_id in self._selected_rows:
                r_info["frame"].configure(border_color=BORDER_FOCUS, border_width=2)
            else:
                r_info["frame"].configure(border_color=BORDER, border_width=1)

    def focus(self, item=None):
        """Kompatibilitas Treeview.focus."""
        if item is not None:
            self.selection_set(item)
            return item
        return self._selected_rows[0] if self._selected_rows else ""

    def insert(self, parent="", index="end", iid=None, values=(), tags=(), **kw):
        """
        Menambahkan baris baru ke dalam tabel (kompatibel penuh dengan Treeview.insert).
        Menerima positional maupun keyword arguments: values=..., iid=..., tags=...
        """
        self._counter += 1
        row_id = str(iid) if iid is not None else f"row_{self._counter}"

        vals = kw.get("values", values)
        row_tags = kw.get("tags", tags)

        no = vals[0] if len(vals) > 0 else len(self._rows) + 1
        nama = vals[1] if len(vals) > 1 else "-"
        kategori = vals[2] if len(vals) > 2 else "Lain-lain"
        sku = vals[3] if len(vals) > 3 else "-"
        status = vals[4] if len(vals) > 4 else "Tersedia"

        row_frame = ctk.CTkFrame(
            self.scroll,
            fg_color=BG_CARD,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
            height=50
        )
        row_frame.pack(fill="x", pady=3, padx=2)
        row_frame.grid_columnconfigure(0, weight=1, minsize=60)
        row_frame.grid_columnconfigure(1, weight=5, minsize=210)
        row_frame.grid_columnconfigure(2, weight=3, minsize=145)
        row_frame.grid_columnconfigure(3, weight=3, minsize=135)
        row_frame.grid_columnconfigure(4, weight=2, minsize=115)
        row_frame.grid_columnconfigure(5, weight=1, minsize=65)

        # Col 0: No
        lbl_no = ctk.CTkLabel(
            row_frame,
            text=f"#{int(no):02d}" if str(no).isdigit() else str(no),
            font=FONT_TABLE_MONO,
            text_color=TEXT_SUBTLE,
            anchor="center"
        )
        lbl_no.grid(row=0, column=0, padx=8, pady=10, sticky="ew")

        # Col 1: Nama Barang
        lbl_nama = ctk.CTkLabel(
            row_frame,
            text=str(nama),
            font=FONT_TABLE_ROW,
            text_color=TEXT_MAIN,
            anchor="w"
        )
        lbl_nama.grid(row=0, column=1, padx=8, pady=10, sticky="ew")

        # Col 2: Kategori Badge
        kat_color = KategoriBarang.get_warna(kategori)
        lbl_kat = ctk.CTkLabel(
            row_frame,
            text=f"  {KategoriBarang.get_ikon(kategori)} {kategori}  ",
            font=FONT_TABLE_BADGE,
            text_color="#FFFFFF",
            fg_color=adjust_color_brightness(kat_color, 0.4),
            corner_radius=6
        )
        lbl_kat.grid(row=0, column=2, padx=8, pady=10, sticky="w")

        # Col 3: SKU Mono Tag
        lbl_sku = ctk.CTkLabel(
            row_frame,
            text=f" {sku} ",
            font=FONT_TABLE_MONO,
            text_color=ACCENT_BLUE,
            fg_color=BG_APP,
            corner_radius=6
        )
        lbl_sku.grid(row=0, column=3, padx=8, pady=10, sticky="w")

        # Col 4: Status Pill
        st_norm = str(status).strip().lower()
        if st_norm == "tersedia":
            st_fg = "#064E3B"
            st_txt = "#34D399"
            st_icon = "🟢"
        elif st_norm == "habis":
            st_fg = "#7F1D1D"
            st_txt = "#F87171"
            st_icon = "🔴"
        else:
            st_fg = "#78350F"
            st_txt = "#FBBF24"
            st_icon = "🟡"

        lbl_status = ctk.CTkLabel(
            row_frame,
            text=f"{st_icon} {status}",
            font=FONT_TABLE_BADGE,
            text_color=st_txt,
            fg_color=st_fg,
            corner_radius=6
        )
        lbl_status.grid(row=0, column=4, padx=8, pady=10, sticky="ew")

        # Col 5: Tombol Hapus Baris
        btn_del = ctk.CTkButton(
            row_frame,
            text="🗑️",
            width=34,
            height=30,
            corner_radius=6,
            fg_color="transparent",
            hover_color=ACCENT_ROSE,
            text_color=TEXT_MUTED,
            font=("Segoe UI", 12),
            command=lambda r=row_id, s=sku, n=nama: self._delete_row_permanently(r, s, n)
        )
        btn_del.grid(row=0, column=5, padx=8, pady=8)

        # Hover & Selection
        def on_enter(e=None):
            if row_id not in self._selected_rows:
                row_frame.configure(fg_color=BG_CARD_HOVER)

        def on_leave(e=None):
            if row_id not in self._selected_rows:
                row_frame.configure(fg_color=BG_CARD)

        def on_select(e=None):
            self.selection_set(row_id)

        for w in (row_frame, lbl_no, lbl_nama):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_select)

        self._rows[row_id] = {
            "frame": row_frame,
            "lbl_no": lbl_no,
            "values": vals,
            "tags": row_tags or (),
            "nama": str(nama),
            "kategori": str(kategori),
            "sku": str(sku),
            "status": str(status)
        }

        self._update_empty_state()
        self._update_total_label()
        return row_id

    def insert_item(self, no, nama, kategori, sku, status):
        """Metode utilitas untuk memasukkan data secara eksplisit."""
        return self.insert("", "end", values=(no, nama, kategori, sku, status))

    def _renumber_rows(self):
        """Mengurutkan kembali penomoran baris aktif (No. 1, 2, 3...)."""
        for idx, (r_id, r_info) in enumerate(self._rows.items(), start=1):
            if "lbl_no" in r_info:
                try:
                    r_info["lbl_no"].configure(text=f"#{idx:02d}")
                except Exception:
                    pass
                old_v = list(r_info["values"])
                if old_v:
                    old_v[0] = idx
                    r_info["values"] = tuple(old_v)

    def _delete_row_permanently(self, row_id, sku, nama):
        """Menghapus item dari antarmuka dan file barang.csv secara langsung."""
        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus '{nama}' (SKU: {sku}) dari inventaris gudang?"
        )
        if not konfirmasi:
            return

        # Hapus dari CSV
        base_dir = os.path.dirname(os.path.abspath(__file__))
        tampil_mod = sys.modules.get("tampil_barang")
        csv_file = getattr(tampil_mod, "CSV_PATH", os.path.join(base_dir, "barang.csv"))
        if os.path.exists(csv_file):
            try:
                remaining_rows = []
                with open(csv_file, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    if header:
                        remaining_rows.append(header)
                    for r in reader:
                        if len(r) >= 3 and r[2].strip().upper() == sku.strip().upper():
                            continue
                        remaining_rows.append(r)

                with open(csv_file, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerows(remaining_rows)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghapus dari file: {e}")
                return

        self.delete(row_id)
        self._renumber_rows()
        self._update_total_label()
        toast_shown = False
        try:
            t = show_toast(self, f"Barang '{nama}' berhasil dihapus.", "info")
            toast_shown = t is not None
        except Exception:
            toast_shown = False
        if not toast_shown:
            messagebox.showinfo("Berhasil", f"Barang '{nama}' berhasil dihapus.")

    def get_children(self, item=None):
        """Mengembalikan daftar id seluruh baris aktif."""
        return list(self._rows.keys())

    def delete(self, *items):
        """
        Menghapus satu atau beberapa baris data dari tabel.
        Mendukung pemanggilan: tree.delete(item) atau tree.delete(*tree.get_children())
        """
        for item_id in items:
            if item_id in self._rows:
                try:
                    self._rows[item_id]["frame"].destroy()
                except Exception:
                    pass
                del self._rows[item_id]
            if item_id in self._selected_rows:
                self._selected_rows.remove(item_id)

        self._update_empty_state()
        self._update_total_label()

    def clear(self):
        """Menghapus seluruh baris data."""
        self.delete(*list(self._rows.keys()))

    def item(self, row_id, option=None):
        """Mengambil metadata baris."""
        if row_id not in self._rows:
            return {}
        info = {
            "values": self._rows[row_id]["values"],
            "tags": self._rows[row_id]["tags"]
        }
        if option:
            return info.get(option)
        return info

    def _update_empty_state(self):
        """Memperbarui penampakan empty state bila baris kosong."""
        if not self._rows:
            self.empty_card.pack(fill="x", pady=20, padx=10)
        else:
            self.empty_card.pack_forget()

    def _apply_filter(self):
        """Menyaring tampilan baris tabel berdasarkan kata kunci dan kategori terpilih."""
        query = self.search_entry.get().strip().lower()
        selected_cat = self.cat_menu.get().strip()

        visible_count = 0
        for row_id, data in self._rows.items():
            frame = data["frame"]
            nama = data["nama"].lower()
            kat = data["kategori"].lower()
            sku = data["sku"].lower()

            match_query = not query or (query in nama or query in kat or query in sku)
            norm_item_cat = KategoriBarang.normalize_kategori(data["kategori"]).lower()
            norm_sel_cat = KategoriBarang.normalize_kategori(selected_cat).lower()
            match_cat = (selected_cat == "Semua Kategori") or (norm_item_cat == norm_sel_cat)

            if match_query and match_cat:
                frame.pack(fill="x", pady=3, padx=2)
                visible_count += 1
            else:
                frame.pack_forget()

        if visible_count == 0 and self._rows:
            self.empty_card.pack(fill="x", pady=20, padx=10)
        else:
            self._update_empty_state()


# ==============================================================================
# LABEL TOTAL
# ==============================================================================
def create_modern_label_total(parent):
    """
    Membuat label total counter modern dengan badge kontras
    serta kompatibilitas .config() dan .configure().
    """
    container = ctk.CTkFrame(
        parent,
        fg_color=BG_CARD,
        corner_radius=8,
        border_width=1,
        border_color=BORDER
    )
    container.pack(side="left", padx=4, pady=4)

    lbl = ctk.CTkLabel(
        container,
        text="📦 Total Barang: 0",
        font=FONT_LABEL,
        text_color=ACCENT_BLUE
    )
    lbl.pack(padx=14, pady=8)

    return lbl


# ==============================================================================
# MODERN TOAST NOTIFICATION (SLIDE-IN & FADE-OUT BANNER)
# ==============================================================================
def show_toast(master, message, toast_type="success", duration_ms=2500):
    """
    Menampilkan floating toast notification modern dengan animasi slide-in dari atas,
    jeda waktu baca (duration_ms), dan slide-out otomatis atau dismiss on click / tombol close (✕).
    """
    if master is None:
        return None

    try:
        top = master.winfo_toplevel() if hasattr(master, "winfo_toplevel") else master
        if not top or not hasattr(top, "winfo_exists") or not top.winfo_exists():
            return None
    except Exception:
        return None

    # Hapus toast aktif sebelumnya jika ada pada window yang sama
    old_toast = getattr(top, "_active_toast", None)
    if old_toast and hasattr(old_toast, "winfo_exists") and old_toast.winfo_exists():
        try:
            cancel_timer(old_toast, getattr(old_toast, "_anim_timer", None))
            cancel_timer(old_toast, getattr(old_toast, "_dismiss_timer", None))
            old_toast.destroy()
        except Exception:
            pass
        top._active_toast = None

    toast_themes = {
        "success": {
            "icon": "✅",
            "accent": "#10B981",
            "bg": "#0D281E",
            "text": "#ECFDF5"
        },
        "info": {
            "icon": "ℹ️",
            "accent": "#3B82F6",
            "bg": "#0F233D",
            "text": "#EFF6FF"
        },
        "warning": {
            "icon": "⚠️",
            "accent": "#F59E0B",
            "bg": "#2B2108",
            "text": "#FFFBEB"
        },
        "error": {
            "icon": "❌",
            "accent": "#EF4444",
            "bg": "#2D1212",
            "text": "#FEF2F2"
        }
    }
    theme = toast_themes.get(str(toast_type).strip().lower(), toast_themes["info"])

    try:
        toast = ctk.CTkFrame(
            top,
            fg_color=theme["bg"],
            corner_radius=10,
            border_width=1.5,
            border_color=theme["accent"],
            height=46
        )
    except Exception:
        return None

    top._active_toast = toast
    toast._anim_timer = None
    toast._dismiss_timer = None
    toast._is_dismissing = False

    content_box = ctk.CTkFrame(toast, fg_color="transparent")
    content_box.pack(fill="both", expand=True, padx=14, pady=8)

    # Ikon status
    lbl_icon = ctk.CTkLabel(
        content_box,
        text=theme["icon"],
        font=("Segoe UI", 13)
    )
    lbl_icon.pack(side="left", padx=(0, 10))

    # Teks pesan dengan wraplength agar tidak meluap
    try:
        top_w = top.winfo_width()
        wrap_len = max(260, top_w - 140) if top_w > 100 else 460
    except Exception:
        wrap_len = 460

    lbl_msg = ctk.CTkLabel(
        content_box,
        text=str(message),
        font=FONT_LABEL,
        text_color=theme["text"],
        anchor="w",
        wraplength=wrap_len
    )
    lbl_msg.pack(side="left", fill="x", expand=True, padx=(0, 12))

    # Tombol tutup (✕)
    btn_close = ctk.CTkButton(
        content_box,
        text="✕",
        width=24,
        height=24,
        corner_radius=12,
        fg_color="transparent",
        hover_color=theme["accent"],
        text_color=TEXT_MUTED,
        font=("Segoe UI", 11, "bold")
    )
    btn_close.pack(side="right")

    target_y = 20
    start_y = -60

    toast.place(relx=0.5, y=start_y, anchor="n")
    try:
        toast.lift()
    except Exception:
        pass
    toast._curr_y = start_y

    def _destroy_toast():
        if getattr(top, "_active_toast", None) == toast:
            top._active_toast = None
        cancel_timer(toast, getattr(toast, "_anim_timer", None))
        cancel_timer(toast, getattr(toast, "_dismiss_timer", None))
        try:
            if toast.winfo_exists():
                toast.destroy()
        except Exception:
            pass

    def _on_destroy(e=None):
        if e is not None:
            w = getattr(e, "widget", None)
            if w not in (toast, getattr(toast, "_canvas", None)) and str(w) != str(toast):
                return
        if getattr(top, "_active_toast", None) == toast:
            top._active_toast = None
        cancel_timer(toast, getattr(toast, "_anim_timer", None))
        cancel_timer(toast, getattr(toast, "_dismiss_timer", None))

    def _on_top_destroy(e=None):
        if e is not None:
            w = getattr(e, "widget", None)
            if w not in (top, getattr(top, "_canvas", None)) and str(w) != str(top):
                return
        _destroy_toast()

    def _slide_out():
        if getattr(toast, "_is_dismissing", False):
            return
        toast._is_dismissing = True
        cancel_timer(toast, getattr(toast, "_anim_timer", None))
        toast._anim_timer = None
        cancel_timer(toast, getattr(toast, "_dismiss_timer", None))
        toast._dismiss_timer = None

        steps = 8
        step_idx = [0]
        y_from = getattr(toast, "_curr_y", target_y)
        y_to = start_y

        def _out_step():
            if not toast.winfo_exists() or not top.winfo_exists():
                _destroy_toast()
                return
            step_idx[0] += 1
            progress = min(1.0, step_idx[0] / steps)
            curr = int(round(y_from + (y_to - y_from) * progress))
            toast._curr_y = curr
            try:
                toast.place_configure(y=curr)
            except Exception:
                _destroy_toast()
                return

            if progress < 1.0:
                toast._anim_timer = safe_after(toast, 18, _out_step)
            else:
                _destroy_toast()

        _out_step()

    def _slide_in():
        steps = 8
        step_idx = [0]
        y_from = start_y
        y_to = target_y

        def _in_step():
            if getattr(toast, "_is_dismissing", False):
                return
            if not toast.winfo_exists() or not top.winfo_exists():
                _destroy_toast()
                return
            step_idx[0] += 1
            progress = min(1.0, step_idx[0] / steps)
            ease = 1.0 - (1.0 - progress) * (1.0 - progress)
            curr = int(round(y_from + (y_to - y_from) * ease))
            toast._curr_y = curr
            try:
                toast.place_configure(y=curr)
            except Exception:
                _destroy_toast()
                return

            if progress < 1.0:
                toast._anim_timer = safe_after(toast, 18, _in_step)
            else:
                toast._anim_timer = None
                toast._dismiss_timer = safe_after(toast, duration_ms, _slide_out)

        _in_step()

    btn_close.configure(command=_slide_out)
    for w in (toast, content_box, lbl_icon, lbl_msg):
        w.bind("<Button-1>", lambda e: _slide_out())

    toast.bind("<Destroy>", _on_destroy, add="+")
    top.bind("<Destroy>", _on_top_destroy, add="+")

    _slide_in()
    return toast
