# ARPINIA ODYSSEY — DATA SOURCES

## 1. Sentinel-1 SAR (Zenodo / Copernicus)
- **Primary Source:** Zenodo Oil Spill Datasets (e.g., M4D or Kresten et al.).
- **Fallback:** Copernicus Data Space Ecosystem (CDSE).
- **Format:** GeoTIFF or SAFE format.

## 2. AIS (MarineCadastre / Synthetic)
- **Primary Open Source:** NOAA MarineCadastre (US Waters only).
- **Fallback Source:** `SYNTHETIC_DEMO_AIS`. Generated using standard navigational mathematics to mimic realistic shipping lanes, SOG, and COG.
- **Format:** CSV / GeoJSON.

## 3. Meteorological (ECMWF ERA5)
- **Source:** Copernicus Climate Change Service (C3S).
- **Variables:** 10m u-component of wind, 10m v-component of wind.
- **Format:** NetCDF (.nc).

## 4. Oceanographic (Copernicus Marine)
- **Source:** Copernicus Marine Environment Monitoring Service (CMEMS).
- **Variables:** Eastward sea water velocity (uo), Northward sea water velocity (vo).
- **Format:** NetCDF (.nc).
