import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Cek Lokasi Gmaps", layout="centered")

# === Inisialisasi session_state
if "lat" not in st.session_state:
    st.session_state.lat = None
    st.session_state.lon = None
    st.session_state.hasil = None
    st.session_state.trigger_gmaps = False

# === Judul
st.markdown("<h1 style='text-align: center;'>📍 Cek Wilayah SLS Kota Pekalongan</h1>", unsafe_allow_html=True)

# === Load GeoJSON
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/masnanana/koordinat-sbr-3375/main/data.geojson"
    gdf = gpd.read_file(url)
    if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    return gdf

gdf = load_geojson()

# === Input Manual
st.markdown("### 📝 Masukkan Koordinat Manual (format: `lat, lon`)")
koordinat_input = st.text_input("Contoh: `-6.8888, 109.6789`", key="manual_input")

# === Tombol Aksi
cek_manual = st.button("🔍 Cek Lokasi Manual")
ambil_gmaps = st.button("📡 Ambil Titik Gmaps Sekarang")

st.markdown("<br>", unsafe_allow_html=True)

# === RESET HASIL saat tombol ditekan
if cek_manual or ambil_gmaps:
    st.session_state.lat = None
    st.session_state.lon = None
    st.session_state.hasil = None

# === Logika manual
if cek_manual:
    if not koordinat_input:
        st.warning("Silakan masukkan koordinat terlebih dahulu.")
    else:
        try:
            lat_str, lon_str = koordinat_input.split(",")
            st.session_state.lat = float(lat_str.strip())
            st.session_state.lon = float(lon_str.strip())
            st.success(f"Koordinat manual: {st.session_state.lat}, {st.session_state.lon}")
        except:
            st.error("❌ Format salah. Gunakan format: `-6.8888, 109.6789`")

# === Logika tombol Gmaps
if ambil_gmaps:
    st.session_state.trigger_gmaps = True

if st.session_state.get("trigger_gmaps"):
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

    st.session_state.trigger_gmaps = False  # reset trigger

    if lokasi is None:
        st.error("❌ Tidak ada data lokasi yang diterima.")
    elif 'error' in lokasi:
        st.warning(f"⚠️ {lokasi['error']}")
    else:
        st.session_state.lat = lokasi.get("lat")
        st.session_state.lon = lokasi.get("lon")
        if st.session_state.lat and st.session_state.lon:
            st.success(f"📍 Koordinat dari browser: {st.session_state.lat}, {st.session_state.lon}")
        else:
            st.warning("⚠️ Koordinat tidak ditemukan.")

# === Cek hasil wilayah
if st.session_state.lat is not None and st.session_state.lon is not None:
    titik = Point(st.session_state.lon, st.session_state.lat)
    st.session_state.hasil = gdf[gdf.contains(titik)]

    st.markdown("---")
    st.markdown("### 🗺️ Hasil Cek Wilayah")

    if not st.session_state.hasil.empty:
        row = st.session_state.hasil.iloc[0]
        st.markdown(f"""
            <div style="background-color:#e8f4ff;padding:20px;border-radius:10px;border-left:5px solid #1c8adb;">
                <b>Kota:</b> {row.get('nmkab', '-')}<br>
                <b>Kecamatan:</b> {row.get('nmkec', '-')}<br>
                <b>Kelurahan:</b> {row.get('nmdesa', '-')}<br>
                <b>SLS:</b> {row.get('nmsls', '-')}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Titik tidak berada dalam batas wilayah manapun.")
