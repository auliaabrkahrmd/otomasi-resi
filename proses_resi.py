import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

st.title("Sistem Cetak PO Otomatis Resi Shopee")

# Upload file
file_pdf = st.file_uploader("Upload PDF Resi Shopee", type=["pdf"])
file_excel = st.file_uploader("Upload Excel (Data_Pesanan_Baru.xlsx)", type=["xlsx"])
keterangan = st.selectbox("Pilih Keterangan", ["Instan", "Prioritas"])

if st.button("Mulai Proses"):
    if file_pdf and file_excel:
        try:
            # 1. Baca Excel
            df = pd.read_excel(file_excel)
            # Pastikan kolom NO PESANAN dibaca sebagai teks untuk kecocokan akurat
            df['NO PESANAN'] = df['NO PESANAN'].astype(str).str.strip()
            data_po = dict(zip(df['NO PESANAN'], df['KODE PO']))
            
            # 2. Proses PDF
            doc = fitz.open(stream=file_pdf.read(), filetype="pdf")
            ditemukan_counter = 0
            
            for page in doc:
                text = page.get_text()
                page_width = page.rect.width
                
                for no_pesanan, kode_po in data_po.items():
                    if no_pesanan in text:
                        # Definisikan area teks di bagian atas kertas
                        rect = fitz.Rect(10, 10, page_width - 10, 50)
                        teks_hasil = f"PO: {kode_po} | Ket: {keterangan}"
                        
                        # Logika Auto-Font Size
                        fontsize = 20
                        while fontsize > 8:
                            # Hitung lebar teks dan sesuaikan agar tidak keluar kotak
                            text_len = fitz.get_text_length(teks_hasil, fontname="helv-bold", fontsize=fontsize)
                            if text_len < (rect.width - 20):
                                break
                            fontsize -= 1
                        
                        # Tambahkan latar belakang putih agar teks tertutup rapi
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                        
                        # Masukkan teks dengan ukuran yang sudah disesuaikan secara otomatis
                        page.insert_textbox(
                            rect, 
                            teks_hasil, 
                            fontsize=fontsize, 
                            color=(0, 0, 0), 
                            align=1,
                            fontname="helv-bold"
                        )
                        ditemukan_counter += 1
            
            # 3. Simpan dan Sediakan Tombol Unduh
            output_path = "hasil_resi.pdf"
            doc.save(output_path)
            doc.close()
            
            with open(output_path, "rb") as f:
                st.download_button(
                    label="Klik di sini untuk Unduh PDF Hasil", 
                    data=f, 
                    file_name="Resi_Selesai.pdf",
                    mime="application/pdf"
                )
            st.success(f"Proses selesai! Ditemukan {ditemukan_counter} kecocokan.")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {e}")
            st.write("Pastikan file Excel memiliki kolom 'NO PESANAN' dan 'KODE PO'.")
    else:
        st.error("Mohon upload kedua file terlebih dahulu!")