import streamlit as st
import geopandas as gpd
from shapely.geometry import Point

# Judul aplikasi
st.title("🗺️ Cek Koordinat dalam Wilayah SBR")

# Ambil GeoJSON dari GitHub
url = "https://raw.githubusercontent.com/masnanana/koordinat-sbr-3375/main/data.geojson"

# Coba baca data GeoJSON
try:
    gdf = gpd.read_file(url)

    # Pastikan dalam EPSG:4326
    if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
except Exception as e:
    st.error(f"❌ Gagal memuat GeoJSON: {e}")
    st.stop()

# Input koordinat dari pengguna
koordinat_input = st.text_input("📍 Masukkan koordinat dari Google Maps (format: lat, lon)", "")

if st.button("🔍 Cek Lokasi"):
    if koordinat_input.strip() == "":
        st.warning("⚠️ Silakan masukkan koordinat terlebih dahulu.")
    else:
        try:
            lat_str, lon_str = koordinat_input.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            titik = Point(lon, lat)

            # Cek apakah titik berada dalam poligon
            hasil = gdf[gdf.contains(titik)]

            if not hasil.empty:
                row = hasil.iloc[0]
                st.success("✅ Titik berada di wilayah:")
                st.markdown(f"- **Kabupaten**: {row.get('nmkab', '-')}")
                st.markdown(f"- **Kecamatan**: {row.get('nmkec', '-')}")
                st.markdown(f"- **Desa**: {row.get('nmdesa', '-')}")
                st.markdown(f"- **SLS**: {row.get('nmsls', '-')}")
            else:
                st.error("❌ Titik tidak berada dalam batas wilayah manapun.")
        except:
            st.error("❌ Format salah. Gunakan format: -6.88, 109.68")

