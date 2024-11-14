import simplekml
import pandas as pd
from InputOutput import PvtIdx
import math



def generate_circle_polygon(latitude, longitude, radius_km, num_segments=36):
    """
    Generate the coordinates for a circular polygon in KML.
    latitude, longitude: Center of the circle
    radius_km: Radius of the circle in kilometers
    num_segments: Number of segments to approximate the circle
    """
    coords = []
    for i in range(num_segments + 1):
        angle = math.radians(float(i) / num_segments * 360)
        lat_offset = (radius_km / 6371) * math.sin(angle)  # 6371 km is Earth's radius
        lon_offset = (radius_km / 6371) * math.cos(angle) / math.cos(math.radians(latitude))
        
        lat = latitude + math.degrees(lat_offset)
        lon = longitude + math.degrees(lon_offset)
        coords.append((lon, lat))  # KML format expects (longitude, latitude)
    return coords

def dat_to_kml(dat_file_path, kml_file_path, radius_km=100):
    # Read the .dat file using pandas
    data = pd.read_csv(dat_file_path, delim_whitespace=True, skiprows=1, header=None, 
                       usecols=[PvtIdx["SOD"], PvtIdx["LONG"], PvtIdx["LAT"], PvtIdx["ALT"]])
    
    # Initialize KML object
    kml = simplekml.Kml()
    
    # Iterate over each row in the dataframe
    for index, row in data.iterrows():
        print(row)
        # Assuming columns are named 'timestamp', 'latitude', 'longitude', 'altitude'
        timestamp = row[PvtIdx["SOD"]]
        latitude = row[PvtIdx["LAT"]]
        longitude = row[PvtIdx["LONG"]]
        altitude = row[PvtIdx["ALT"]]

        # Generate a circular polygon around each point
        coords = generate_circle_polygon(latitude, longitude, radius_km)

        
         # Add the polygon to the KML file
        pol = kml.newpolygon(name=timestamp)
        pol.outerboundaryis = coords
        pol.altitudemode = simplekml.AltitudeMode.clamptoground  # Ground level
        pol.style.polystyle.color = simplekml.Color.changealphaint(100, simplekml.Color.white)  # Semi-transparent white color
        
        # Optional: Add description
        pol.description = f"Timestamp: {timestamp}"
    
    # Save the KML file
    kml.save(kml_file_path)
    print(f"KML file created: {kml_file_path}")

# Usage
dat_to_kml("/home/perni/Desktop/GNSS-ACADEMY/WP3/SENTUS-V3/SCN/SCEN-SENTINEL6A-JAN24/OUT/PVT/PVT_OBS_s6an_Y24D011.dat", "/home/perni/Desktop/GNSS-ACADEMY/WP3/SENTUS-V3/SCN/SCEN-SENTINEL6A-JAN24/OUT/PVT/PVT_OBS_s6an_Y24D011.kml", radius_km=100)