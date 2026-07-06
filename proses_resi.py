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
            
            for page in doc:
                text = page.get_text()
                # Memperbaiki 'or' menjadi 'for' di sini
                for no_pesanan, kode_po in data_po.items():
                    if no_pesanan in text:
                        pos_y = 80
                        
                        # Logika keterangan
                        ket_text = "" if keterangan == "-" else f" | STATUS: {keterangan.upper()}"
                        teks_utama = f"KODE PO: {kode_po}{ket_text}"
                        
                        # FontSize 20 untuk tampilan besar
                        fontsize = 20
                        text_width = fitz.get_text_length(teks_utama, fontname="hebo", fontsize=fontsize)
                        
                        # Posisi X agar teks memenuhi lebar (tengah)
                        pos_x = (page.rect.width - text_width) / 2
                        
                        # Insert Teks Utama
                        page.insert_text((pos_x, pos_y), teks_utama, fontsize=fontsize, fontname="hebo", color=(0, 0, 0), overlay=True)
                        
                        # Jika Prioritas, tambahkan Love hitam di samping kiri dan kanan
                        if keterangan == "Prioritas":
                            page.insert_text((pos_x - 35, pos_y), "♥", fontsize=22, color=(0, 0, 0), overlay=True)
                            page.insert_text((pos_x + text_width + 10, pos_y), "♥", fontsize=22, color=(0, 0, 0), overlay=True)
            
            # 3. Simpan dan Sediakan Tombol Unduh
            output_path = "hasil_resi.pdf"
            doc.save(output_path)
            doc.close()
            
            with open(output_path, "rb") as f:
                st.download_button("Download PDF Hasil", f, "Resi_Selesai.pdf", "application/pdf")
            st.success("Berhasil! Ukuran teks sudah diperbesar dan memenuhi layar.")
            
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Mohon upload kedua file terlebih dahulu!")