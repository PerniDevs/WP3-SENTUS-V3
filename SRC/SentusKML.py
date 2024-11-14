import simplekml
import pandas as pd
from InputOutput import PvtIdx


def dat_to_kml(dat_file_path, kml_file_path):
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

        
        # Add a new point to the KML file
        point = kml.newpoint()
        point.coords = [(longitude, latitude, altitude)]
        point.description = f"Timestamp: {timestamp}"
        point.altitudemode = simplekml.AltitudeMode.absolute  # Set altitude mode
    
    # Save the KML file
    kml.save(kml_file_path)
    print(f"KML file created: {kml_file_path}")

# Usage
dat_to_kml("/home/perni/Desktop/GNSS-ACADEMY/WP3/SENTUS-V3/SCN/SCEN-SENTINEL6A-JAN24/OUT/PVT/PVT_OBS_s6an_Y24D011.dat", "/home/perni/Desktop/GNSS-ACADEMY/WP3/SENTUS-V3/SCN/SCEN-SENTINEL6A-JAN24/OUT/PVT/PVT_OBS_s6an_Y24D011.kml")