import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium

# --- 1. Settings and File Definitions ---

# Define file names (Ensure these files are in the same directory)
FACILITY_FILE = 'bay_area_facilities_cleaned.csv'
WATER_FILE = 'NHDFlowline.shp' 
# Target Projected CRS for the Bay Area (UTM Zone 10N, unit is meters)
TARGET_CRS = 'EPSG:32610' 

def load_and_transform_data():
    """Loads facility and water data and transforms them to the common projected CRS."""
    
    print("--- 1. Data Loading and GeoDataFrame Creation ---")
    
    # Load Facility Data (Points)
    try:
        df_facilities = pd.read_csv(FACILITY_FILE)
        # Create geometry points from Longitude/Latitude, initial CRS is EPSG:4326
        geometry = [Point(xy) for xy in zip(df_facilities['LONGITUDE'], df_facilities['LATITUDE'])]
        gdf_facilities = gpd.GeoDataFrame(
            df_facilities,
            geometry=geometry,
            crs="EPSG:4326"
        )
    except FileNotFoundError:
        print(f"ERROR: Facility file {FACILITY_FILE} not found. Check file name and path.")
        return None, None
    
    # Load Water Body Data (Lines/Polygons)
    try:
        # Load Shapefile
        gdf_water = gpd.read_file(WATER_FILE)
    except Exception as e:
        print(f"ERROR: Failed to load water Shapefile {WATER_FILE}. Error: {e}")
        return None, None

    print(f"Facilities loaded: {len(gdf_facilities)} points. Water features loaded: {len(gdf_water)}")
    
    # --- 2. Coordinate Reference System (CRS) Transformation ---
    print(f"--- 2. Transforming CRS to {TARGET_CRS} (Meters unit) ---")
    
    # Convert both GeoDataFrames to the target projected CRS for accurate distance measurement
    gdf_facilities_proj = gdf_facilities.to_crs(TARGET_CRS)
    gdf_water_proj = gdf_water.to_crs(TARGET_CRS)
    
    print(f"Data successfully projected. CRS: {gdf_facilities_proj.crs}")
    return gdf_facilities_proj, gdf_water_proj

def calculate_distance_and_categorize_risk(gdf_facilities_proj, gdf_water_proj):
    """Calculates the minimum distance to water and assigns a risk category."""

    print("\n--- 3. Core Distance Calculation and Risk Categorization ---")
    
    distances_m = []

    # Iterate through facility points to find the minimum distance to any water feature
    # WARNING: This loop can be slow with large datasets
    for index, facility in gdf_facilities_proj.iterrows():
        # .min() finds the shortest distance among all water features
        min_dist = gdf_water_proj.distance(facility.geometry).min()
        distances_m.append(min_dist)

    # Add the distance result back to the GeoDataFrame
    gdf_facilities_proj['Distance_to_Water_m'] = distances_m
    
    print("Distance calculation complete!")

    # Define Environmental Engineering Risk Thresholds (in meters)
    HIGH_RISK_THRESHOLD = 100 
    MEDIUM_RISK_THRESHOLD = 500 

    def categorize_risk(distance):
        """Assigns a risk level based on the calculated distance."""
        if distance <= HIGH_RISK_THRESHOLD:
            return 'High Risk (<100m)'
        elif distance <= MEDIUM_RISK_THRESHOLD:
            return 'Medium Risk (101-500m)'
        else:
            return 'Low Risk (>500m)'

    # Create the Risk Category column
    gdf_facilities_proj['Risk_Category'] = gdf_facilities_proj['Distance_to_Water_m'].apply(categorize_risk)
    
    return gdf_facilities_proj

def generate_reports(gdf_classified):
    """Generates the final CSV report and the interactive Folium map."""
    
    # 1. Output CSV Report
    print("\n--- 4. Outputting CSV Report ---")
    
    # Convert back to EPSG:4326 for easy reading of original Lat/Lon in the report
    gdf_report = gdf_classified.to_crs(epsg=4326)
    
    df_report = gdf_report[[
        'FACILITY_NAME', 
        'COUNTY', 
        'LATITUDE', 
        'LONGITUDE', 
        'Distance_to_Water_m', 
        'Risk_Category'
    ]].copy()

    df_report.to_csv('BayArea_Risk_Analysis_Results.csv', index=False)
    print("CSV Report saved to 'BayArea_Risk_Analysis_Results.csv'.")
    print("\nRisk Category Statistics:")
    print(df_report['Risk_Category'].value_counts())

    # 2. Generate Interactive Map (Folium)
    print("\n--- 5. Generating Interactive Map (Folium) ---")
    
    # Create the map centered near the Bay Area
    m = folium.Map(location=[37.77, -122.41], zoom_start=9, tiles='CartoDB Positron')

    # Define colors for risk categories
    risk_colors = {'High Risk (<100m)': 'red', 'Medium Risk (101-500m)': 'orange', 'Low Risk (>500m)': 'blue'}

    # Plot points on the map
    for index, row in df_report.iterrows():
        color = risk_colors.get(row['Risk_Category'], 'gray')
        
        popup_html = (
            f"<b>Facility: {row['FACILITY_NAME']}</b><br>"
            f"County: {row['COUNTY']}<br>"
            f"Distance to Water: {row['Distance_to_Water_m']:.2f} m<br>"
            f"Risk Level: {row['Risk_Category']}"
        )
        
        folium.CircleMarker(
            location=[row['LATITUDE'], row['LONGITUDE']],
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=popup_html
        ).add_to(m)

    m.save("bay_area_risk_map.html")
    print("Interactive map saved as 'bay_area_risk_map.html'.")

# --- Main Execution Block ---
if __name__ == "__main__":
    
    # Step 1-2: Load and Transform Data
    gdf_facilities_proj, gdf_water_proj = load_and_transform_data()
    
    if gdf_facilities_proj is not None and gdf_water_proj is not None:
        
        # Step 3: Calculate Distance and Classify Risk
        gdf_classified = calculate_distance_and_categorize_risk(gdf_facilities_proj, gdf_water_proj)
        
        # Step 4-5: Output Reports and Map
        generate_reports(gdf_classified)
        
        print("\n--- Project executed successfully! Check your directory for the two output files. ---")