import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np
from io import BytesIO


# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Kesadaran Keamanan Siber",
    page_icon="📊",
    layout="wide"
)

# Fungsi untuk menentukan kategori
def tentukan_kategori(nilai):
    if nilai > 80:
        return "Sangat Baik"
    elif nilai > 50:
        return "Baik"
    elif nilai > 25:
        return "Kurang Baik"
    else:
        return "Buruk"

# Fungsi untuk memproses file Excel yang diupload
def proses_file_excel(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
        return df, None
    except Exception as e:
        return None, f"Error membaca file Excel: {str(e)}"

# Fungsi untuk membuat grafik index
def create_bar_index(index_value, figsize=(8, 4)):
    fig, ax = plt.subplots(figsize=figsize)

    # Warna dan segmentasi
    color_ranges = [
        (0, 25, '#ec204f', "Buruk" ,'25'),
        (25, 50, '#feed47', "Kurang Baik" , '50'),
        (50, 80, '#8de45f', "Baik", '80'),
        (80, 100, '#2ecf03', "Sangat Baik", '100')
    ]

    center = (0.5, 0.0)
    radius = 0.5

    # Gambar segmen warna
    for start_val, end_val, color, category_label, value_label in color_ranges:
        # 1. Gambar segmen wedge
        wedge = Wedge(center, radius,
                      theta1=180 - (end_val / 100) * 180,
                      theta2=180 - (start_val / 100) * 180,
                      color=color,
                      width=0.2)
        ax.add_patch(wedge)

        # 2. Label kategori (di luar)
        mid_angle = 180 - ((start_val + end_val) / 2 / 100) * 180
        angle_rad = np.radians(mid_angle)
        label_radius = radius * 0.7
        x_cat = center[0] + label_radius * np.cos(angle_rad)
        y_cat = center[1] + label_radius * np.sin(angle_rad)
        rotation = mid_angle - 90
        ax.text(x_cat, y_cat, category_label,
                ha='center', va='center',
                fontsize=14, rotation=rotation)

        # 3. Label nilai di KANAN ATAS LUAR TEPI
        edge_angle = 180 - (end_val / 100) * 180
        edge_rad = np.radians(edge_angle)

        # Posisi kanan atas (adjustment khusus)
        offset_x = 0.0  # Geser horizontal
        offset_y = 0.0  # Geser vertikal
        x_val = center[0] + (radius * 1.0) * np.cos(edge_rad) + (
            offset_x if np.cos(edge_rad) >= 0 else -offset_x
        )
        y_val = center[1] + (radius * 1.0) * np.sin(edge_rad) + (
            offset_y if np.sin(edge_rad) >= 0 else -offset_y
        )

        # Alignment dinamis berdasarkan kuadran
        ha = 'left' if np.cos(edge_rad) >= 0 else 'right'
        va = 'bottom' if np.sin(edge_rad) >= 0 else 'top'

        ax.text(x_val, y_val, value_label,
                ha=ha,
                va=va,
                fontsize=12,
                fontweight='bold',
                color='black')

        ax.text(center[0], center[1] - 0.05, f"{index_value:.2f}",
                ha='center', va='center',
                fontsize=34, fontweight='bold')

        # Parameter jarum
    needle_length = 0.6  # Panjang relatif terhadap radius (0 < x ≤ 1)
    needle_base_width = 0.4  # Lebar pangkal jarum
    needle_tip_width = 0.4 # Lebar ujung jarum

    # Hitung posisi jarum
    angle = np.radians(180 - (index_value / 100) * 180)

    # Titik pangkal (base) jarum
    base_length = radius * 0.01  # Jarak dari pusat
    base_x = center[0] + base_length * np.cos(angle)
    base_y = center[1] + base_length * np.sin(angle)

    # Titik ujung (tip) jarum
    tip_x = center[0] + (radius * needle_length) * np.cos(angle)
    tip_y = center[1] + (radius * needle_length) * np.sin(angle)

    # Gambar jarum dengan bentuk wedge
    ax.annotate("",
                xy=(tip_x, tip_y),  # Ujung jarum
                xytext=(base_x, base_y),  # Pangkal jarum
                arrowprops=dict(
                    arrowstyle="wedge,tail_width={},shrink_factor={}".format(
                        needle_base_width,
                        needle_tip_width / needle_base_width
                    ),
                    color="black",
                    linewidth=0
                ))

    ax.add_patch(plt.Circle(center, 0.03, color='black'))

    ax.set_title('Nilai Rata-Rata Kesadaran Keamanan Siber',
                 fontsize=16, pad=30, loc="center")

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 0.5)
    ax.axis('off')

    return fig

# Fungsi untuk menghitung distribusi kategori
def hitung_distribusi_kategori(df_hasil):
    # Pastikan kolom 'NKI' ada
    if 'NKI' not in df_hasil.columns:
        raise ValueError("DataFrame tidak memiliki kolom 'NKI'")

    # Hitung dengan kondisi terpisah
    sangat_baik = df_hasil[df_hasil['NKI'] > 80]
    baik = df_hasil[(df_hasil['NKI'] > 50) & (df_hasil['NKI'] <= 80)]
    kurang_baik = df_hasil[(df_hasil['NKI'] > 25) & (df_hasil['NKI'] <= 50)]
    buruk = df_hasil[df_hasil['NKI'] <= 25]

    distribusi = {
        'Sangat Baik': len(sangat_baik),
        'Baik': len(baik),
        'Kurang Baik': len(kurang_baik),
        'Buruk': len(buruk)
    }
    return distribusi

# Fungsi untuk membuat pie chart kategori NKI
def create_pie_kategori(distribusi_kategori, figsize=(8, 4)):
    """Buat pie chart yang hanya menampilkan kategori dengan nilai > 0"""
    # Siapkan data, filter kategori dengan nilai > 0
    labels = []
    sizes = []
    colors = []

    # Warna dan label default (sesuaikan dengan kebutuhan)
    color_map = {
        'Sangat Baik': '#4CAF50',
        'Baik': '#8BC34A',
        'Kurang Baik': '#FFC107',
        'Buruk': '#F44336'
    }

    # Filter kategori yang memiliki nilai > 0
    for kategori, nilai in distribusi_kategori.items():
        if nilai > 0:
            labels.append(f"{kategori}\n({nilai} Responden)")  # Contoh: "Baik (15)"
            sizes.append(nilai)
            colors.append(color_map[kategori])

    # Jika tidak ada data sama sekali
    if not sizes:
        st.warning("Tidak ada data untuk ditampilkan")
        return None

    # Buat pie chart
    fig, ax = plt.subplots(figsize=figsize)

    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=labels if len(labels) > 1 else None,  # Sembunyikan label jika hanya 1 kategori
        autopct='%1.1f%%' if len(sizes) > 1 else None,  # Sembunyikan persentase jika hanya 1 kategori
        startangle=90,
        colors=colors,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'},
        textprops={'fontsize': 12}
    )

    # Atur judul
    ax.set_title('Distribusi Kategori Kesadaran Keamanan Siber', pad=20, fontsize=12)

    ax.axis('equal')
    return fig

# Fungsi untuk membuat tabel data responden
def buat_tabel_responden(data, hasil, avg_NKI):
    # 1. Siapkan data untuk DataFrame
    list_responden = []
    for i, row in data.iterrows():
        list_responden.append({
            "No.": i + 1,
            "Nama Responden": row['NAMA'],
            "Asal Instansi": row['INSTANSI'],
            "Nilai Kesadaran Keamanan Siber Individu (NKI)": hasil['NKI'][i],
            "Kategori NKI": tentukan_kategori(hasil['NKI'][i])
        })

    # 2. Buat DataFrame
    df = pd.DataFrame(list_responden)

    # 4. Tampilkan di Streamlit dengan styling
    st.dataframe(
        df,
        column_config={
            "No.": st.column_config.NumberColumn(
                width="60px"
            ),
            "Nama Responden": st.column_config.TextColumn(
                width="200px"
            ),
            "Asal Instansi": st.column_config.TextColumn(
                width="180px"
            ),
            "Nilai Kesadaran Keamanan Siber Individu (NKI)": st.column_config.ProgressColumn(
                format="%.2f%%",
                min_value=0,
                max_value=100,
                width="180px"
            ),
            "Kategori NKI": st.column_config.TextColumn(
                width="160px"
            )
        },
        hide_index=True,
        use_container_width=True
    )

# Fungsi untuk membuat bar variabel
def create_bar_variabel(avg_nkkst, avg_nkkss, figsize=(6, 5)):
    fig, ax = plt.subplots(figsize=figsize)

    # Posisi bar di x-axis (lebih rapat)
    x_pos = [0.4, 1.0]  # Mengurangi jarak dari default [0,1]

    colors = ['blue', 'red']  # Biru dan Oranye
    bars = ax.bar(x_pos, [avg_nkkst, avg_nkkss],
                  width=0.5,  # Lebar bar diperbesar
                  color=colors,
                  alpha=0.7)

    # Styling
    ax.set_xticks(x_pos)
    ax.set_title('Perbandingan Rata-Rata Nilai Kesadaran Keamanan Siber\nBerdasarkan Fokus Area',
                 fontsize=14, pad=50, loc="left")
    ax.set_xticklabels(['Keamanan Siber Teknis', 'Keamanan Siber Sosial'], fontsize=10)
    ax.set_ylim(0, max(avg_nkkst, avg_nkkss) * 1.2)

    # Tambahkan nilai di atas bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height,
                f'{height:.2f}',
                ha='center', va='bottom', fontsize=14)

    # Hapus garis tepi dan tambah grid
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    ax.grid(axis='y', color='gray', linestyle='--', linewidth=0.5)
    ax.set_ylim(0, 100)

    return fig

# Fungsi untuk membuat bar chart NKKST
def create_bar_chart_NKKST(categories, values, color='blue', figsize=(6, 4)):
    fig, ax = plt.subplots(figsize=figsize)

    # Mapping nama lengkap indikator
    indicator_descriptions = {
        'SK':'Syarat & Ketentuan Instalasi',
        'KS':'Kata Sandi',
        'IW':'Internet & WiFi',
        'KP':'Keamanan Perangkat',
        'AT':'Aduan Insiden Siber Teknis',
        'HT':'Hukum & Regulasi Keamanan Siber Teknis'
    }

    # Membuat bar chart
    bars = ax.bar(categories, values, color=color, alpha=0.7)


    # Menambahkan nilai di atas bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=12)

    # Grid dan styling
    ax.set_ylim(0, 100)
    ax.grid(axis='y', color='gray', linestyle='--', linewidth=0.5)

    # Title dan label
    ax.set_title('Perbandingan Rata-Rata Nilai Kesadaran Keamanan Siber\nBerdasarkan Fokus Area Keamanan Siber Teknis', loc='left', fontsize=12, pad=50)
    ax.set_xlabel('Indikator')
    ax.set_ylabel('Nilai')
    ax.spines['top'].set_visible(False)

    # Membuat legenda kustom
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w',
                   label=f'{cat} = {indicator_descriptions[cat]}',
                   markerfacecolor=color, markersize=10)
        for cat in categories
    ]

    # Menambahkan legenda di sebelah kanan
    ax.legend(
        handles=legend_elements,
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        frameon=False,
        fontsize=8
    )

    plt.tight_layout()
    return fig

# Fungsi untuk membuat bar chart NKKSS
def create_bar_chart_NKKSS(categories, values, color='red', figsize=(6, 4)):
    fig, ax = plt.subplots(figsize=figsize)
    # Mapping nama lengkap indikator
    indicator_descriptions = {
        'RS':'Rekayasa Sosial',
        'KN':'Konten Negatif',
        'AM':'Aktivitas Media Sosial',
        'AS':'Aduan Insiden Siber Sosial',
        'HS':'Hukum & Regulasi Keamanan Siber Sosial'
    }

    # Membuat bar chart
    bars = ax.bar(categories, values, color=color, alpha=0.7)
    # Menambahkan nilai di atas bar
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}',
                ha='center', va='bottom', fontsize=12)

    # Grid dan styling
    ax.set_ylim(0, 100)
    ax.grid(axis='y', color='gray', linestyle='dashed', linewidth=0.5)

    # Title dan label
    ax.set_title('Perbandingan Rata-Rata Nilai Kesadaran Keamanan Siber\nBerdasarkan Fokus Area Keamanan Siber Sosial', loc='left', fontsize=12, pad=50)
    ax.set_xlabel('Indikator')
    ax.set_ylabel('Nilai')
    ax.spines['top'].set_visible(False)
    # Membuat legenda kustom
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='w',
                   label=f'{cat} = {indicator_descriptions[cat]}',
                   markerfacecolor=color, markersize=10)
        for cat in categories
    ]

    # Menambahkan legenda di sebelah kanan
    ax.legend(
        handles=legend_elements,
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        frameon=False,
        fontsize=8
    )

    plt.tight_layout()
    return fig

# Fungsi untuk membuat grafik jenis kelamin
def create_pie_kelamin(df, jenis_kelamin_col="JENIS KELAMIN"):
    # Preprocessing data
    df[jenis_kelamin_col] = df[jenis_kelamin_col].str.upper().str.strip()

    # Handle missing values dan standardisasi nilai
    df[jenis_kelamin_col] = df[jenis_kelamin_col].replace({
        'L': 'Laki-Laki',
        'LAKI2': 'Laki-Laki',
        'PRIA': 'Laki-Laki',
        'P': 'Perempuan',
        'WANITA': 'Perempuan'
    }).fillna('Tidak Ada Data')

    # Hitung distribusi
    distribusi = df[jenis_kelamin_col].value_counts()
    total = distribusi.sum()

    # Buat figure dengan ukuran lebih proporsional
    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=100)

    # Warna dan label
    colors = ['#25C4F8', '#F354A9', '#A9A9A9']  # Biru, Pink, Abu-abu (untuk data kosong)
    labels = distribusi.index

    # Fungsi untuk menampilkan jumlah dan persentase
    def format_label(pct):
        absolute = int(round(pct / 100. * total))
        return f"{absolute}"

    # Buat pie chart
    wedges, texts, autotexts = ax.pie(
        distribusi,
        labels=labels,
        autopct=format_label,
        startangle=90,
        colors=colors[:len(distribusi)],
        textprops={'fontsize': 14, 'color': 'black'},
        pctdistance=0.75,
        wedgeprops={'linewidth': 1, 'edgecolor': 'white'}
    )

    # Atur style teks
    plt.setp(autotexts, size=14)
    plt.setp(texts, size=10)

    # Tambahkan judul
    ax.set_title('Distribusi Jenis Kelamin Responden',
                 pad=20, fontsize=14, loc='center')

    # Tambahkan total responden di tengah (donut chart)
    centre_circle = plt.Circle((0, 0), 0.6, color='white')
    ax.add_artist(centre_circle)
    ax.text(0, 0, f"Total:\n{total} Responden",
            ha='center', va='center',
            fontsize=12)

    # Atur layout
    plt.tight_layout()
    ax.axis('equal')  # Pastikan pie tetap lingkaran

    return fig

# Fungsi untuk membuat grafik umur
def create_bar_umur(df, umur_col="UMUR"):
    # Hitung distribusi umur dan urutkan
    distribusi = df[umur_col].value_counts().sort_values(ascending=True)

    # Buat figure
    fig, ax = plt.subplots(figsize=(8, 4.8))

    # Warna untuk bar chart
    color = '#53E8D4'  # Warna biru standar

    # Buat horizontal bar chart
    bars = ax.barh(
        distribusi.index.astype(str),  # Kategori umur sebagai string
        distribusi.values,  # Jumlah responden
        color=color,
        height=0.6  # Tinggi bar
    )

    # Tambahkan jumlah responden di ujung setiap bar
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5,  # Posisi x (jumlah + sedikit spacing)
                bar.get_y() + bar.get_height() / 2,  # Posisi y di tengah bar
                f'{int(width)}',  # Teks yang ditampilkan
                va='center',  # Vertikal alignment
                ha='left',  # Horizontal alignment
                fontsize=10)

    # Atur sumbu x dengan interval 2
    max_count = distribusi.max()
    ax.set_xticks(np.arange(0, max_count + 3, 2))  # +3 untuk memastikan cukup
    ax.set_xticklabels([str(int(x)) for x in np.arange(0, max_count + 3, 2)])

    # Atur label dan judul
    ax.set_xlabel('Jumlah Responden', fontsize=12)
    ax.set_title('Distribusi Umur Responden', pad=20, fontsize=14, loc='left')

    # Hilangkan spines (garis tepi) yang tidak perlu
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Atur grid untuk memudahkan pembacaan
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    # Auto adjust layout
    plt.tight_layout()

    return fig

# Fungsi untuk membuat grafik tingkat pendidikan
def create_bar_pendidikan(df, pendidikan_col="TINGKAT PENDIDIKAN"):
    # Hitung distribusi umur dan urutkan
    distribusi = df[pendidikan_col].value_counts().sort_values(ascending=True)

    # Buat figure
    fig, ax = plt.subplots(figsize=(8, 4.8))

    # Warna untuk bar chart
    color = '#F0533C'  # Warna biru standar

    # Buat horizontal bar chart
    bars = ax.barh(
        distribusi.index.astype(str),  # Kategori umur sebagai string
        distribusi.values,  # Jumlah responden
        color=color,
        height=0.6  # Tinggi bar
    )

    # Tambahkan jumlah responden di ujung setiap bar
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5,  # Posisi x (jumlah + sedikit spacing)
                bar.get_y() + bar.get_height() / 2,  # Posisi y di tengah bar
                f'{int(width)}',  # Teks yang ditampilkan
                va='center',  # Vertikal alignment
                ha='left',  # Horizontal alignment
                fontsize=10)

    # Atur sumbu x dengan interval 2
    max_count = distribusi.max()
    ax.set_xticks(np.arange(0, max_count + 3, 2))  # +3 untuk memastikan cukup
    ax.set_xticklabels([str(int(x)) for x in np.arange(0, max_count + 3, 2)])

    # Atur label dan judul
    ax.set_xlabel('Jumlah Responden', fontsize=12)
    ax.set_title('Distribusi Tingkat Pendidikan Responden', pad=20, fontsize=14, loc='left')

    # Hilangkan spines (garis tepi) yang tidak perlu
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Atur grid untuk memudahkan pembacaan
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    # Auto adjust layout
    plt.tight_layout()

    return fig

# Fungsi untuk membuat grafik domisili
def create_bar_domisili(df, domisili_col="PROVINSI"):
    # Hitung distribusi umur dan urutkan
    distribusi = df[domisili_col].value_counts().sort_values(ascending=True)

    # Buat figure
    fig, ax = plt.subplots(figsize=(8, 4.8))

    # Warna untuk bar chart
    color = '#8921C2'  # Warna biru standar

    # Buat horizontal bar chart
    bars = ax.barh(
        distribusi.index.astype(str),  # Kategori umur sebagai string
        distribusi.values,  # Jumlah responden
        color=color,
        height=0.6  # Tinggi bar
    )

    # Tambahkan jumlah responden di ujung setiap bar
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5,  # Posisi x (jumlah + sedikit spacing)
                bar.get_y() + bar.get_height() / 2,  # Posisi y di tengah bar
                f'{int(width)}',  # Teks yang ditampilkan
                va='center',  # Vertikal alignment
                ha='left',  # Horizontal alignment
                fontsize=10)

    # Atur sumbu x dengan interval 2
    max_count = distribusi.max()
    ax.set_xticks(np.arange(0, max_count + 3, 2))  # +3 untuk memastikan cukup
    ax.set_xticklabels([str(int(x)) for x in np.arange(0, max_count + 3, 2)])

    # Atur label dan judul
    ax.set_xlabel('Jumlah Responden', fontsize=12)
    ax.set_title('Distribusi Domisili Responden', pad=20, fontsize=14, loc='left')

    # Hilangkan spines (garis tepi) yang tidak perlu
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Atur grid untuk memudahkan pembacaan
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    # Auto adjust layout
    plt.tight_layout()

    return fig

# Fungsi untuk membuat file Excel yang bisa didownload
def create_excel_download(df_teknis, df_nkkst, df_sosial, df_nkkss, df_nki):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Tulis setiap DataFrame ke sheet yang sama dengan jarak
        start_row = 0
        df_teknis.to_excel(writer, sheet_name='Hasil Penilaian', index=False, startrow=start_row)
        start_row += len(df_teknis) + 2
        df_nkkst.to_excel(writer, sheet_name='Hasil Penilaian', index=False, startrow=start_row)
        start_row += len(df_nkkst) + 2
        df_sosial.to_excel(writer, sheet_name='Hasil Penilaian', index=False, startrow=start_row)
        start_row += len(df_sosial) + 2
        df_nkkss.to_excel(writer, sheet_name='Hasil Penilaian', index=False, startrow=start_row)
        start_row += len(df_nkkss) + 2
        df_nki.to_excel(writer, sheet_name='Hasil Penilaian', index=False, startrow=start_row)

        # Formatting
        workbook = writer.book
        worksheet = writer.sheets['Hasil Penilaian']

        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })

        number_format = workbook.add_format({'num_format': '0.00'})

        # Terapkan format ke semua tabel
        for tbl in [df_teknis, df_nkkst, df_sosial, df_nkkss, df_nki]:
            for col_num, value in enumerate(tbl.columns.values):
                worksheet.write(tbl.index.start, col_num, value, header_format)

        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 15, number_format)
        worksheet.set_column('C:C', 20)

    output.seek(0)
    return output

# Fungsi untuk menghitung nilai responden
def hitung_nilai_responden(df, row_index) :
    # [MASUKKAN SEMUA KODE MAPPING DAN PERHITUNGAN DI SINI]
    # SKTOTAL
    map_SK1 = {
        "Saya tidak membacanya": 1,
        "Saya hanya membaca pada poin penting": 2,
        "Saya membacanya sekilas": 3,
        "Saya membacanya dengan teliti": 4
    }
    map_SK2 = {
        "Saya mengizinkannya walaupun tidak memahami risikonya": 1,
        "Saya tidak mengizinkannya karena tidak memahami risikonya": 2,
        "Saya tidak mengizinkannya karena ragu terhadap keamanan risikonya": 3,
        "Saya mengizinkannya dengan memahami risikonya": 4
    }
    # KSTOTAL
    map_KS1 = {
        "Saya mengabaikannya": 1,
        "Saya menggunakan salah satu kombinasi": 2,
        "Saya menggunakan beberapa kombinasi": 3,
        "Saya menggunakan seluruh kombinasi": 4
    }
    map_KS2 = {
        "Saya membagikan password seluruh akun yang saya miliki": 1,
        "Saya membagikan password hanya kepada orang yang saya percayai": 2,
        "Saya membagikannya ketika hanya ada urgensi": 3,
        "Saya tidak pernah membagikan password akun kepada siapapun": 4
    }
    map_KS3 = {
        "Tidak sama sekali": 1,
        "Jika saya ingat saja": 2,
        "Ya, setiap setahun sekali": 3,
        "Ya, setiap tiga bulan sekali": 4
    }
    map_KS4 = {
        "Saya tidak menyimpan password saya": 1,
        "Saya tidak menyimpannya pada aplikasi penyimpan password": 2,
        "Saya menyimpannya pada aplikasi penyimpan password meskipun tidak tepercaya": 3,
        "Saya menyimpannya pada aplikasi yang tepercaya": 4
    }
    map_KS5 = {
        "Setiap akun digital saya memiliki password yang sama": 1,
        "Beberapa akun digital saya memiliki password yang sama": 2,
        "Satu sampai dua akun digital saya memiliki password yang sama": 3,
        "Setiap akun digital saya memiliki password yang berbeda-beda": 4
    }
    map_KS6 = {
        "Saya tidak mengetahuinya": 1,
        "Saya tidak mengaktifkannya": 2,
        "Saya mengaktifkannya jika tidak mengunduh aplikasi tambahan": 3,
        "Saya mengaktifkannya walaupun harus menggunakan aplikasi tambahan": 4
    }
    # IWTOTAL
    map_IW1 = {
        "Saya tidak menyadari risikonya": 1,
        "Saya menyadari risikonya tetapi tetap mengekliknya": 2,
        "Saya menyadari risikonya dan mengabaikan tautannya": 3,
        "Saya menyadari risikonya dan mengecek validitas sumbernya": 4
    }
    map_IW2 = {
        "Saya tidak menyadari risikonya sama sekali": 1,
        "Saya tidak terlalu menyadari risikonya": 2,
        "Saya menyadari risikonya tetapi saya tidak peduli": 3,
        "Saya sangat menyadari risikonya dan selalu waspada": 4
    }
    map_IW3 = {
        "Saya sering mengunjungi situs yang mencurigakan": 1,
        "Saya kadang-kadang mengunjungi situs yang mencurigakan": 2,
        "Saya jarang mengunjungi situs yang mencurigakan secara tidak sengaja": 3,
        "Saya tidak pernah mengunjungi situs yang mencurigakan": 4
    }
    map_IW4 = {
        "Saya selalu menggunakan jaringan publik": 1,
        "Saya sering menggunakan jaringan publik": 2,
        "Saya kadang-kadang menggunakan jaringan publik": 3,
        "Saya tidak pernah menggunakan jaringan publik": 4
    }
    map_IW5 = {
        "Saya tidak pernah memastikannya": 1,
        "Saya kadang-kadang memastikannya": 2,
        "Saya sering memastikannya": 3,
        "Saya selalu memastikannya": 4
    }
    # KPTOTAL
    map_KP1 = {
        "Saya tidak pernah melakukan update software": 1,
        "Saya jarang melakukan update software": 2,
        "Saya melakukan update secara berkala terutama saat menerima pemberitahuan": 3,
        "Saya selalu melakukan update software secara rutin": 4
    }
    map_KP2 = {
        "Saya tidak pernah memasang antivirus pada perangkat digital": 1,
        "Saya mengandalkan perlindungan bawaan dari sistem operasi": 2,
        "Saya hanya memasang antivirus pada beberapa perangkat digital saya tergantung kebutuhan dan aktivitas online saya": 3,
        "Saya selalu memasang antivirus pada semua perangkat digital saya": 4
    }
    map_KP3 = {
        "Saya selalu mengunduh aplikasi dari penyedia yang tidak resmi": 1,
        "Saya terkadang mengunduh aplikasi dari sumber yang tidak resmi ketika aplikasi tersebut tidak tersedia dari penyedia resmi": 2,
        "Saya beberapa kali mengunduh aplikasi dari penyedia aplikasi resmi": 3,
        "Saya hanya mengunduh aplikasi dari penyedia aplikasi resmi seperti Google Play Store atau Apple Store": 4
    }
    map_KP4 = {
        "Saya tidak pernah melakukan update antivirus": 1,
        "Saya jarang melakukan update antivirus": 2,
        "Saya melakukan update secara berkala terutama saat menerima pemberitahuan": 3,
        "Saya selalu melakukan update antivirus secara rutin": 4
    }
    map_KP5 = {
        "Saya tidak mengetahui mengenai pengaturan penonaktifkan posisi geografis": 1,
        "Saya mengaktifkan posisi geografis perangkat digital": 2,
        "Saya menonaktifkan posisi geografis perangkat saya dalam situasi tertentu": 3,
        "Saya selalu menonaktifkan posisi geografis perangkat saya ketika tidak digunakan": 4
    }
    map_KP6 = {
        "Saya tidak pernah melakukan backup data": 1,
        "Saya jarang melakukan backup data": 2,
        "Saya melakukan backup data secara berkala terutama saat menerima pemberitahuan": 3,
        "Saya selalu melakukan backup data secara rutin": 4
    }
    # ATTOTAL
    map_AT1 = {
        "Saya tidak mengetahui sama sekali pihak berwenang dalam penanganan insiden siber": 1,
        "Saya hanya mengetahui beberapa pihak berwenang dalam penanganan insiden siber": 2,
        "Saya mengetahui semua pihak berwenang dalam penanganan insiden siber, namun tidak tahu cara menghubunginya": 3,
        "Saya mengetahui semua pihak berwenang dalam penanganan insiden siber dan tahu cara menghubunginya": 4
    }
    map_AT2 = {
        "Saya tidak melaporkannya kepada pihak berwenang": 1,
        "Saya ragu untuk melaporkannya kepada pihak berwenang karena tidak yakin akan ditindak": 2,
        "Saya menunda melaporkannya kepada pihak berwenang karena mencoba menyelesaikannya sendiri": 3,
        "Saya langsung melaporkannya kepada pihak berwenang": 4
    }
    map_AT3 = {
        "Saya tidak mengetahui BSSN memiliki layanan aduan siber": 1,
        "Saya pernah mendengar BSSN memiliki layanan aduan siber": 2,
        "Saya mengetahui namun tidak paham mekanisme pelaporan layanan aduan siber BSSN": 3,
        "Saya mengetahui dan paham mekanisme pelaporan layanan aduan siber BSSN": 4
    }
    # HTTOTAL
    map_HT1 = {
        "Saya tidak tahu pemerintah memiliki aturan tersebut": 1,
        "Saya pernah mendengar pemerintah memiliki aturan tersebut": 2,
        "Saya tidak tahu secara detail": 3,
        "Saya tahu secara detail": 4
    }
    map_HT2 = {
        "Saya pernah melakukannya walaupun tahu jika itu dilarang": 1,
        "Saya pernah melakukan karena tidak mengetahui jika itu dilarang": 2,
        "Saya tidak pernah melakukannya namun tidak tahu jika itu dilarang": 3,
        "Saya tidak pernah melakukan karena saya tahu itu dilarang": 4
    }

    # RSTOTAL
    map_RS1 = {
        "Saya tidak menyadari dan tidak mengetahui adanya penipuan online": 1,
        "Saya tidak menyadari adanya praktik tersebut namun mengetahui adanya penipuan online": 2,
        "Saya sadar tapi kurang berhati-hati dalam berinteraksi online": 3,
        "Saya sadar dan selalu berhati-hati dalam berinteraksi online": 4
    }
    map_RS2 = {
        "Saya selalu berbagi informasi pribadi": 1,
        "Saya sering berbagi informasi pribadi": 2,
        "Saya jarang membagikan informasi pribadi": 3,
        "Saya tidak pernah membagikan informasi pribadi": 4
    }
    map_RS3 = {
        "Saya tidak mengerti dan tidak peduli": 1,
        "Saya tidak mengerti hal tersebut penting bagi data saya": 2,
        "Saya mengerti hal tersebut penting tapi tidak tahu manfaatnya": 3,
        "Saya mengerti hal tersebut penting demi mencegah manipulasi data": 4
    }
    map_RS4 = {
        "Saya tidak pernah melakukan pengecekan": 1,
        "Saya jarang melakukan pengecekan": 2,
        "Saya sering melakukan pengecekan": 3,
        "Saya selalu melakukan pengecekan": 4
    }
    map_RS5 = {
        "Saya tidak minat dengan keamanan siber": 1,
        "Saya tidak minat namun mengetahui ancamannya": 2,
        "Saya berupaya namun tidak selalu meningkatkan literasi keamanan siber": 3,
        "Saya berupaya dan selalu meningkatkan literasi keamanan siber": 4
    }
    map_RS6 = {
        "Saya tidak mengetahui definisinya maupun bentuk praktik rekayasa sosial": 1,
        "Saya hanya mengetahui definisinya namun tidak mengetahui bentuk praktik rekayasa sosial": 2,
        "Saya mengetahui bentuk praktik rekayasa sosial hanya pada beberapa media": 3,
        "Saya mengetahui bentuk praktik rekayasa sosial pada media apapun": 4
    }
    # KNTOTAL
    map_KN1 = {
        "Saya selalu menyebarkannya": 1,
        "Saya sering menyebarkannya": 2,
        "Saya jarang menyebarkannya": 3,
        "Saya tidak pernah menyebarkannya": 4
    }
    map_KN2 = {
        "Saya langsung percaya dan langsung meneruskannya kebenaran informasi tersebut": 1,
        "Saya tidak langsung percaya dan tidak memastikan kebenaran informasi tersebut": 2,
        "Saya tidak langsung percaya dan memastikan kebenaran informasi tersebut": 3,
        "Saya tidak langsung percaya, memastikannya dan meneruskan kebenaran informasi tersebut": 4
    }
    map_KN3 = {
        "Saya selalu menyebarkannya": 1,
        "Saya sering menyebarkannya": 2,
        "Saya jarang menyebarkannya": 3,
        "Saya tidak pernah menyebarkannya": 4
    }
    # AMTOTAL
    map_AM1 = {
        "Saya tidak mengetahui mengenai pengaturan privasi pada media sosial": 1,
        "Saya tidak mengaktifkan pengaturan privasi pada media sosial": 2,
        "Saya mengaktifkan pengaturan privasi pada media sosial saya dalam situasi tertentu": 3,
        "Saya selalu mengaktifkan pengaturan privasi pada media sosial saya": 4
    }
    map_AM2 = {
        "Saya selalu membagikannya": 1,
        "Saya sering membagikannya": 2,
        "Saya jarang membagikannya": 3,
        "Saya tidak pernah membagikannya": 4
    }
    map_AM3 = {
        "Saya tidak peduli": 1,
        "Saya merasa perlu namun belum melakukan sepenuhnya": 2,
        "Saya sudah melakukannya": 3,
        "Saya sudah melakukannya dan mengingatkan orang lain untuk bersikap positif": 4
    }
    map_AM4 = {
        "Saya tidak menyadari dampak negatifnya dan berlebihan menggunakan media sosial": 1,
        "Saya tidak menyadari dampak negatifnya dan banyak menggunakan media sosial": 2,
        "Saya menyadari dampak negatifnya namun banyak menggunakan media sosial": 3,
        "Saya menyadari dampak negatifnya dan menggunakan media sosial dengan bijak": 4
    }
    map_AM5 = {
        "Saya merasa tidak perlu melakukannya": 1,
        "Saya merasa perlu namun belum melakukannya": 2,
        "Saya sudah melakukannya namun hanya kepada orang yang saya kenal": 3,
        "Saya sudah melakukannya": 4
    }
    # ASTOTAL
    map_AS1 = {
        "Saya tidak mengetahui sama sekali pihak berwenang dalam penanganan konten negatif": 1,
        "Saya hanya mengetahui beberapa pihak berwenang dalam penanganan konten negatif": 2,
        "Saya mengetahui semua pihak berwenang dalam penanganan konten negatif, namun tidak tahu cara menghubunginya": 3,
        "Saya mengetahui semua pihak berwenang dalam penanganan konten negatif dan tahu cara menghubunginya": 4
    }
    map_AS2 = {
        "Saya tidak pernah melaporkannya": 1,
        "Saya jarang melaporkannya": 2,
        "Saya sering melaporkannya": 3,
        "Saya selalu melaporkannya": 4
    }
    map_AS3 = {
        "Saya tidak mengetahui BSSN memiliki layanan Lapor Konten": 1,
        "Saya pernah mendengar BSSN memiliki layanan Lapor Konten": 2,
        "Saya mengetahui namun tidak paham mekanisme layanan Lapor Konten BSSN": 3,
        "Saya mengetahui dan paham mekanisme layanan Lapor Konten BSSN": 4
    }
    # HSTOTAL
    map_HS1 = {
        "Saya tidak tahu pemerintah memiliki aturan tersebut": 1,
        "Saya pernah mendengar pemerintah memiliki aturan tersebut": 2,
        "Saya tidak tahu secara detail": 3,
        "Saya tahu secara detail": 4
    }
    map_HS2 = {
        "Saya tidak peduli dengan hal tersebut": 1,
        "Saya tidak percaya pihak berwenang akan menegakkan aturan tersebut": 2,
        "Saya hanya mempercayai sebagian pihak berwenang akan menegakkan aturan tersebut": 3,
        "Saya percaya seluruh pihak berwenang akan menegakkan aturan tersebut": 4
    }

    maps = {
        'SK': [map_SK1, map_SK2],
        'KS': [map_KS1, map_KS2, map_KS3, map_KS4, map_KS5, map_KS6],
        'IW': [map_IW1, map_IW2, map_IW3, map_IW4, map_IW5],
        'KP': [map_KP1, map_KP2, map_KP3, map_KP4, map_KP5, map_KP6],
        'AT': [map_AT1, map_AT2, map_AT3],
        'HT': [map_HT1, map_HT2],
        'RS': [map_RS1, map_RS2, map_RS3, map_RS4, map_RS5, map_RS6],
        'KN': [map_KN1, map_KN2, map_KN3],
        'AM': [map_AM1, map_AM2, map_AM3, map_AM4, map_AM5],
        'AS': [map_AS1, map_AS2, map_AS3],
        'HS': [map_HS1, map_HS2],
    }

    # Ambil jawaban dari dataframe
    jawaban = [df.iloc[row_index, i] for i in
               [9, 11, 13, 14, 16, 18, 20, 22, 24, 25, 27, 28, 30, 32, 34, 35, 37, 39, 41, 43, 44, 45, 46, 47,
                49, 50, 51, 52, 53, 55, 57, 58, 59, 61, 62, 63, 64, 65, 67, 68, 69, 70, 71]]

    # Hitung skor untuk setiap kategori
    sk_scores = {'sk' + str(i + 1): maps['SK'][i].get(jawaban[i], 0) for i in range(2)}
    ks_scores = {'ks' + str(i + 1): maps['KS'][i].get(jawaban[i + 2], 0) for i in range(6)}
    iw_scores = {'iw' + str(i + 1): maps['IW'][i].get(jawaban[i + 8], 0) for i in range(5)}
    kp_scores = {'kp' + str(i + 1): maps['KP'][i].get(jawaban[i + 13], 0) for i in range(6)}
    at_scores = {'at' + str(i + 1): maps['AT'][i].get(jawaban[i + 19], 0) for i in range(3)}
    ht_scores = {'ht' + str(i + 1): maps['HT'][i].get(jawaban[i + 22], 0) for i in range(2)}
    rs_scores = {'rs' + str(i + 1): maps['RS'][i].get(jawaban[i + 24], 0) for i in range(6)}
    kn_scores = {'kn' + str(i + 1): maps['KN'][i].get(jawaban[i + 30], 0) for i in range(3)}
    am_scores = {'am' + str(i + 1): maps['AM'][i].get(jawaban[i + 33], 0) for i in range(5)}
    as_scores = {'as' + str(i + 1): maps['AS'][i].get(jawaban[i + 38], 0) for i in range(3)}
    hs_scores = {'hs' + str(i + 1): maps['HS'][i].get(jawaban[i + 41], 0) for i in range(2)}

    # Hitung total nilai per indikator
    hasil = {
        'SKTOTAL' : round((sum(sk_scores.values()) / 8) * 100, 2),
        'KSTOTAL' : round((sum(ks_scores.values()) / 24) * 100, 2),
        'IWTOTAL' : round((sum(iw_scores.values()) / 20) * 100, 2),
        'KPTOTAL' : round((sum(kp_scores.values()) / 24) * 100, 2),
        'ATTOTAL' : round((sum(at_scores.values()) / 12) * 100, 2),
        'HTTOTAL' : round((sum(ht_scores.values()) / 8) * 100, 2),
        'RSTOTAL' : round((sum(rs_scores.values()) / 24) * 100, 2),
        'KNTOTAL' : round((sum(kn_scores.values()) / 12) * 100, 2),
        'AMTOTAL' : round((sum(am_scores.values()) / 20) * 100, 2),
        'ASTOTAL' : round((sum(as_scores.values()) / 12) * 100, 2),
        'HSTOTAL' : round((sum(hs_scores.values()) / 8) * 100, 2),
    }

    # Hitung nilai rata-rata
    hasil['NKKST'] = round((hasil['SKTOTAL'] + hasil['KSTOTAL'] + hasil['IWTOTAL'] + hasil['KPTOTAL'] + hasil['ATTOTAL'] + hasil['HTTOTAL']) / 6, 2)
    hasil['NKKSS'] = round((hasil['RSTOTAL'] + hasil['KNTOTAL'] + hasil['AMTOTAL'] + hasil['ASTOTAL'] + hasil['HSTOTAL']) / 5, 2)
    hasil['NKI'] = round((hasil['NKKST'] + hasil['NKKSS']) / 2, 2)

    return hasil

# Fungsi untuk menghitung semua responden
def hitung_semua_responden(df):
    hasil_responden = []
    for i in range(len(df)):
        hasil = hitung_nilai_responden(df, i)
        hasil_responden.append(hasil)

    df_hasil = pd.DataFrame(hasil_responden)

    # Tambahkan kolom ID responden jika perlu
    if not df.empty:
        df_hasil.insert(0, 'Responden_ID', df.iloc[:, 0])

    return df_hasil

def main():
    st.title('📊 Dashboard Penilaian Kesadaran Keamanan Siber')

    # Step 1: Upload File Excel
    with st.expander("📤 Upload Data Responden", expanded=True):
        uploaded_file = st.file_uploader(
            "Unggah file Excel",
            type=["xlsx"],
            help="Pastikan file sesuai dengan template standar"
        )

        if uploaded_file is not None:
            df, error = proses_file_excel(uploaded_file)
            file_name = uploaded_file.name.rsplit('.', 1)[0]

            if error:
                st.error(error)
            else:
                st.success("File berhasil diunggah dan diproses!")
                st.session_state['df'] = df

                # with st.expander("🔍 Lihat Preview Data"):
                   #  st.write("Main expander content")
                   # st.dataframe(df.head(3))
            if 'df' in st.session_state and st.session_state['df'] is not None:  # <-- Blok if kedua
                df = st.session_state['df']

                # Step 2: Lakukan Penilaian jika file sudah diupload
    if 'df' in st.session_state and st.session_state['df'] is not None:
        df = st.session_state['df']

        # Buat tab untuk tampilan
        tab1, tab2 = st.tabs(["📈 Hasil Penilaian", "📊 Visualisasi"])

        with tab1:
            df_semua_hasil = hitung_semua_responden(df)

            # Hitung rata-rata untuk setiap kolom numerik
            avg_dict = df_semua_hasil.drop(columns=["Responden_ID"]).mean()

            # Ambil nilai rata-rata indikator
            avg_SKTOTAL = avg_dict["SKTOTAL"]
            avg_KSTOTAL = avg_dict["KSTOTAL"]
            avg_IWTOTAL = avg_dict["IWTOTAL"]
            avg_KPTOTAL = avg_dict["KPTOTAL"]
            avg_ATTOTAL = avg_dict["ATTOTAL"]
            avg_HTTOTAL = avg_dict["HTTOTAL"]

            avg_RSTOTAL = avg_dict["RSTOTAL"]
            avg_KNTOTAL = avg_dict["KNTOTAL"]
            avg_AMTOTAL = avg_dict["AMTOTAL"]
            avg_ASTOTAL = avg_dict["ASTOTAL"]
            avg_HSTOTAL = avg_dict["HSTOTAL"]

            avg_NKKST = avg_dict["NKKST"]
            avg_NKKSS = avg_dict["NKKSS"]
            avg_NKI = avg_dict["NKI"]

            # Tentukan kategori untuk rata-rata
            avg_KATEGORI_NKI = tentukan_kategori(avg_NKI)
            avg_KATEGORI_NKKST = tentukan_kategori(avg_NKKST)
            avg_KATEGORI_NKKSS = tentukan_kategori(avg_NKKSS)

            # Tabel Aspek Teknis Rata-Rata

            hasil_df_teknis_avg = pd.DataFrame({
                "Indikator": [
                    "Syarat dan Ketentuan Instalasi",
                    "Kata Sandi",
                    "Internet dan WiFi",
                    "Keamanan Perangkat",
                    "Aduan Insiden Siber Teknis",
                    "Hukum dan Regulasi"
                ],
                "Nilai Rata-Rata": [avg_SKTOTAL, avg_KSTOTAL, avg_IWTOTAL,
                                    avg_KPTOTAL, avg_ATTOTAL, avg_HTTOTAL],
                "Kategori": [
                    tentukan_kategori(avg_SKTOTAL),
                    tentukan_kategori(avg_KSTOTAL),
                    tentukan_kategori(avg_IWTOTAL),
                    tentukan_kategori(avg_KPTOTAL),
                    tentukan_kategori(avg_ATTOTAL),
                    tentukan_kategori(avg_HTTOTAL)
                ]
            })

            # Tabel Aspek Sosial Rata-Rata

            hasil_df_sosial_avg = pd.DataFrame({
                "Indikator": [
                    "Rekayasa Sosial",
                    "Konten Negatif",
                    "Aktivitas Media Sosial",
                    "Aduan Konten Negatif",
                    "Hukum dan Regulasi Sosial"
                ],
                "Nilai Rata-Rata": [avg_RSTOTAL, avg_KNTOTAL, avg_AMTOTAL,
                                    avg_ASTOTAL, avg_HSTOTAL],
                "Kategori": [
                    tentukan_kategori(avg_RSTOTAL),
                    tentukan_kategori(avg_KNTOTAL),
                    tentukan_kategori(avg_AMTOTAL),
                    tentukan_kategori(avg_ASTOTAL),
                    tentukan_kategori(avg_HSTOTAL)
                ]
            })

            # Tampilkan NKI rata-rata di bagian atas
            col1, col2, col3 = st.columns([3.55, 4, 4])

            with col1:
                fig_index = (create_bar_index(avg_NKI))
                st.pyplot(fig_index, use_container_width=True)
            with col2:
                # Hitung distribusi kategori dari data responden
                distribusi_kategori = hitung_distribusi_kategori(df_semua_hasil)
                fig_pie = create_pie_kategori(distribusi_kategori)
                st.pyplot(fig_pie)
            with col3:
                st.subheader("Nilai Rata-Rata Kesadaran Keamanan Siber")
                st.write(f"Berdasarkan {len(df)} responden dari hasil **{file_name}**")
                st.metric(label="Rata-Rata NKI", value=f"{avg_NKI:.2f}")
                st.progress(avg_NKI / 100)
                st.info(f"Kategori: {avg_KATEGORI_NKI}")

            # Tabel Data Responden
            col_table1, col_table2 = st.columns([3, 1])  # Perubahan rasio kolom dari [5,1] menjadi [8,2]
            with col_table1:
                st.subheader("Tabel Hasil Responden")
                buat_tabel_responden(df, df_semua_hasil, avg_NKI)

            with col_table2:
                # Tombol Download untuk data rata-rata
                st.subheader("Ekspor Data Rata-Rata")
                excel_data = create_excel_download(
                    hasil_df_teknis_avg,
                    pd.DataFrame({"Deskripsi": ["Rata-Rata NKKST"], "Nilai": [avg_NKKST],
                                  "Kategori": [tentukan_kategori(avg_NKKST)]}),
                    hasil_df_sosial_avg,
                    pd.DataFrame({"Deskripsi": ["Rata-Rata NKKSS"], "Nilai": [avg_NKKSS],
                                  "Kategori": [tentukan_kategori(avg_NKKSS)]}),
                    pd.DataFrame({"Deskripsi": ["Rata-Rata NKI"], "Nilai": [avg_NKI],
                                  "Kategori": [avg_KATEGORI_NKI]})
                )
                st.download_button(
                    label="📥 Download Hasil Rata-Rata",
                    data=excel_data,
                    file_name="Hasil_Rata_Rata_Kesadaran_Keamanan_Siber.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )



            col_tek1, col_tek2 = st.columns([3, 1])
            with col_tek1:
                st.subheader("Rata-Rata Nilai Kesadaran Keamanan Siber Teknis (NKKST)")
                st.dataframe(hasil_df_teknis_avg.style.format({"Nilai Rata-Rata": "{:.2f}"}),
                             hide_index=True)
            with col_tek2:
                st.metric("Rata-Rata NKKST", f"{avg_NKKST:.2f}")
                st.progress(avg_NKKST / 100)
                st.success(f"Kategori: {tentukan_kategori(avg_NKKST)}")



            col_sos1, col_sos2 = st.columns([3, 1])
            with col_sos1:
                st.subheader("Rata-Rata Nilai Kesadaran Keamanan Siber Sosial (NKKSS)")
                st.dataframe(hasil_df_sosial_avg.style.format({"Nilai Rata-Rata": "{:.2f}"}),
                             hide_index=True)
            with col_sos2:
                st.metric("Rata-Rata NKKSS", f"{avg_NKKSS:.2f}")
                st.progress(avg_NKKSS / 100)
                st.warning(f"Kategori: {tentukan_kategori(avg_NKKSS)}")

        with tab2:
            st.header("Visualisasi Hasil")
            st.subheader("Hasil NKKST dan NKKSS")

            # Data untuk NKKST (6 indikator)
            categories_teknis = ['SK', 'KS', 'IW', 'KP', 'AT', 'HT']
            values_teknis = [avg_SKTOTAL, avg_KSTOTAL, avg_IWTOTAL, avg_KPTOTAL, avg_ATTOTAL, avg_HTTOTAL]

            # Pastikan values_teknis memiliki 6 elemen
            if len(values_teknis) != 6:
                st.error(f"Jumlah nilai NKKST harus 6, tetapi mendapatkan {len(values_teknis)}")
                values_teknis = values_teknis[:6]  # Ambil 6 nilai pertama jika lebih

            # Data untuk NKKSS (5 indikator)
            categories_sosial = ['RS', 'KN', 'AM', 'AS', 'HS']
            values_sosial = [avg_RSTOTAL, avg_KNTOTAL, avg_AMTOTAL, avg_ASTOTAL, avg_HSTOTAL]

            # Pastikan values_sosial memiliki 5 elemen
            if len(values_sosial) != 5:
                st.error(f"Jumlah nilai NKKSS harus 5, tetapi mendapatkan {len(values_sosial)}")
                values_sosial = values_sosial[:5]  # Ambil 5 nilai pertama jika lebih

            #Kolom Nilai NKKST dan NKKSS
            col1, col2, col3 = st.columns([4.05, 5, 5])

            with col1:
                fig_comparison = create_bar_variabel(avg_NKKST, avg_NKKSS, figsize=(7, 5.2))
                st.pyplot(fig_comparison, use_container_width=True)
            with col2:
                try:
                    fig_bar_teknis = create_bar_chart_NKKST(categories_teknis, values_teknis, figsize=(7, 5.1))
                    st.pyplot(fig_bar_teknis, use_container_width=True)
                except Exception as e:
                    st.error(f"Error membuat bar chart NKKST: {str(e)}")
            with col3:
                try:
                    fig_bar_sosial = create_bar_chart_NKKSS(categories_sosial, values_sosial, figsize=(7, 5.1))
                    st.pyplot(fig_bar_sosial, use_container_width=True)
                except Exception as e:
                    st.error(f"Error membuat bar chart NKKSS: {str(e)}")

            col_JK, col_UMUR = st.columns([5, 5])
            with col_JK:
                if 'df' in st.session_state and st.session_state['df'] is not None:
                    df = st.session_state['df']

                    if "JENIS KELAMIN" in df.columns:
                        st.subheader("Grafik Jenis Kelamin Responden")
                        fig = create_pie_kelamin(df)
                        st.pyplot(fig)
                    else:
                        st.warning("Kolom 'JENIS KELAMIN' tidak ditemukan dalam data")
            with col_UMUR:
                if 'df' in st.session_state and st.session_state['df'] is not None:
                    df = st.session_state['df']

                    if "UMUR" in df.columns:
                        st.subheader("Grafik Umur Responden")
                        # Buat dan tampilkan bar chart
                        fig = create_bar_umur(df)
                        st.pyplot(fig)
                    else:
                        st.warning("Kolom 'UMUR' tidak ditemukan dalam data")

            col_TP, col_DOMISILI = st.columns([5, 5])
            with col_TP:
                if 'df' in st.session_state and st.session_state['df'] is not None:
                    df = st.session_state['df']

                    if "TINGKAT PENDIDIKAN" in df.columns:
                        st.subheader("Grafik Tingkat Pendidikan Responden")
                        # Buat dan tampilkan bar chart
                        fig = create_bar_pendidikan(df)
                        st.pyplot(fig)
                    else:
                        st.warning("Kolom 'UMUR' tidak ditemukan dalam data")
            with col_DOMISILI:
                if 'df' in st.session_state and st.session_state['df'] is not None:
                    df = st.session_state['df']

                    if "PROVINSI" in df.columns:
                        st.subheader("Grafik Domisili Responden")
                        # Buat dan tampilkan bar chart
                        fig = create_bar_domisili(df)
                        st.pyplot(fig)
                    else:
                        st.warning("Kolom 'DOMISILI' tidak ditemukan dalam data")

if __name__ == "__main__":
    main()
