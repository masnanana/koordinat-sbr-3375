import streamlit as st
import geopandas as gpd
from shapely.geometry import Point

@st.cache_data
def load_geojson()
    return gpd.read_file(data.geojson).to_crs(epsg=4326)

gdf = load_geojson()

st.title(🔍 Cek Lokasi Berdasarkan Koordinat)
st.write(Masukkan koordinat dari Google Maps (format `lat, lon`))

koordinat = st.text_input(Contoh `-6.88, 109.68`)

if koordinat
    try
        lat_str, lon_str = koordinat.split(,)
        lat = float(lat_str.strip())
        lon = float(lon_str.strip())
        titik = Point(lon, lat)

        hasil = gdf[gdf.contains(titik)]

        if not hasil.empty
            row = hasil.iloc[0]
            st.success(✅ Lokasi ditemukan)
            st.write(fKabupaten {row['nmkab']})
            st.write(fKecamatan {row['nmkec']})
            st.write(fDesa {row['nmdesa']})
            st.write(fSLS {row['nmsls']})
        else
            st.warning(❌ Titik tidak ada dalam batas wilayah.)
    except
        st.error(❌ Format salah. Gunakan format `-6.88, 109.68`)
