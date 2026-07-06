import streamlit as st
import pandas as pd
import fitz  # PyMuPDF

st.title("Sistem Cetak PO Otomatis Resi Shopee")

# Upload file
file_pdf = st.file_uploader("Upload PDF Resi Shopee", type=["pdf"])
file_excel = st.file_uploader("Upload Excel (Data_Pesanan_Baru.xlsx)", type=["xlsx"])
keterangan = st.selectbox("Pilih Keterangan", ["-", "Prioritas"])

if st.button("Proses & Siapkan Unduhan"):
    if file_pdf and file_excel:
        try:
            # 1. Baca Excel
            df = pd.read_excel(file_excel)
            df['NO PESANAN'] = df['NO PESANAN'].astype(str).str.strip()
            data_po = dict(zip(df['NO PESANAN'], df['KODE PO']))
            
            # 2. Proses PDF
            doc = fitz.open(stream=file_pdf.read(), filetype="pdf")
            jumlah_berhasil = 0
            
            for page in doc:
                text = page.get_text()
                for no_pesanan, kode_po in data_po.items():
                    if no_pesanan in text:
                        jumlah_berhasil += 1
                        
                        # Pengaturan posisi
                        pos_y = 15
                        ket_text = "" if keterangan == "-" else f" | STATUS: {keterangan.upper()}"
                        teks_utama = f"KODE PO: {kode_po}{ket_text}"
                        
                        # Fontsize 10 agar ringkas
                        fontsize = 10 
                        text_width = fitz.get_text_length(teks_utama, fontname="hebo", fontsize=fontsize)
                        pos_x = (page.rect.width - text_width) / 2
                        
                        # Membuat block putih latar belakang
                        padding_x = 6
                        padding_y = 3
                        rect = fitz.Rect(
                            pos_x - padding_x, 
                            pos_y - 2, 
                            pos_x + text_width + padding_x, 
                            pos_y + fontsize + padding_y
                        )
                        page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
                        
                        # Insert Teks Utama (Tanpa ikon hati)
                        page.insert_text((pos_x, pos_y + fontsize - 2), teks_utama, fontsize=fontsize, fontname="hebo", color=(0, 0, 0), overlay=True)
            
            # 3. Simpan dan Sediakan Tombol Unduh
            output_path = "hasil_resi.pdf"
            doc.save(output_path)
            doc.close()
            
            with open(output_path, "rb") as f:
                st.download_button("Download PDF Hasil", f, "Resi_Selesai.pdf", "application/pdf")
            
            st.success(f"Berhasil! Sebanyak {jumlah_berhasil} resi telah diproses.")
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Mohon untuk upload kedua file terlebih dahulu!")