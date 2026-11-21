# StormSight Atmospheric Data Sources

## Primary Observation Sources

| Source | Agency | Instrument / Model | Primary Variables | Resolution | Format |
|---|---|---|---|---|---|
| **Weather Radar** | IMD | Doppler Weather Radar (DWR) | Reflectivity ($Z_H$), Diff. Refl ($Z_{DR}$) | 250 km radius / 2 km grid | NetCDF4 / HDF5 |
| **Satellite** | ISRO / MOSDAC | INSAT-3D / 3DR / 3DS | TIR1 (10.8 µm), Water Vapour (6.7 µm) | 4 km resampled to 2 km | HDF5 |
| **Lightning** | IMD / IITM / Vaisala | ILDN / GLD360 | Flash coordinates, peak current, CG/IC | Point events | JSON / CSV |
| **NWP Model** | NCEP / NCMRWF | GFS / NCUM | CAPE, CIN, 0-6 km wind shear | 13–25 km | GRIB2 |

## Development & Benchmark Datasets
- **SEVIR (Spatiotemporal Environmental Radar & Satellite)**: Open multimodal benchmark containing synchronized radar, GOES infrared/water-vapour, and GLM lightning flashes.
- **NOAA NEXRAD Level-II**: Public Doppler radar archive for continuous validation and Py-ART testing.
