import requests
import pandas as pd
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
import numpy as np
import ftplib
import os
import io

# Allow larger images
Image.MAX_IMAGE_PIXELS = None

# Function to plot the Cyclone Track
def plot_cyclone_track(track_data, cyclone_id):
    # Add additional information
# Step 3: Calculate max wind speed and time of occurrence
    max_wind = track_data['Intensity'].max()
    max_wind_time = track_data.loc[track_data['Intensity'].idxmax(), 'Synoptic Time']
    max_mslp = track_data.loc[track_data['Intensity'].idxmax(), 'Pressure']
    
    # Step 4: Plot the Cyclone Track

    # Define the conditions and corresponding colors for cyclone categories
    prev_conditions = [
        ("Invest Area", 'lime'),
        ("Depression", 'steelblue'),
        ("Deep Depression", 'deepskyblue'),
        ("Cyclonic Storm", 'aqua'),
        ("Category 1", 'lemonchiffon'),
        ("Category 2", 'gold'),
        ("Category 3", 'tomato'),
        ("Category 4", 'fuchsia'),
        ("Category 5", 'mediumpurple'),
    ]

    # Create the legend for previous conditions
    legend_elements_prev = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=8, label=condition, lw=0, mec='k')
        for condition, color in prev_conditions
    ]

    # Step 5: Load the background image from the URL
    image_url = "https://cdn.trackgen.codingcactus.codes/map.jpg"
    img_response = requests.get(image_url)

    if img_response.status_code == 200:
        img = Image.open(io.BytesIO(img_response.content))
        img = img.resize((int(img.width / 2), int(img.height / 2)), Image.Resampling.LANCZOS)  # Downscale by 2x
        background_image = np.array(img)
    else:
        print(f"Failed to retrieve the image. Status code: {img_response.status_code}")
        background_image = np.zeros((1000, 1000, 3))  # Placeholder in case of error

    # Define the latitude and longitude limits
    lat_min, lat_max = -90, 90
    lon_min, lon_max = -180, 180

    # Get the last latitude and longitude values
    first_lat = track_data["Latitude"].min()
    last_lat = track_data["Latitude"].max()
    last_lon = track_data["Longitude"].max()
    first_lon = track_data["Longitude"].min()
    # Set the latitude and longitude limits based on the last values with a buffer
    ax.set_xlim(first_lon - 7, last_lon + 5)
    ax.set_ylim(first_lat - 3, last_lat + 4)

    # Set the extent of the background image
    ax.imshow(background_image, extent=[lon_min, lon_max, lat_min, lat_max])

    # Increase the figure size (adjust the width and height as needed)
    fig, ax = plt.subplots(figsize=(18, 13), dpi=300)
    
    # Initialize variables for the first point
    prev_lat = track_data["Latitude"].iloc[0]
    prev_lon = track_data["Longitude"].iloc[0]

    # Plot the cyclone track with conditional marker color and default black line color
    for lat, lon, intensity in zip(track_data["Latitude"], track_data["Longitude"], track_data["Intensity"]):
        if intensity > 136:
            marker_color = 'mediumpurple'
        elif intensity > 113:
            marker_color = 'magenta'
        elif intensity > 96:
            marker_color = 'tomato'
        elif intensity > 83:
            marker_color = 'gold'
        elif intensity > 63:
            marker_color = 'lemonchiffon'
        elif intensity > 33:
            marker_color = 'aqua'
        elif intensity > 27:
            marker_color = 'deepskyblue'
        elif intensity > 22:
            marker_color = 'steelblue'
        else:
            marker_color = 'lime'

        ax.plot([prev_lon, lon], [prev_lat, lat], linestyle='-', color='white', linewidth=0.6, zorder=1)
        ax.plot(lon, lat, marker='o', color=marker_color, markersize=9, zorder=2, mec='k')
        prev_lat = lat
        prev_lon = lon

    # Add the title and legend
    observed_start_time = track_data['Synoptic Time'].iloc[0].strftime("%HZ %d-%b-%Y")
    observed_end_time = track_data['Synoptic Time'].iloc[-1].strftime("%HZ %d-%b-%Y")
    update_time = track_data['Synoptic Time'].iloc[-1].strftime("%HZ UTC %d-%b-%Y")
    wind = track_data['Intensity'].iloc[-1]
    mslp = track_data['Pressure'].iloc[-1]

    legend = ax.legend(handles=legend_elements_prev, title='COLOR LEGENDS', loc='upper right')
    legend.get_title().set_fontweight('bold')

    # Add custom text and wind speed info
    cc = ax.text(0.99, 0.01, "© XP WEATHER", fontsize=14, ha="right", va="bottom", color='white', transform=ax.transAxes)
    cc.set_bbox(dict(facecolor='white', alpha=0.4, edgecolor='none'))

    maxtime = max_wind_time.strftime("%HZ %d-%b")

    up = ax.text(0.01, 0.01, f"WIND SPEED: {wind}KT | PRESSURE: {mslp} | {update_time.upper()}", fontsize=14, ha="left", va="bottom", color='white', transform=ax.transAxes)
    up.set_bbox(dict(facecolor='white', alpha=0.4, edgecolor='none'))

    # Define storm category based on cyclone_id
    if 'L' in cyclone_id or 'E' in cyclone_id:
        storm_type = "Hurricane"
    elif 'A' in cyclone_id or 'B' in cyclone_id:
        storm_type = "Cyclone"
    elif 'W' in cyclone_id:
        storm_type = "Typhoon"
    else:
        storm_type = "Storm"  # Default if none of the conditions are met

    # Check if 'Invest' is in the cyclone_name
    if 'Invest' in cyclone_name:
        title_text = f'{storm_type.upper()} {cyclone_id.upper()} TRACK'
    else:
        title_text = f'{storm_type.upper()} "{cyclone_name.upper()}" TRACK'

    # Adjust space between suptitle and title
    ax.set_title(title_text, fontsize=20, fontweight='bold', color='red', x=0.5, y=1.015, fontdict={'horizontalalignment': 'center'})
   
    # Texts
    ax.text(1.00, 1.01, f"PEAK TIME\n{maxtime.upper()}", fontsize=14, ha="right", va="bottom", color='.1', transform=ax.transAxes)
    ax.text(0.00, 1.01, f"MAX WIND: {max_wind}KT\nMIN MSLP: {max_mslp}MB", fontsize=14, ha="left", va="bottom", color='.1', transform=ax.transAxes)

    # Set xlabel with correct indentation
    ax.set_xlabel(f"START: {observed_start_time.upper()} | END: {observed_end_time.upper()}", fontsize='14', fontweight='bold')

    # Add grid lines with opacity 0.5
    ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    
    # Save the plot as an image file (e.g., PNG)
    plt.savefig(f"{cyclone_name}_1M.png", dpi=300, bbox_inches='tight')
    
    ftp = ftplib.FTP('ftpupload.net')
    ftp.login('epiz_32144154', 'Im80K123')
    ftp.cwd('htdocs/tc')
    
    # Upload the plot to the server
    with open(f"{cyclone_name}_1M.png", 'rb') as f:
        ftp.storbinary(f"STOR {cyclone_name.lower()} (1M).jpg", f)

    # Show the plot
    plt.show()

# Create an in-memory bytes buffer
byte_stream = BytesIO()

# Fetch data with SSL verification disabled
response = requests.get('https://www.nrlmry.navy.mil/tcdat/sectors/updated_sector_file', verify=False)

if response.status_code == 200:
    print("Data fetched successfully.\n")

    tc_ids = []  # List to hold all tc_ids

    for line in response.text.splitlines():
        tc_id = line.split()[0]
        if 'al' in tc_id.lower():
            tc_ids.append(tc_id)  # Add the tc_id to the list
            print(f"Processing TC ID: {tc_id}")

            # Construct the URL and fetch data
            url2 = f"https://www.nrlmry.navy.mil/tcdat/tc2024/AL/{tc_id.upper()}/txt/trackfile.txt"
            response2 = requests.get(url2, verify=False)

            if response2.status_code == 200:
                print(f"Data fetched from {url2}.\n")

                # Define column names
                columns = ["Id", "Name", "Date", "Time", "Latitude", "Longitude", "Basin", "Intensity", "Pressure"]
                data = StringIO(response2.text)
                df = pd.read_csv(data, delim_whitespace=True, header=None, names=columns)

                # Process Date and Time columns
                df['Time'] = df['Time'].astype(int).apply(lambda x: f"{x//100:02}:{x%100:02}")
                df['Date'] = df['Date'].astype(str).apply(lambda x: f"20{x[:2]}-{x[2:4]}-{x[4:]}")
                df = df.iloc[::-1].reset_index(drop=True)
                df['Synoptic Time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
                df = df.drop(columns=['Date', 'Time'])

                # Convert Latitude and Longitude to appropriate signs
                df['Latitude'] = df['Latitude'].apply(lambda lat: -float(lat[:-1]) if lat.endswith('S') else float(lat[:-1]))
                df['Longitude'] = df['Longitude'].apply(lambda lon: -float(lon[:-1]) if lon.endswith('W') else float(lon[:-1]))

                # Reorder and filter columns
                df = df[['Id', 'Name', 'Synoptic Time', 'Latitude', 'Longitude', 'Intensity', 'Pressure']]

                # Output cyclone information
                cyclone_name, cyclone_id = df['Name'].iloc[0], df['Id'].iloc[0]
                print(f"Cyclone Name: {cyclone_name} ({cyclone_id})")

                # Save DataFrame to byte stream
                df.to_csv(byte_stream, index=False)
                byte_stream.seek(0)  # Reset the stream for reading

                # Plotting the cyclone track
                plot_cyclone_track(df, cyclone_id)

else:
    print("Failed to fetch data.")
