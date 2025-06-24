import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Cek Lokasi Gmaps", layout="centered")
st.title("📍 Cek Wilayah SLS Kota Pekalongann")

# === Load GeoJSON ===
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/masnanana/koordinat-sbr-3375/main/data.geojson"
    gdf = gpd.read_file(url)
    if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    return gdf

gdf = load_geojson()

# === Input Manual ===
st.markdown("### 📝 Masukkan Koordinat Manual (format: `lat, lon`)")
koordinat_input = st.text_input("Contoh: `-6.8888, 109.6789`", key="manual_input")

# === Dua Tombol Sejajar ===
col1, col2 = st.columns(2)
with col1:
    cek_manual = st.button("🧭 Cek Lokasi Manual")
with col2:
    ambil_gmaps = st.button("🎯 Ambil Titik Gmaps Sekarang")

# === Variabel koordinat
lat = lon = None

# === Logika tombol manual
if cek_manual:
    if not koordinat_input:
        st.warning("Silakan masukkan koordinat terlebih dahulu.")
    else:
        try:
            lat_str, lon_str = koordinat_input.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            st.success(f"Koordinat manual berhasil dibaca: {lat}, {lon}")
        except:
            st.error("❌ Format salah. Gunakan format: `-6.8888, 109.6789`")

# === Trigger ambil gmaps pakai session_state
if ambil_gmaps:
    st.session_state['trigger_gmaps'] = True

# === Hanya jalankan streamlit_js_eval jika sudah ditekan tombol
if st.session_state.get("trigger_gmaps", False):
    lokasi = streamlit_js_eval(
        js_expressions="""
            new Promise((resolve, reject) => {
                if (!navigator.geolocation) {
                    resolve({ error: "Geolocation tidak didukung browser ini." });
                } else {
                    navigator.geolocation.getCurrentPosition(
                        pos => resolve({ lat: pos.coords.latitude, lon: pos.coords.longitude }),
                        err => resolve({ error: err.message })
                    );
                }
            })
        """,
        key="ambil_gmaps_eval",
        want_result=True,
    )

    st.subheader("📡 Debug Output dari Browser:")
    st.json(lokasi)

    if lokasi is None:
        st.error("❌ Tidak ada data lokasi yang diterima. Pastikan izin lokasi diaktifkan.")
    elif 'error' in lokasi:
        st.warning(f"⚠️ Gagal mengambil titik: {lokasi['error']}")
    else:
        lat = lokasi.get("lat")
        lon = lokasi.get("lon")
        if lat is not None and lon is not None:
            st.success(f"📍 Koordinat dari browser: {lat}, {lon}")
        else:
            st.warning("⚠️ Koordinat tidak ditemukan.")

# === Proses hasil jika ada koordinat
if lat is not None and lon is not None:
    titik = Point(lon, lat)
    hasil = gdf[gdf.contains(titik)]

    st.markdown("---")
    st.subheader("🗺️ Hasil Cek Wilayah:")

    if not hasil.empty:
        row = hasil.iloc[0]
        st.markdown(f"""
            <div style="background-color:#f0f8ff;padding:15px;border-radius:10px;">
                <b>Kota:</b> {row.get('nmkab', '-')}<br>
                <b>Kecamatan:</b> {row.get('nmkec', '-')}<br>
                <b>Kelurahan:</b> {row.get('nmdesa', '-')}<br>
                <b>SLS:</b> {row.get('nmsls', '-')}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Titik tidak berada dalam batas wilayah manapun.")
