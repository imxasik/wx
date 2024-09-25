import requests
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from PIL import Image
import io
import ftplib

Image.MAX_IMAGE_PIXELS = 300000000

# Step 1: Fetch and Process Cyclone Data (Without saving to a CSV file)

# URL of the data
url = "https://www.nrlmry.navy.mil/tcdat/tc2024/EP/EP102024/txt/trackfile.txt"

# Disable SSL certificate verification and fetch the data
response = requests.get(url, verify=False)

# Define the column names
columns = ["Id", "Name", "Date", "Time", "Latitude", "Longitude", "Basin", "Intensity", "Pressure"]

# Load the text data into a pandas dataframe
if response.status_code == 200:
    data = StringIO(response.text)
    df = pd.read_csv(data, delim_whitespace=True, header=None, names=columns)

    # Ensure Time column is in the format 'HH:MM'
    df['Time'] = df['Time'].astype(int).apply(lambda x: f"{x//100:02}:{x%100:02}")

    # Convert Date column from YYMMDD to YYYY-MM-DD
    df['Date'] = df['Date'].astype(str).apply(lambda x: f"20{x[:2]}-{x[2:4]}-{x[4:]}")

    # Invert the DataFrame
    df = df.iloc[::-1].reset_index(drop=True)

    # Combine Date and Time into a new Synoptic Time column
    df['Synoptic Time'] = df['Date'] + ' ' + df['Time']

    # Drop the original Date and Time columns
    df = df.drop(columns=['Date', 'Time'])

    # Convert Latitude and Longitude to appropriate signs
    def convert_latitude(lat):
        return -float(lat[:-1]) if lat.endswith('S') else float(lat[:-1])

    def convert_longitude(lon):
        return -float(lon[:-1]) if lon.endswith('W') else float(lon[:-1])

    df['Latitude'] = df['Latitude'].apply(convert_latitude)
    df['Longitude'] = df['Longitude'].apply(convert_longitude)

    # Reorder the columns to exclude Name and Basin
    df = df[['Id', 'Name', 'Synoptic Time', 'Latitude', 'Longitude', 'Intensity', 'Pressure']]

    # Get the cyclone name and Id value
    cyclone_name = df['Name'].iloc[0]  # Get the cyclone name (first entry)
    cyclone_id = df['Id'].iloc[0]      # Get the cyclone Id (first entry)

    print(f"Cyclone Name: {cyclone_name} ({cyclone_id})")

    # Step 2: Use in-memory data instead of CSV for plotting
    # Convert the DataFrame to a CSV format in memory (using StringIO) without saving to disk
    buffer = StringIO()
    df.to_csv(buffer, sep=',', index=False)
    buffer.seek(0)

    # Read the in-memory CSV data for further processing (to avoid saving a CSV file)
    cyclone_data = buffer.getvalue()

    # Create a DataFrame from the in-memory CSV content
    track_data = pd.read_csv(StringIO(cyclone_data))

    # Convert Synoptic Time to datetime for plotting
    track_data['Synoptic Time'] = pd.to_datetime(track_data['Synoptic Time'])

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

    # Increase the figure size (adjust the width and height as needed)
    fig, ax = plt.subplots(figsize=(18, 12), dpi=300)

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
    first_lat = track_data["Latitude"].iloc[1]
    last_lat = track_data["Latitude"].iloc[-1]
    last_lon = track_data["Longitude"].iloc[-1]
    first_lon = track_data["Longitude"].iloc[1]
    # Set the latitude and longitude limits based on the last values with a buffer
    ax.set_xlim(last_lon - 4, first_lon + 4)
    ax.set_ylim(first_lat - 1, last_lat + 2)

    # Set the extent of the background image
    ax.imshow(background_image, extent=[lon_min, lon_max, lat_min, lat_max])

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

    title = f"{observed_start_time.upper()} | {observed_end_time.upper()}"
    ax.set_title(title, fontsize=14, fontweight='bold', x=0.475, y=1.005, fontdict={'horizontalalignment': 'center'})

    legend = ax.legend(handles=legend_elements_prev, title='COLOR LEGENDS', loc='upper right')
    legend.get_title().set_fontweight('bold')

    # Add custom text and wind speed info
    cc = ax.text(0.99, 0.01, "© XP WEATHER", fontsize=14, ha="right", va="bottom", color='white', transform=ax.transAxes)
    cc.set_bbox(dict(facecolor='white', alpha=0.4, edgecolor='none'))

    maxtime = max_wind_time.strftime("%HZ %d-%b-%Y")

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
    plt.suptitle(title_text, fontsize=20, color='red', fontweight='bold', y=0.935)

     # Texts
    ax.text(1.00, 1.01, f"PEAK TIME\n{maxtime.upper()}", fontsize=14, ha="right", va="bottom", color='.1', transform=ax.transAxes)
    ax.text(0.00, 1.01, f"MAX WIND: {max_wind}KT\nMIN MSLP: {max_mslp}MB", fontsize=14, ha="left", va="bottom", color='.1', transform=ax.transAxes)

    # Set xlabel with correct indentation
    ax.set_xlabel(f"(1-MINUTE SUSTAINED WIND SCALE)")

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

else:
    print(f"Failed to retrieve data from the URL. Status code: {response.status_code}")
