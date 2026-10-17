"""
models.py - Definisi Data Model Objek (OOP) Sistem Inventaris Gudang.
"""

# Re-ekspor utilitas kategori & status dari ui_components untuk efisiensi modul
from ui_components import KategoriBarang, StatusStok


class Barang:
    """Model data barang dalam inventaris gudang."""

    def __init__(self, nama_barang, kategori, kode_sku, status="Tersedia", jumlah=1, harga=0.0, lokasi=""):
        self.nama_barang = str(nama_barang).strip()
        self.kategori = str(kategori).strip()
        self.kode_sku = str(kode_sku).strip()
        self.status = str(status).strip() if status else "Tersedia"
        try:
            self.jumlah = int(jumlah)
        except (ValueError, TypeError):
            self.jumlah = 1
        try:
            self.harga = float(harga)
        except (ValueError, TypeError):
            self.harga = 0.0
        self.lokasi = str(lokasi).strip()

    def to_list(self):
        """Konversi data barang menjadi representasi list CSV 4-kolom."""
        return [self.nama_barang, self.kategori, self.kode_sku, self.status]

    def to_dict(self):
        """Representasi dictionary."""
        return {
            "nama_barang": self.nama_barang,
            "kategori": self.kategori,
            "kode_sku": self.kode_sku,
            "status": self.status,
            "jumlah": self.jumlah,
            "harga": self.harga,
            "lokasi": self.lokasi
        }

    def __str__(self):
        return f"{self.nama_barang} | {self.kategori} | {self.kode_sku} | {self.status}"


class Petugas:
    """Model data petugas pengelola gudang."""

    def __init__(self, id_petugas, nama, bagian, no_hp):
        self.id = str(id_petugas).strip()
        self.nama = str(nama).strip()
        self.bagian = str(bagian).strip()
        self.no_hp = str(no_hp).strip()

    def to_list(self):
        """Konversi data petugas menjadi list."""
        return [self.id, self.nama, self.bagian, self.no_hp]

    def __str__(self):
        return f"{self.nama} ({self.id}) - Bagian {self.bagian}"