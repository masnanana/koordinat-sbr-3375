import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Cek Lokasi Gmaps", layout="centered")

# === Judul Tengah
st.markdown("<h1>Cek Wilayah SLS Kota Pekalongan</h1>", unsafe_allow_html=True)

# === Load GeoJSON
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/masnanana/koordinat-sbr-3375/main/data.geojson"
    gdf = gpd.read_file(url)
    if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    return gdf

gdf = load_geojson()

# === Inisialisasi session_state
if "lat" not in st.session_state:
    st.session_state.lat = None
    st.session_state.lon = None
    st.session_state.hasil = None
    st.session_state.trigger_gmaps = False

# === Input Manual
st.markdown("### 📝 Masukkan Koordinat Manual (format: `lat, lon`)")
koordinat_input = st.text_input("Contoh: `-6.8888, 109.6789`", key="manual_input")

# === Tombol
cek_manual = st.button("🔍 Cek Lokasi Manual")
ambil_gmaps = st.button("📡 Ambil Titik Gmaps Sekarang")

st.markdown("<br>", unsafe_allow_html=True)

# === Reset hasil jika salah satu tombol ditekan
if cek_manual or ambil_gmaps:
    st.session_state.lat = None
    st.session_state.lon = None
    st.session_state.hasil = None

# === Logika tombol manual
if cek_manual:
    if not koordinat_input:
        st.warning("Silakan masukkan koordinat terlebih dahulu.")
    else:
        try:
            lat_str, lon_str = koordinat_input.split(",")
            st.session_state.lat = float(lat_str.strip())
            st.session_state.lon = float(lon_str.strip())
            st.success(f"Koordinat manual berhasil dibaca: {st.session_state.lat}, {st.session_state.lon}")
        except:
            st.error("❌ Format salah. Gunakan format: `-6.8888, 109.6789`")

# === Trigger ambil gmaps
if ambil_gmaps:
    st.session_state.trigger_gmaps = True

# === Eksekusi ambil gmaps
if st.session_state.trigger_gmaps:
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

    # Reset trigger
    st.session_state.trigger_gmaps = False

    if lokasi is None:
        st.error("❌ Tidak ada data lokasi yang diterima. Pastikan izin lokasi diaktifkan.")
    elif 'error' in lokasi:
        st.warning(f"⚠️ Gagal mengambil titik: {lokasi['error']}")
    else:
        st.session_state.lat = lokasi.get("lat")
        st.session_state.lon = lokasi.get("lon")
        if st.session_state.lat is not None and st.session_state.lon is not None:
            st.success(f"📍 Koordinat dari browser: {st.session_state.lat}, {st.session_state.lon}")
        else:
            st.warning("⚠️ Koordinat tidak ditemukan.")

# === Cek hasil dari koordinat
if st.session_state.lat is not None and st.session_state.lon is not None:
    titik = Point(st.session_state.lon, st.session_state.lat)
    st.session_state.hasil = gdf[gdf.contains(titik)]

    st.markdown("---")
    st.markdown("<h3>🗺️ Hasil Cek Wilayah:</h3>", unsafe_allow_html=True)

    if not st.session_state.hasil.empty:
        row = st.session_state.hasil.iloc[0]
        st.markdown(f"""
            <div style="background-color:#e8f4ff;padding:20px;border-radius:10px;border-left:5px solid #1c8adb;">
                <b>Kota :</b> {row.get('nmkab', '-')}<br>
                <b>Kecamatan :</b> {row.get('nmkec', '-')}<br>
                <b>Kelurahan :</b> {row.get('nmdesa', '-')}<br>
                <b>SLS :</b> {row.get('nmsls', '-')}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Titik tidak berada dalam batas wilayah Kota Pekalongan.")
