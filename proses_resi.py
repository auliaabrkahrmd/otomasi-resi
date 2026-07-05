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
            # Pastikan NO PESANAN dibaca sebagai string bersih
            df['NO PESANAN'] = df['NO PESANAN'].astype(str).str.strip()
            data_po = dict(zip(df['NO PESANAN'], df['KODE PO']))
            
            # 2. Proses PDF
            doc = fitz.open(stream=file_pdf.read(), filetype="pdf")
            ditemukan_counter = 0
            
            for page in doc:
                # Deteksi ukuran dokumen secara otomatis
                page_width = page.rect.width
                page_height = page.rect.height
                
                text = page.get_text()
                
                for no_pesanan, kode_po in data_po.items():
                    # Cek kecocokan nomor pesanan dalam teks[cite: 2]
                    if no_pesanan in text:
                        # Tentukan area teks (margin 5% dari lebar/tinggi)
                        margin_x = page_width * 0.05
                        margin_y = page_height * 0.02
                        rect = fitz.Rect(margin_x, margin_y, page_width - margin_x, margin_y + 40)
                        
                        teks_hasil = f"PO: {kode_po} | Ket: {keterangan}"
                        
                        # Font size otomatis proporsional dengan lebar kertas
                        fontsize = max(10, int(page_width * 0.06)) 
                        
                        # Tambahkan latar belakang putih dengan overlay=True
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
                        
                        # Masukkan teks dengan overlay=True agar selalu terlihat[cite: 1]
                        page.insert_textbox(
                            rect, 
                            teks_hasil, 
                            fontsize=fontsize, 
                            color=(0, 0, 0), 
                            align=1,
                            fontname="helv",
                            overlay=True 
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
            
            # Notifikasi hasil
            st.success(f"Proses selesai! Ditemukan {ditemukan_counter} kecocokan.")
            if ditemukan_counter == 0:
                st.warning("Perhatian: Tidak ada nomor pesanan yang cocok. Pastikan format teks di PDF dan Excel sama persis.")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {e}")
    else:
        st.error("Mohon upload kedua file terlebih dahulu!")