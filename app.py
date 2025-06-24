import streamlit as st
import geopandas as gpd
from shapely.geometry import Point
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Cek Lokasi Gmaps", layout="centered")


st.markdown("""
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/masnanana/koordinat-sbr-3375/main/logo_tirto.png" width="300"/>
        <div style="font-size:16px; margin-top:5px; color: #444;"> <h1 style="margin-top:10px;">Temukan Informasi Rukun Tetangga Otomatis</h1></div>
       
    </div>
""", unsafe_allow_html=True)



# === Load data
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/masnanana/koordinat-sbr-3375/main/data.geojson"
    gdf = gpd.read_file(url)
    if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
    return gdf

gdf = load_geojson()

# === Reset kondisi saat tombol lain ditekan
if "last_button" not in st.session_state:
    st.session_state.last_button = None

# === Input manual
st.markdown("### 📝 Masukkan Koordinat Manual (format = lat, lan)")
koordinat_input = st.text_input("Contoh: -6.8888, 109.6789", key="manual_input")

# === Tombol vertikal (atas-bawah)
if st.button("🔍 Cek Lokasi Manual"):
    st.session_state.last_button = "manual"
    st.rerun()

if st.button("📡 Ambil Titik Gmaps Sekarang"):
    st.session_state.last_button = "gmaps"
    st.rerun()

# === Eksekusi berdasarkan tombol terakhir
lat = lon = None
if st.session_state.last_button == "manual":
    if not koordinat_input:
        st.warning("Silakan masukkan koordinat terlebih dahulu.")
    else:
        try:
            lat_str, lon_str = koordinat_input.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            st.success(f"📍 Koordinat manual: {lat}, {lon}")
        except:
            st.error("❌ Format salah. Gunakan format: `-6.8888, 109.6789`")

elif st.session_state.last_button == "gmaps":
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

    if lokasi is None:
        st.error("❌ Tidak ada data lokasi yang diterima.")
    elif 'error' in lokasi:
        st.warning(f"⚠️ Gagal mengambil titik: {lokasi['error']}")
    else:
        lat = lokasi.get("lat")
        lon = lokasi.get("lon")
        st.success(f"📍 Koordinat dari browser: {lat}, {lon}")

# === Cek hasil koordinat
if lat is not None and lon is not None:
    titik = Point(lon, lat)
    hasil = gdf[gdf.contains(titik)]
    st.markdown("---")
    st.markdown("<h3>🗺️ Hasil Cek Wilayah:</h3>", unsafe_allow_html=True)

    if not hasil.empty:
        row = hasil.iloc[0]
        st.markdown(f"""
            <div style="background-color:#e8f4ff;padding:20px;border-radius:10px;border-left:5px solid #1c8adb;">
                <b>Kota :</b> {row.get('nmkab', '-')}<br>
                <b>Kecamatan :</b> {row.get('nmkec', '-')}<br>
                <b>Kelurahan :</b> {row.get('nmdesa', '-')}<br>
                <b>SLS :</b> {row.get('nmsls', '-')}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ Titik tidak berada dalam batas wilayah Kota Pekalongan")
