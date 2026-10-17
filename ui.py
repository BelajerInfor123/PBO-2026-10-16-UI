"""
ui.py - Modul Antarmuka Utama Berbasis CustomTkinter (CTK).
Menyediakan utilitas antarmuka, layout modern, dashboard kpi, maskot gudang, dan komponen interaktif.
"""

import customtkinter as ctk

# Impor palet tema & utilitas
from ui_theme import (
    BG_APP, BG_CARD, BG_CARD_HOVER, BG_INPUT, BORDER, BORDER_FOCUS,
    ACCENT_EMERALD, ACCENT_BLUE, ACCENT_ROSE, ACCENT_AMBER, ACCENT_PURPLE,
    TEXT_MAIN, TEXT_MUTED, TEXT_SUBTLE, FONT_SECTION,
    center_window, format_rupiah
)

# Impor komponen pembangun antarmuka modern
from ui_components import (
    create_modern_header,
    create_dashboard_stats,
    create_menu_card,
    create_modern_form,
    create_modern_entry,
    create_modern_button,
    create_modern_label_total,
    create_warehouse_mascot,
    create_animated_dashboard_ornament,
    ModernTable,
    adjust_color_brightness,
    show_toast,
    safe_after,
    cancel_timer,
    KategoriBarang,
    StatusStok
)

# Alias backward compatibility
tampilkan_toast = show_toast
buat_maskot_gudang = create_warehouse_mascot
buat_ornamen_dashboard = create_warehouse_mascot

# ==============================================================================
# FUNGSI INTERFACE UTAMA SESUAI STRUKTUR GITHUB
# ==============================================================================

def buat_header(parent, title, subtitle_or_color="", warna_badge=None):
    """Membuat header antarmuka modern dengan status indikator dan aksen warna."""
    return create_modern_header(parent, title, subtitle_or_color, warna_badge)


def buat_dashboard_stats(parent):
    """Menampilkan ringkasan metrik statistik KPI inventaris di dashboard utama."""
    return create_dashboard_stats(parent)


def buat_menu_button(parent, text, subtitle_or_cmd=None, command=None, bg_color="#059669", hover_color=None):
    """Membuat kartu navigasi menu modern untuk jendela dashboard utama."""
    return create_menu_card(parent, text, subtitle_or_cmd, command, bg_color, hover_color)


def buat_form(parent):
    """Membuat wadah formulir modern dengan sudut membulat dan kartu bayangan."""
    return create_modern_form(parent)


def buat_entry(parent, label_text, placeholder=""):
    """Membuat field input teks modern dengan label dan efek fokus elegan."""
    return create_modern_entry(parent, label_text, placeholder)


def buat_tombol(parent, text, command, bg_color="#2563EB", width=140, side="left"):
    """Membuat tombol aksi modern dengan efek hover dan ukuran adaptif."""
    return create_modern_button(parent, text, command, bg_color, width, side)


def buat_treeview(parent):
    """
    Membuat tabel data inventaris modern berbasis CustomTkinter
    dilengkapi live search, filter kategori, badge status, dan aksi hapus.
    """
    return ModernTable(parent)


def buat_label_total(parent):
    """Membuat badge label counter total barang inventaris."""
    return create_modern_label_total(parent)