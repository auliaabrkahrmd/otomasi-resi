import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
import os

st.title("Sistem Cetak PO Otomatis Resi Shopee")

# Upload file
file_pdf = st.file_uploader("Upload PDF Resi Shopee", type=["pdf"])
file_excel = st.file_uploader("Upload Excel (Data_Pesanan_Baru.xlsx)", type=["xlsx"])
keterangan = st.selectbox("Pilih Keterangan", ["Instan", "Prioritas"])

if st.button("Mulai Proses"):
    if file_pdf and file_excel:
        try:
            # 1. Baca Excel
            df_temp = pd.read_excel(file_excel, header=None)
            header_idx = df_temp[df_temp.apply(lambda row: row.astype(str).str.contains('NO PESANAN').any(), axis=1)].index[0]
            
            df = pd.read_excel(file_excel, header=header_idx)
            df.columns = df.columns.str.strip()
            data_po = df.set_index('NO PESANAN')['KODE PO'].to_dict()
            
            # 2. Proses PDF
            doc = fitz.open(stream=file_pdf.read(), filetype="pdf")
            ditemukan_counter = 0
            
            for page in doc:
                text = page.get_text()
                # Dapatkan ukuran halaman untuk membuat posisi dinamis
                page_rect = page.rect
                page_width = page_rect.width
                
                for no_pesanan, kode_po in data_po.items():
                    if str(no_pesanan) in text:
                        # Membuat posisi dinamis berdasarkan lebar kertas
                        rect = fitz.Rect(10, 10, page_width - 10, 50)
                        
                        teks_hasil = f"PO: {kode_po} | Ket: {keterangan}"
                        
                        # Menambahkan latar belakang putih agar teks terbaca jelas
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                        
                        # Memasukkan teks
                        page.insert_textbox(
                            rect, 
                            teks_hasil, 
                            fontsize=12, 
                            color=(0, 0, 0), 
                            align=1 
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