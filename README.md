# BayArea_EnvRisk_GIS_Analysis
A Python-based geospatial analysis of pollution source proximity to water bodies in the San Francisco Bay Area.
# Bay Area Environmental Risk Proximity Analysis

---

## Project Overview

This project performs a spatial proximity analysis between **polluting facilities** in the San Francisco Bay Area and **water bodies** sourced from the National Hydrography Dataset (NHD), using **GeoPandas** and **Python**.

The primary objective is to calculate the minimum distance from each pollution source to the nearest surface water feature and categorize the facility based on this proximity into distinct **environmental risk levels**.

### Project Deliverables

Upon successful execution, the project generates the following two core output files:

1.  **`BayArea_Risk_Analysis_Results.csv`**: A structured report containing the facility details, their minimum distance (in meters), and the final risk classification.
2.  **`bay_area_risk_map.html`**: An interactive **Folium** map visualization. Facilities are marked and colored according to their calculated risk level (High/Medium/Low), allowing for easy navigation and inspection.

---

## 🛠️ Technology Stack and Dependencies

This project relies on the following key Python libraries, managed within a **Conda** virtual environment:

* **GeoPandas (v0.14+)**: Core library for geospatial data handling and processing.
* **Pandas**: Data cleaning and report generation.
* **Folium**: Interactive map visualization.
* **Pyogrio / Fiona**: Shapefile reading engine, dependent on **GDAL**.

### Environment Setup (Conda Recommended)

Due to the complex dependencies of GeoPandas (especially GDAL) on Windows, using **Conda** or **Mamba** is strongly recommended for a stable environment:

```bash
# 1. Create and activate the environment
conda create -n georisk_env python=3.10
conda activate georisk_env

# 2. Install all dependencies (Use conda-forge for robust GIS libraries)
conda install -c conda-forge geopandas pyogrio folium pandas

Website: https://e-alkl.github.io/BayArea_EnvRisk_GIS_Analysi/bay_area_risk_map.html
