import geopandas as gpd
from shapely.geometry import Point

# Ambil GeoJSON langsung dari GitHub kamu
url = "https://raw.githubusercontent.com/masnanana/koordinat-sbr-3375/main/data.geojson"

# Baca file GeoJSON
gdf = gpd.read_file(url)

# Pastikan dalam sistem koordinat EPSG:4326 (lat, lon)
if gdf.crs is None or gdf.crs.to_string() != "EPSG:4326":
    gdf = gdf.to_crs(epsg=4326)

# Input koordinat Google Maps
try:
    koordinat = input("📍 Masukkan koordinat dari Google Maps (format: lat, lon): ")
    lat_str, lon_str = koordinat.split(",")
    lat = float(lat_str.strip())
    lon = float(lon_str.strip())
except:
    print("❌ Format salah. Gunakan format: -6.88, 109.68")
    raise SystemExit

# Buat titik shapely dari input
titik = Point(lon, lat)

# Cari poligon yang mengandung titik
hasil = gdf[gdf.contains(titik)]

# Tampilkan hasil
if not hasil.empty:
    row = hasil.iloc[0]
    print("✅ Titik berada di wilayah:")
    print(f"- Kabupaten : {row.get('nmkab', '-')}")
    print(f"- Kecamatan : {row.get('nmkec', '-')}")
    print(f"- Desa      : {row.get('nmdesa', '-')}")
    print(f"- SLS       : {row.get('nmsls', '-')}")
else:
    print("❌ Titik tidak berada dalam batas wilayah manapun.")
