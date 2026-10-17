"""
================================================================================
TEST_SUITE.PY - RANGKAIAN PENGUJIAN OTOMATISASI INVENTARIS GUDANG CUSTOMTKINTER
================================================================================
Memvalidasi seluruh fungsionalitas sistem:
1. TestModels: OOP Domain Models (Barang, Petugas, KategoriBarang, StatusStok).
2. TestUITheme: Utilitas Tema, Warna Hex, Penomoran Rupiah, Posisi Layar, Subscripting.
3. TestUIComponents: Komponen Antarmuka Modern CustomTkinter (Header 2/3 argumen, Form, Entry,
   Tombol, Menu Button 4/5 argumen, Table duck-typing, Stats Auto-Refresh).
4. TestTambahBarang: Alur Validasi Input, Pencegahan SKU Duplikat, 0-byte File Header Handling, & Penulisan CSV.
5. TestTampilBarang: Pembacaan CSV, Penomoran Berurutan, Baris Kosong & Total Counter Auto-Sync.
6. TestSubprocessLaunch: Eksekusi Subprocess Independen CWD Eksternal.
7. TestEdgeCases: Penanganan Berkas Rusak, Simbol Khusus (Koma & Tanda Petik).
"""

import unittest
import os
import sys
import csv
import tempfile
import shutil
import subprocess
import time

import tkinter as tk
import customtkinter as ctk

# Impor modul proyek
import models
from models import Barang, Petugas, KategoriBarang, StatusStok
import ui_components
import ui
from ui import (
    buat_header, buat_form, buat_entry, buat_tombol, buat_menu_button,
    buat_treeview, buat_label_total, buat_dashboard_stats,
    buat_ornamen_dashboard, create_animated_dashboard_ornament,
    buat_maskot_gudang, create_warehouse_mascot,
    show_toast, tampilkan_toast, safe_after, cancel_timer,
    center_window, format_rupiah,
    BG_APP, BG_CARD, BG_CARD_HOVER, BG_INPUT, BORDER, BORDER_FOCUS,
    ACCENT_EMERALD, ACCENT_BLUE, ACCENT_ROSE, ACCENT_AMBER, ACCENT_PURPLE,
    TEXT_MAIN, TEXT_MUTED
)
import tambah_barang
from tambah_barang import simpan_barang
import tampil_barang
from tampil_barang import tampilkan_barang
import Main
from Main import buka_tambah_barang, buka_tampil_barang, keluar


class TestModels(unittest.TestCase):
    """Pengujian Unit untuk Domain Model PBO dan Utilitas Kategori."""

    def test_barang_init_and_methods(self):
        b = Barang("Laptop Asus", "Elektronik", "SKU-9901", "Tersedia")
        self.assertEqual(b.nama_barang, "Laptop Asus")
        self.assertEqual(b.kategori, "Elektronik")
        self.assertEqual(b.kode_sku, "SKU-9901")
        self.assertEqual(b.status, "Tersedia")
        self.assertEqual(b.to_list(), ["Laptop Asus", "Elektronik", "SKU-9901", "Tersedia"])
        self.assertIn("Laptop Asus", str(b))

    def test_barang_extended_attributes(self):
        b = Barang(
            nama_barang="Mouse Wireless",
            kategori="Elektronik",
            kode_sku="ELE-1001",
            status="Tersedia",
            jumlah=25,
            harga=120000.0,
            lokasi="Rak A-02"
        )
        self.assertEqual(b.jumlah, 25)
        self.assertEqual(b.harga, 120000.0)
        self.assertEqual(b.lokasi, "Rak A-02")
        d = b.to_dict()
        self.assertEqual(d["kode_sku"], "ELE-1001")
        self.assertEqual(d["harga"], 120000.0)

    def test_petugas_init_and_methods(self):
        p = Petugas("P01", "Budi", "Gudang A", "08123456789")
        self.assertEqual(p.id, "P01")
        self.assertEqual(p.nama, "Budi")
        self.assertEqual(p.bagian, "Gudang A")
        self.assertEqual(p.no_hp, "08123456789")
        self.assertEqual(p.to_list(), ["P01", "Budi", "Gudang A", "08123456789"])
        self.assertIn("Budi", str(p))

    def test_kategori_barang_methods(self):
        self.assertEqual(KategoriBarang.get_prefix("Elektronik"), "ELE")
        self.assertEqual(KategoriBarang.get_prefix("Alat Tulis"), "ATK")
        self.assertEqual(KategoriBarang.get_prefix("Perkakas & Teknik"), "TKN")
        self.assertEqual(KategoriBarang.get_prefix("Unknown"), "GUD")
        self.assertIsNotNone(KategoriBarang.get_warna("Elektronik"))
        self.assertIsNotNone(KategoriBarang.get_ikon("Elektronik"))
        self.assertEqual(KategoriBarang.normalize_kategori("alat tulis"), "Alat Tulis")

    def test_status_stok_methods(self):
        self.assertEqual(StatusStok.normalize_status("tersedia"), "Tersedia")
        self.assertEqual(StatusStok.normalize_status("habis"), "Habis")
        self.assertEqual(StatusStok.normalize_status("inden"), "Inden")


class TestUITheme(unittest.TestCase):
    """Pengujian Unit untuk Tema, Warna Hex, dan Utilitas UI."""

    def test_hex_colors(self):
        colors = [BG_APP, BG_CARD, BG_INPUT, BORDER, BORDER_FOCUS, ACCENT_EMERALD, ACCENT_BLUE]
        for c in colors:
            self.assertTrue(c.startswith("#"))
            self.assertEqual(len(c), 7)

    def test_format_rupiah(self):
        self.assertEqual(format_rupiah(0), "Rp 0")
        self.assertEqual(format_rupiah(1500), "Rp 1.500")
        self.assertEqual(format_rupiah(25000000), "Rp 25.000.000")
        self.assertEqual(format_rupiah("invalid"), "Rp 0")

    def test_center_window(self):
        root = ctk.CTk()
        try:
            center_window(root, 600, 400)
            root.update()
            geom = root.geometry()
            self.assertIn("600x400", geom)
            # Verifikasi posisi y tidak overflow batas layar
            self.assertGreaterEqual(root.winfo_y(), 0)
            self.assertLessEqual(root.winfo_y() + root.winfo_height(), root.winfo_screenheight())
        finally:
            root.destroy()

    def test_widget_subscript_access(self):
        root = ctk.CTk()
        try:
            lbl = ctk.CTkLabel(root, text="Awal")
            self.assertEqual(lbl["text"], "Awal")
            lbl["text"] = "Berubah"
            self.assertEqual(lbl["text"], "Berubah")
        finally:
            root.destroy()


class TestUIComponents(unittest.TestCase):
    """Pengujian Komponen CustomTkinter Modern."""

    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.geometry("800x600")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def tearDown(self):
        for child in self.root.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self.root.update_idletasks()

    def test_header_creation_flexible_args(self):
        # 3 argumen: title, subtitle, badge
        hdr1 = buat_header(self.root, "MENU INVENTARIS GUDANG", "Subjudul Uji")
        self.assertIsInstance(hdr1, ctk.CTkFrame)

        # 2 argumen: title, hex_color (pola GitHub)
        hdr2 = buat_header(self.root, "TAMBAH DATA BARANG", "#059669")
        self.assertIsInstance(hdr2, ctk.CTkFrame)

        # 1 argumen: title saja
        hdr3 = buat_header(self.root, "MENU INVENTARIS GUDANG")
        self.assertIsInstance(hdr3, ctk.CTkFrame)

    def test_form_creation(self):
        form = buat_form(self.root)
        self.assertIsInstance(form, ctk.CTkFrame)

    def test_entry_creation_and_methods(self):
        entry = buat_entry(self.root, "Nama Barang")
        self.assertIsInstance(entry, ctk.CTkEntry)
        entry.insert(0, "Komputer Kantor")
        self.assertEqual(entry.get(), "Komputer Kantor")
        entry.delete(0, "end")
        self.assertEqual(entry.get(), "")

    def test_tombol_creation_and_invoke(self):
        clicked = []
        btn = buat_tombol(self.root, "Simpan", lambda: clicked.append(1), "#10B981")
        self.assertIsInstance(btn, ctk.CTkButton)
        btn.invoke()
        self.assertEqual(clicked, [1])

    def test_menu_button_github_signature_and_click(self):
        clicked = []
        # Pola GitHub: 4 argumen (parent, teks, cmd, warna)
        card = buat_menu_button(
            self.root,
            "📦 Tambah Barang",
            lambda: clicked.append("tambah"),
            "#10B981"
        )
        self.assertIsInstance(card, ctk.CTkFrame)
        card._on_enter()
        self.assertEqual(card.cget("border_color"), "#10B981")
        card._on_click()
        self.assertEqual(clicked, ["tambah"])
        card._on_leave()
        self.assertEqual(card.cget("border_color"), BORDER)

    def test_label_total_config_and_configure(self):
        lbl = buat_label_total(self.root)
        self.assertIsInstance(lbl, ctk.CTkLabel)
        self.assertEqual(lbl.cget("text"), "📦 Total Barang: 0")

        # Uji pemanggilan .configure(), .config(), dan ['text']
        lbl.configure(text="📦 Total Barang: 5")
        self.assertEqual(lbl.cget("text"), "📦 Total Barang: 5")

        lbl.config(text="📦 Total Barang: 10")
        self.assertEqual(lbl.cget("text"), "📦 Total Barang: 10")

        self.assertEqual(lbl["text"], "📦 Total Barang: 10")

    def test_dashboard_stats_creation_and_refresh(self):
        stats = buat_dashboard_stats(self.root)
        self.assertIsInstance(stats, ctk.CTkFrame)
        self.assertTrue(hasattr(stats, "refresh"))
        # Verifikasi tepat terdapat 3 kartu metrik (Total Barang, Stok Tersedia, Database CSV)
        cards = [w for w in stats.winfo_children() if isinstance(w, ctk.CTkFrame)]
        self.assertEqual(len(cards), 3)

        # Verifikasi teks judul kartu dan ketiadaan kartu Kategori/Klasifikasi
        card_texts = []
        for c in cards:
            for child in c.winfo_children():
                if isinstance(child, ctk.CTkFrame):
                    for sub in child.winfo_children():
                        if isinstance(sub, ctk.CTkLabel):
                            card_texts.append(sub.cget("text"))
                        elif isinstance(sub, ctk.CTkFrame):
                            for ssub in sub.winfo_children():
                                if isinstance(ssub, ctk.CTkLabel):
                                    card_texts.append(ssub.cget("text"))

        combined = " ".join(card_texts)
        self.assertIn("TOTAL BARANG", combined)
        self.assertIn("STOK TERSEDIA", combined)
        self.assertIn("DATABASE CSV", combined)
        self.assertNotIn("Klasifikasi", combined)
        self.assertNotIn("KATEGORI", combined)

        # Refresh harus dapat dipanggil tanpa error
        stats.refresh()

    def test_dashboard_stats_three_cards_geometry_and_even_distribution(self):
        """Memverifikasi 3 kartu KPI terdistribusi rata dengan lebar seimbang dan padding simetris."""
        container = ctk.CTkFrame(self.root, width=800, height=120)
        container.pack(fill="x", padx=32)
        self.root.update_idletasks()
        self.root.update()

        stats = buat_dashboard_stats(container)
        self.root.update_idletasks()
        self.root.update()

        cards = [w for w in stats.winfo_children() if isinstance(w, ctk.CTkFrame)]
        self.assertEqual(len(cards), 3)

        widths = [c.winfo_width() for c in cards]
        # Selisih lebar antar-kartu maksimal 1 piksel (pembagian integer piksel sempurna)
        self.assertLessEqual(max(widths) - min(widths), 1)

        # Verifikasi jarak/gap antar kartu konsisten
        gap1 = cards[1].winfo_x() - (cards[0].winfo_x() + cards[0].winfo_width())
        gap2 = cards[2].winfo_x() - (cards[1].winfo_x() + cards[1].winfo_width())
        self.assertEqual(gap1, gap2)
        self.assertGreater(gap1, 0)

    def test_modern_table_duck_typing(self):
        table = buat_treeview(self.root)

        # 1. Uji insert dengan positional dan kwarg iid
        r1 = table.insert("", "end", values=(1, "Monitor 24 Inch", "Elektronik", "ELE-001", "Tersedia"))
        r2 = table.insert("", "end", iid="custom_row_2", values=(2, "Pulpen Gel", "Alat Tulis", "ATK-001", "Habis"))

        children = table.get_children()
        self.assertEqual(len(children), 2)
        self.assertEqual(table.item(r1, "values")[1], "Monitor 24 Inch")
        self.assertEqual(table.item("custom_row_2", "values")[3], "ATK-001")

        # 2. Uji treeview methods: heading, column, tag_configure
        table.heading("no", text="Nomor Urut")
        self.assertEqual(table.heading("no"), "Nomor Urut")
        table.column("no", width=80)
        self.assertEqual(table.column("no"), 80)
        table.tag_configure("highlight", background="#FF0000")

        # 3. Uji selection & focus
        table.selection_set(r1)
        self.assertIn(r1, table.selection())
        self.assertEqual(table.focus(), r1)

        # 4. Uji delete dengan multiple items (*items)
        table.delete(r1, "custom_row_2")
        self.assertEqual(len(table.get_children()), 0)

        # 5. Uji clear
        table.insert("", "end", values=(1, "Item Baru", "Bahan Baku", "BBK-001", "Tersedia"))
        self.assertEqual(len(table.get_children()), 1)
        table.clear()
        self.assertEqual(len(table.get_children()), 0)

    def test_modern_table_case_insensitive_category_filter(self):
        table = buat_treeview(self.root)
        # Masukkan item dengan huruf kecil 'Alat tulis' seperti di barang.csv
        r1 = table.insert("", "end", values=(1, "Pensil 2B", "Alat tulis", "ATK-001", "Tersedia"))
        r2 = table.insert("", "end", values=(2, "Laptop Dell", "Elektronik", "ELE-001", "Tersedia"))

        # Filter berdasarkan opsi dropdown standar 'Alat Tulis' (Title Case)
        table.cat_menu.set("Alat Tulis")
        table._apply_filter()

        # Item r1 harus tetap tampil (pack info ada), r2 harus di-pack_forget
        self.assertEqual(table._rows[r1]["frame"].winfo_manager(), "pack")
        self.assertEqual(table._rows[r2]["frame"].winfo_manager(), "")

        # Kembalikan ke 'Semua Kategori'
        table.cat_menu.set("Semua Kategori")
        table._apply_filter()
        self.assertEqual(table._rows[r1]["frame"].winfo_manager(), "pack")
        self.assertEqual(table._rows[r2]["frame"].winfo_manager(), "pack")


class TestTambahBarang(unittest.TestCase):
    """Pengujian Unit Modul Tambah Barang & Integritas File CSV."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_csv = os.path.join(self.temp_dir, "test_barang.csv")
        self.orig_csv = tambah_barang.CSV_PATH
        tambah_barang.CSV_PATH = self.test_csv

        # Suppress messagebox dialogs
        self.orig_info = tambah_barang.messagebox.showinfo
        self.orig_warn = tambah_barang.messagebox.showwarning
        self.orig_err = tambah_barang.messagebox.showerror
        tambah_barang.messagebox.showinfo = lambda *a, **k: None
        tambah_barang.messagebox.showwarning = lambda *a, **k: None
        tambah_barang.messagebox.showerror = lambda *a, **k: None

    def tearDown(self):
        tambah_barang.CSV_PATH = self.orig_csv
        tambah_barang.messagebox.showinfo = self.orig_info
        tambah_barang.messagebox.showwarning = self.orig_warn
        tambah_barang.messagebox.showerror = self.orig_err
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_simpan_barang_empty_validation(self):
        root = ctk.CTk()
        try:
            e_nama = ctk.CTkEntry(root)
            e_kat = ctk.CTkEntry(root)
            e_sku = ctk.CTkEntry(root)

            # Field kosong -> Harus return False
            res = simpan_barang(e_nama, e_kat, e_sku)
            self.assertFalse(res)
            self.assertFalse(os.path.exists(self.test_csv))
        finally:
            root.destroy()

    def test_simpan_barang_success_and_duplicate_prevention(self):
        root = ctk.CTk()
        try:
            e_nama = ctk.CTkEntry(root)
            e_kat = ctk.CTkEntry(root)
            e_sku = ctk.CTkEntry(root)

            e_nama.insert(0, "Keyboard Mechanical")
            e_kat.insert(0, "Elektronik")
            e_sku.insert(0, "ELE-555")

            # Simpan item pertama -> Berhasil
            res1 = simpan_barang(e_nama, e_kat, e_sku)
            self.assertTrue(res1)
            self.assertTrue(os.path.exists(self.test_csv))

            # Verifikasi isi CSV
            with open(self.test_csv, "r", encoding="utf-8") as f:
                lines = f.readlines()
            self.assertEqual(len(lines), 2)
            self.assertIn("Keyboard Mechanical", lines[1])
            self.assertIn("ELE-555", lines[1])

            # Coba simpan kembali dengan SKU yang sama (case-insensitive) -> Harus ditolak
            e_nama.insert(0, "Keyboard Lain")
            e_kat.insert(0, "Elektronik")
            e_sku.insert(0, "ele-555")

            res_dup = simpan_barang(e_nama, e_kat, e_sku)
            self.assertFalse(res_dup)
        finally:
            root.destroy()

    def test_simpan_barang_empty_existing_file(self):
        # Buat file kosong 0-byte
        with open(self.test_csv, "w", encoding="utf-8") as f:
            pass
        self.assertEqual(os.path.getsize(self.test_csv), 0)

        root = ctk.CTk()
        try:
            e_nama = ctk.CTkEntry(root)
            e_kat = ctk.CTkEntry(root)
            e_sku = ctk.CTkEntry(root)

            e_nama.insert(0, "Printer Laser")
            e_kat.insert(0, "Elektronik")
            e_sku.insert(0, "ELE-888")

            res = simpan_barang(e_nama, e_kat, e_sku)
            self.assertTrue(res)

            with open(self.test_csv, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            # Harus terdapat header dan baris data
            self.assertEqual(len(lines), 2)
            self.assertIn("nama_barang", lines[0])
            self.assertIn("Printer Laser", lines[1])
        finally:
            root.destroy()


class TestTampilBarang(unittest.TestCase):
    """Pengujian Unit Modul Tampil Barang & Parsing CSV."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_csv = os.path.join(self.temp_dir, "test_tampil.csv")
        self.orig_csv = tampil_barang.CSV_PATH
        tampil_barang.CSV_PATH = self.test_csv

    def tearDown(self):
        tampil_barang.CSV_PATH = self.orig_csv
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tampilkan_barang_non_existent_file(self):
        root = ctk.CTk()
        try:
            tree = buat_treeview(root)
            label = buat_label_total(root)

            tampilkan_barang(tree, label)
            self.assertEqual(len(tree.get_children()), 0)
            self.assertEqual(label.cget("text"), "📦 Total Barang: 0")
        finally:
            root.destroy()

    def test_tampilkan_barang_with_data_and_blank_lines(self):
        with open(self.test_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["nama_barang", "kategori", "kode_sku", "status"])
            writer.writerow(["Item Satu", "Elektronik", "SKU-01", "Tersedia"])
            writer.writerow(["   ", "", "", ""])  # Baris kosong harus diabaikan
            writer.writerow(["Item Dua", "Alat Tulis", "SKU-02", "Habis"])

        root = ctk.CTk()
        try:
            tree = buat_treeview(root)
            label = buat_label_total(root)

            tampilkan_barang(tree, label)
            self.assertEqual(len(tree.get_children()), 2)
            self.assertEqual(label.cget("text"), "📦 Total Barang: 2")
        finally:
            root.destroy()


class TestSubprocessLaunch(unittest.TestCase):
    """Pengujian Peluncuran Subprocess dengan CWD Eksternal."""

    def test_launch_with_external_cwd(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ext_dir = os.path.expanduser("~")

        cmd = [
            sys.executable,
            "-c",
            f"import subprocess, sys, os; "
            f"p = subprocess.Popen([sys.executable, os.path.join(r'{base_dir}', 'tambah_barang.py')], cwd=r'{base_dir}'); "
            f"import time; time.sleep(0.5); p.terminate()"
        ]

        res = subprocess.run(cmd, cwd=ext_dir, capture_output=True, text=True, timeout=5)
        self.assertEqual(res.returncode, 0)


class TestEdgeCases(unittest.TestCase):
    """Pengujian Khusus Kasus Batas (Edge Cases)."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_csv = os.path.join(self.temp_dir, "edge_cases.csv")
        self.orig_csv = tampil_barang.CSV_PATH
        tampil_barang.CSV_PATH = self.test_csv

    def tearDown(self):
        tampil_barang.CSV_PATH = self.orig_csv
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_special_characters_in_csv(self):
        # Menyimpan item dengan koma, kutip ganda, dan simbol
        with open(self.test_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["nama_barang", "kategori", "kode_sku", "status"])
            writer.writerow(['Kabel "HDMI" 4K, 2m', "Elektronik & Gadget", "ELE/SPEC-01", "Tersedia"])

        root = ctk.CTk()
        try:
            tree = buat_treeview(root)
            label = buat_label_total(root)

            tampilkan_barang(tree, label)
            children = tree.get_children()
            self.assertEqual(len(children), 1)
            row_data = tree.item(children[0], "values")
            self.assertEqual(row_data[1], 'Kabel "HDMI" 4K, 2m')
        finally:
            root.destroy()

    def test_corrupted_csv_format(self):
        with open(self.test_csv, "w", encoding="utf-8") as f:
            f.write("Some,Header,Only\n")
            f.write("\n\n")
            f.write("OnlyOneCol\n")
            f.write("Valid Item,Kategori,SKU-CORR,Tersedia\n")

        root = ctk.CTk()
        try:
            tree = buat_treeview(root)
            label = buat_label_total(root)

            tampilkan_barang(tree, label)
            self.assertEqual(len(tree.get_children()), 1)
            self.assertEqual(label.cget("text"), "📦 Total Barang: 1")
        finally:
            root.destroy()


class TestInteractiveAnimations(unittest.TestCase):
    """Pengujian Unit untuk Animasi Interaktif CustomTkinter."""

    @classmethod
    def setUpClass(cls):
        cls.root = ctk.CTk()
        cls.root.geometry("860x600")

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def tearDown(self):
        for child in self.root.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass
        self.root.update_idletasks()

    def test_animated_count_up(self):
        stats = buat_dashboard_stats(self.root)
        self.assertIsInstance(stats, ctk.CTkFrame)
        self.assertTrue(hasattr(stats, "refresh"))

        cards = [w for w in stats.winfo_children() if isinstance(w, ctk.CTkFrame)]
        self.assertEqual(len(cards), 3)

        total_card = cards[0]
        body_total = [w for w in total_card.winfo_children() if isinstance(w, ctk.CTkFrame)][1]
        lbl_total = [w for w in body_total.winfo_children() if isinstance(w, ctk.CTkLabel)][0]

        tersedia_card = cards[1]
        body_tersedia = [w for w in tersedia_card.winfo_children() if isinstance(w, ctk.CTkFrame)][1]
        lbl_tersedia = [w for w in body_tersedia.winfo_children() if isinstance(w, ctk.CTkLabel)][0]

        status_card = cards[2]
        body_status = [w for w in status_card.winfo_children() if isinstance(w, ctk.CTkFrame)][1]
        lbl_status = [w for w in body_status.winfo_children() if isinstance(w, ctk.CTkLabel)][0]

        # Biarkan animasi count-up menyelesaikan interpolasi (~350ms)
        for _ in range(25):
            self.root.update()
            time.sleep(0.02)

        self.assertIn("SKU", lbl_total.cget("text"))
        self.assertGreaterEqual(lbl_total._current_numeric_val, 0)

        self.assertIn("Siap", lbl_tersedia.cget("text"))
        self.assertGreaterEqual(lbl_tersedia._current_numeric_val, 0)

        self.assertEqual("Sinkron", lbl_status.cget("text"))

        # Uji refresh dari 0
        stats.refresh(from_zero=True)
        for _ in range(25):
            self.root.update()
            time.sleep(0.02)
        self.assertIn("SKU", lbl_total.cget("text"))
        self.assertIn("Siap", lbl_tersedia.cget("text"))
        self.assertEqual("Sinkron", lbl_status.cget("text"))

    def test_dashboard_stats_csv_refresh_and_empty_file(self):
        """Memverifikasi auto-refresh dashboard stats membaca CSV, menangani file kosong, dan menginterpolasi angka."""
        temp_dir = tempfile.mkdtemp()
        try:
            temp_csv = os.path.join(temp_dir, "test_stats.csv")
            orig_csv = getattr(ui_components, "CSV_PATH", None)
            ui_components.CSV_PATH = temp_csv

            # 1. File kosong / 0 items
            with open(temp_csv, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["nama_barang", "kategori", "kode_sku", "status"])

            stats = buat_dashboard_stats(self.root)
            self.root.update()
            for _ in range(25):
                self.root.update()
                time.sleep(0.02)

            cards = [w for w in stats.winfo_children() if isinstance(w, ctk.CTkFrame)]
            total_card, tersedia_card, status_card = cards[0], cards[1], cards[2]

            body_total = [w for w in total_card.winfo_children() if isinstance(w, ctk.CTkFrame)][1]
            lbl_total = [w for w in body_total.winfo_children() if isinstance(w, ctk.CTkLabel)][0]

            body_tersedia = [w for w in tersedia_card.winfo_children() if isinstance(w, ctk.CTkFrame)][1]
            lbl_tersedia = [w for w in body_tersedia.winfo_children() if isinstance(w, ctk.CTkLabel)][0]

            body_status = [w for w in status_card.winfo_children() if isinstance(w, ctk.CTkFrame)][1]
            lbl_status = [w for w in body_status.winfo_children() if isinstance(w, ctk.CTkLabel)][0]

            self.assertEqual(lbl_total.cget("text"), "0 SKU")
            self.assertEqual(lbl_tersedia.cget("text"), "0 Siap")
            self.assertEqual(lbl_status.cget("text"), "Sinkron")

            # 2. Tambah data barang: 3 barang (2 Tersedia, 1 Habis)
            with open(temp_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Laptop Asus", "Elektronik", "ELE-01", "Tersedia"])
                writer.writerow(["Mouse Gaming", "Elektronik", "ELE-02", "Tersedia"])
                writer.writerow(["Meja Kantor", "Furnitur", "FRN-01", "Habis"])

            stats.refresh(from_zero=True)
            for _ in range(25):
                self.root.update()
                time.sleep(0.02)

            self.assertEqual(lbl_total.cget("text"), "3 SKU")
            self.assertEqual(lbl_tersedia.cget("text"), "2 Siap")
            self.assertEqual(lbl_status.cget("text"), "Sinkron")
        finally:
            if orig_csv:
                ui_components.CSV_PATH = orig_csv
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_dashboard_stats_destroy_cleans_timers(self):
        """Memverifikasi penghancuran stats_container membersihkan seluruh active counter timers tanpa leak."""
        stats = buat_dashboard_stats(self.root)
        self.root.update()

        cards = [w for w in stats.winfo_children() if isinstance(w, ctk.CTkFrame)]
        body_total = [w for w in cards[0].winfo_children() if isinstance(w, ctk.CTkFrame)][1]
        lbl_total = [w for w in body_total.winfo_children() if isinstance(w, ctk.CTkLabel)][0]

        # Trigger refresh agar timer animasi aktif
        stats.refresh(from_zero=True)
        # Hancurkan stats secara langsung
        stats.destroy()
        self.root.update()

        self.assertIsNone(getattr(lbl_total, "_counter_timer", None))

    def test_card_hover_arrow_slide(self):
        card = buat_menu_button(
            self.root,
            "📦 Tambah Barang",
            lambda: None,
            "#10B981"
        )
        self.assertFalse(getattr(card, "is_hover", False))
        arrow_frame = [w for w in card.winfo_children() if isinstance(w, ctk.CTkFrame)][2]
        arrow_lbl = [w for w in arrow_frame.winfo_children() if isinstance(w, ctk.CTkLabel)][0]
        self.assertEqual(getattr(arrow_lbl, "_current_x", 0), 0)

        # Simulasi Hover Enter
        card._on_enter()
        self.assertTrue(getattr(card, "is_hover", False))
        self.assertEqual(card.cget("border_color"), "#10B981")
        for _ in range(12):
            self.root.update()
            time.sleep(0.02)
        self.assertEqual(getattr(arrow_lbl, "_current_x", 0), 5)

        # Simulasi Hover Leave
        card._on_leave()
        self.assertFalse(getattr(card, "is_hover", False))
        self.assertEqual(card.cget("border_color"), BORDER)
        for _ in range(12):
            self.root.update()
            time.sleep(0.02)
        self.assertEqual(getattr(arrow_lbl, "_current_x", 0), 0)

    def test_card_click_press_feedback(self):
        clicked = []
        card = buat_menu_button(
            self.root,
            "📋 Tampil Barang",
            lambda: clicked.append("tampil"),
            "#2563EB"
        )
        card._on_click()
        self.assertEqual(clicked, ["tampil"])
        self.root.update()
        for _ in range(6):
            self.root.update()
            time.sleep(0.02)
        self.assertEqual(card.cget("fg_color"), BG_CARD)

    def test_button_interactive_press_feedback(self):
        clicked = []
        btn = buat_tombol(self.root, "Tombol Uji", lambda: clicked.append(1), "#2563EB")
        self.assertIsInstance(btn, ctk.CTkButton)
        self.root.update()
        btn._canvas.event_generate("<ButtonPress-1>")
        self.root.update()
        self.assertNotEqual(btn.cget("fg_color"), "#2563EB")

        btn._canvas.event_generate("<ButtonRelease-1>")
        self.root.update()
        btn.invoke()
        self.assertEqual(clicked, [1])

    def test_pulsing_status_badge(self):
        hdr = buat_header(self.root, "MENU INVENTARIS GUDANG")
        self.assertIsInstance(hdr, ctk.CTkFrame)
        for _ in range(5):
            self.root.update()
            time.sleep(0.04)
        hdr.destroy()
        self.root.update()

    def test_toast_slide_in_and_dismiss(self):
        toast = show_toast(self.root, "Uji notifikasi animasi", "success", duration_ms=2000)
        self.assertIsNotNone(toast)
        self.assertTrue(toast.winfo_exists())
        self.root.update()

        # Biarkan slide-in berjalan
        for _ in range(10):
            self.root.update()
            time.sleep(0.02)

        self.assertGreater(toast._curr_y, -60)

        # Menampilkan toast baru harus menggantikan toast sebelumnya dengan bersih
        toast2 = tampilkan_toast(self.root, "Uji notifikasi kedua", "info", duration_ms=2000)
        self.assertIsNotNone(toast2)
        self.assertTrue(toast2.winfo_exists())
        self.root.update()

        # Dismiss via tombol tutup (✕)
        btn_close = toast2.winfo_children()[0].winfo_children()[2]
        btn_close.invoke()
        for _ in range(12):
            self.root.update()
            time.sleep(0.02)

        self.assertIsNone(getattr(self.root, "_active_toast", None))

    def test_kpi_cards_click_disabled_and_hover_intact(self):
        """Memverifikasi kartu KPI tidak dapat diklik (tidak merefresh angka), namun hover glow tetap bekerja."""
        stats = buat_dashboard_stats(self.root)
        self.assertIsInstance(stats, ctk.CTkFrame)

        # Pantau apakah refresh() dipanggil saat diklik
        refresh_calls = []
        orig_refresh = stats.refresh
        stats.refresh = lambda *a, **kw: (refresh_calls.append(1), orig_refresh(*a, **kw))

        cards = [w for w in stats.winfo_children() if isinstance(w, ctk.CTkFrame)]
        self.assertEqual(len(cards), 3)

        for card in cards:
            # 1. Kursor tidak boleh 'hand2'
            self.assertNotEqual(card.cget("cursor"), "hand2")

            # 2. Hover enter mengubah warna border dan background
            card._on_enter()
            self.root.update()
            self.assertEqual(card.cget("fg_color"), BG_CARD_HOVER)

            # 3. Klik kartu TIDAK boleh memanggil stats.refresh
            card._canvas.event_generate("<Button-1>")
            self.root.update()
            self.assertEqual(len(refresh_calls), 0)

            # 4. Hover leave mengembalikan warna semula
            card._on_leave()
            self.root.update()
            self.assertEqual(card.cget("fg_color"), BG_CARD)
            self.assertEqual(card.cget("border_color"), BORDER)

    def test_keluar_button_removed_in_submodules(self):
        """Memverifikasi tombol Keluar telah dihilangkan dari window Tambah dan Tampil Barang."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path_tambah = os.path.join(base_dir, "tambah_barang.py")
        path_tampil = os.path.join(base_dir, "tampil_barang.py")

        with open(path_tambah, "r", encoding="utf-8") as f:
            code_tambah = f.read()
        with open(path_tampil, "r", encoding="utf-8") as f:
            code_tampil = f.read()

        # Tombol keluar tidak boleh ada di form tambah_barang
        self.assertNotIn("❌ Keluar", code_tambah)
        self.assertNotIn("root.destroy", code_tambah)
        # Tombol Simpan Barang harus tetap ada
        self.assertIn("💾 Simpan Barang", code_tambah)

        # Tombol keluar tidak boleh ada di footer tampil_barang
        self.assertNotIn("🚪 Keluar", code_tampil)
        # Tombol Refresh Data harus tetap ada
        self.assertIn("🔄 Refresh Data", code_tampil)

    def test_animated_dashboard_ornament_interactions_and_lifecycle(self):
        """Memverifikasi maskot gudang 'Boxy': rendering kanvas, gerakan patroli, interaktivitas klik/hover, dan cleanup."""
        orn = buat_maskot_gudang(self.root)
        self.assertIsInstance(orn, ctk.CTkFrame)
        orn.pack(fill="both", expand=True)
        self.root.update()

        # Biarkan beberapa frame animasi Boxy dieksekusi
        for _ in range(8):
            self.root.update()
            time.sleep(0.02)

        # Temukan kanvas visualizer maskot
        target_canvas = getattr(orn, "canvas", None)
        if target_canvas is None:
            for w in orn.winfo_children():
                if isinstance(w, tk.Canvas):
                    target_canvas = w
                    break
                for sub in w.winfo_children():
                    if isinstance(sub, tk.Canvas):
                        target_canvas = sub
                        break

        self.assertIsNotNone(target_canvas)
        self.assertEqual(orn.get_state(), "idle")

        # Uji hover mouse pada kanvas
        target_canvas.event_generate("<Motion>", x=180, y=35)
        self.root.update()

        # Uji klik langsung pada Boxy (memicu lompat ceria & balon percakapan)
        bx = int(orn.boxy_state["x"])
        by = int(orn.boxy_state["y"])
        target_canvas.event_generate("<Button-1>", x=bx, y=by)
        self.root.update()
        for _ in range(5):
            self.root.update()
            time.sleep(0.02)

        self.assertIn(orn.get_state(), ("jump", "idle"))

        # Uji klik di lantai (memanggil Boxy berjalan ke koordinat X yang diklik)
        floor_x = 140
        target_canvas.event_generate("<Button-1>", x=floor_x, y=55)
        self.root.update()
        self.assertEqual(orn.get_state(), "walk")
        self.assertEqual(orn.boxy_state["target_x"], float(floor_x))

        # Biarkan Boxy melangkah menuju target
        for _ in range(12):
            self.root.update()
            time.sleep(0.02)

        # Temukan tombol aksi interaktif di bilah atas
        action_buttons = [
            getattr(orn, "btn_sapa", None),
            getattr(orn, "btn_paket", None),
            getattr(orn, "btn_tidur", None)
        ]
        self.assertTrue(all(b is not None for b in action_buttons))

        # Uji tombol Sapa (👋)
        btn_sapa = orn.btn_sapa
        btn_sapa.invoke()
        self.root.update()
        self.assertEqual(orn.get_state(), "wave")

        # Uji tombol Bawa Paket (📦)
        btn_paket = orn.btn_paket
        btn_paket.invoke()
        self.root.update()
        self.assertTrue(orn.boxy_state["carrying"])

        # Uji tombol Tidur (💤)
        btn_tidur = orn.btn_tidur
        btn_tidur.invoke()
        self.root.update()
        self.assertEqual(orn.get_state(), "sleep")

        # Uji bangun dari tidur saat mouse digerakkan
        target_canvas.event_generate("<Motion>", x=bx, y=by)
        self.root.update()
        self.assertEqual(orn.get_state(), "idle")

        # Hancurkan widget dan pastikan cleanup timer bersih tanpa error
        orn.destroy()
        self.root.update()

    def test_warehouse_mascot_direct_api_and_features(self):
        """Memverifikasi API publik langsung dan fungsionalitas lanjutan maskot Boxy."""
        mascot = create_warehouse_mascot(self.root)
        self.assertIsInstance(mascot, ctk.CTkFrame)
        mascot.pack(fill="both", expand=True)
        self.root.update()

        # Uji walk_to
        mascot.walk_to(220)
        self.assertEqual(mascot.get_state(), "walk")
        self.assertEqual(mascot.boxy_state["target_x"], 220.0)

        # Uji trigger_jump
        mascot.trigger_jump()
        self.root.update()
        self.assertIn(mascot.get_state(), ("jump", "idle"))

        # Uji toggle_carry
        prev_carrying = mascot.boxy_state["carrying"]
        mascot.toggle_carry()
        self.assertEqual(mascot.boxy_state["carrying"], not prev_carrying)

        # Uji trigger_sleep
        mascot.trigger_sleep()
        self.assertEqual(mascot.get_state(), "sleep")

        # Uji say
        mascot.say("Halo Gudang!")
        self.root.update()

        mascot.destroy()
        self.root.update()

    def test_warehouse_mascot_advanced_interactions_and_edge_cases(self):
        """Memverifikasi penanganan edge case maskot: tidur otomatis, reaksi bangun ceria, pembersihan ripple lantai, dan batas kanvas."""
        mascot = create_warehouse_mascot(self.root)
        mascot.pack(fill="both", expand=True)
        self.root.update()

        # 1. Uji transisi tidur otomatis saat pengguna menganggur (> 240 ticks)
        mascot.boxy_state["user_inactivity_ticks"] = 239
        for _ in range(6):
            self.root.update()
            time.sleep(0.04)
        self.assertEqual(mascot.get_state(), "sleep")

        # 2. Uji klik/senggol pada Boxy saat tidur memicu reaksi bangun ceria (bukan diam)
        mascot.trigger_jump()
        self.root.update()
        self.assertIn(mascot.get_state(), ("jump", "idle"))
        self.assertGreater(mascot.boxy_state["startled_ticks"], 0)

        # 3. Uji pembersihan marker lantai seketika saat pergerakan diinterupsi
        mascot.walk_to(100)
        time.sleep(0.04)
        self.root.update()
        dest_marker_id = None
        for item in mascot.canvas.find_withtag("all"):
            if mascot.canvas.type(item) == "oval" and mascot.canvas.itemcget(item, "outline") == "#F59E0B":
                dest_marker_id = item
                break
        self.assertIsNotNone(dest_marker_id)
        self.assertEqual(mascot.canvas.itemcget(dest_marker_id, "state"), "normal")

        # Interupsi dengan jump -> marker harus langsung hidden
        mascot.trigger_jump()
        self.root.update()
        self.assertEqual(mascot.canvas.itemcget(dest_marker_id, "state"), "hidden")

        # 4. Uji lompatan dan balon percakapan tetap berada di dalam batas kanvas (tidak terpotong di y < 0)
        mascot.say("Semua sistem logistik optimal! 🚀")
        mascot.trigger_jump()
        min_by1 = 999
        for _ in range(25):
            self.root.update()
            time.sleep(0.035)
            min_by1 = min(min_by1, mascot.boxy_state["by1"])
        self.assertGreaterEqual(min_by1, 0)
        self.assertEqual(mascot.boxy_state["jump_y"], 0.0)

        # 5. Uji arah lambaian tangan menyesuaikan arah hadap (facing)
        mascot.boxy_state["facing"] = 1
        mascot.btn_sapa.invoke()
        time.sleep(0.04)
        self.root.update()
        # Saat menghadap kanan, tangan kanan melambai lebih tinggi dari tangan kiri
        arm_l_coords_r = mascot.canvas.coords(mascot.canvas.find_withtag("all")[37])  # arm_l
        arm_r_coords_r = mascot.canvas.coords(mascot.canvas.find_withtag("all")[39])  # arm_r

        mascot.boxy_state["facing"] = -1
        mascot.btn_sapa.invoke()
        time.sleep(0.04)
        self.root.update()
        arm_l_coords_l = mascot.canvas.coords(mascot.canvas.find_withtag("all")[37])  # arm_l
        arm_r_coords_l = mascot.canvas.coords(mascot.canvas.find_withtag("all")[39])  # arm_r
        # Tangan kiri terangkat saat menghadap kiri
        self.assertLess(arm_l_coords_l[3], arm_l_coords_r[3])

        # 6. Uji sol sepatu berdiri tepat di atas garis lantai
        floor_line_y = mascot.canvas.coords(2)[1]
        boot_sole_y = mascot.canvas.coords(30)[1]
        self.assertEqual(boot_sole_y, floor_line_y)

        mascot.destroy()
        self.root.update()

    def test_kpi_card_hover_flicker_protection(self):
        """Memverifikasi hover effect pada kartu KPI tidak flicker saat kursor bergerak di antara sub-widget."""
        stats = buat_dashboard_stats(self.root)
        self.assertIsInstance(stats, ctk.CTkFrame)
        self.root.update()

        cards = [w for w in stats.winfo_children() if isinstance(w, ctk.CTkFrame)]
        self.assertGreaterEqual(len(cards), 1)
        card = cards[0]

        # Hover masuk ke kartu
        card._on_enter()
        self.root.update()
        self.assertEqual(card.cget("fg_color"), BG_CARD_HOVER)

        # Mocking pointerxy berada di dalam kartu
        rx = card.winfo_rootx()
        ry = card.winfo_rooty()
        rw = card.winfo_width()
        rh = card.winfo_height()
        orig_pointerxy = card.winfo_pointerxy
        card.winfo_pointerxy = lambda: (rx + rw // 2, ry + rh // 2)

        try:
            # Pemicuan event <Leave> saat pointer masih di dalam kartu tidak boleh mereset warna
            card._canvas.event_generate("<Leave>")
            self.root.update()
            self.assertEqual(card.cget("fg_color"), BG_CARD_HOVER)

            # Namun saat kursor benar-benar keluar (pointerxy di luar)
            card.winfo_pointerxy = lambda: (rx - 50, ry - 50)
            card._canvas.event_generate("<Leave>")
            self.root.update()
            self.assertEqual(card.cget("fg_color"), BG_CARD)
        finally:
            card.winfo_pointerxy = orig_pointerxy

    def test_ornament_bottom_strip_visibility_and_canvas_geometry(self):
        """Memverifikasi bot_strip ornamen tidak kolaps (h >= 15) dan kanvas memiliki ruang vertikal yang memadai."""
        test_win = ctk.CTk()
        try:
            test_win.geometry("860x660")
            content = ctk.CTkFrame(test_win, fg_color="transparent")
            content.pack(fill="both", expand=True, padx=32, pady=(8, 12))

            stats = buat_dashboard_stats(content)
            m1 = buat_menu_button(content, "📦 Tambah", lambda: None, "#059669")
            m1.pack(fill="x", pady=3)
            m2 = buat_menu_button(content, "📋 Tampil", lambda: None, "#2563EB")
            m2.pack(fill="x", pady=3)
            m3 = buat_menu_button(content, "🚪 Keluar", lambda: None, "#DC2626")
            m3.pack(fill="x", pady=3)

            orn = buat_ornamen_dashboard(content)
            orn.pack(fill="both", expand=True, pady=(6, 0))
            test_win.update()

            # 1. Verifikasi bot_strip teralokasi dengan baik (bukan 1x1 piksel)
            bot_strips = [w for w in orn.winfo_children() if isinstance(w, ctk.CTkFrame)]
            self.assertGreaterEqual(len(bot_strips), 2)
            bot_strip = bot_strips[1]  # Frame kedua setelah top_strip
            self.assertGreaterEqual(bot_strip.winfo_height(), 15)

            # 2. Verifikasi kanvas memiliki tinggi yang proporsional (jauh di atas 14px)
            canvases = []
            for w in orn.winfo_children():
                if isinstance(w, tk.Canvas):
                    canvases.append(w)
                for sub in w.winfo_children():
                    if isinstance(sub, tk.Canvas):
                        canvases.append(sub)
            self.assertGreaterEqual(len(canvases), 1)
            canvas = canvases[0]
            self.assertGreaterEqual(canvas.winfo_height(), 50)

            # 3. Uji event drag <B1-Motion> pada kanvas
            canvas.event_generate("<Button-1>", x=150, y=30)
            canvas.event_generate("<B1-Motion>", x=160, y=30)
            test_win.update()
        finally:
            test_win.destroy()


if __name__ == "__main__":
    unittest.main()

