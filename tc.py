import requests
import pandas as pd
from io import StringIO, BytesIO
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
import ftplib


# Initialize a list to hold all DataFrames
datasets = []

# Initialize a byte stream to hold the CSV data
csv_byte_stream = BytesIO()

# Fetch data with SSL verification disabled
response = requests.get('https://www.nrlmry.navy.mil/tcdat/sectors/updated_sector_file', verify=False)

if response.status_code == 200:
    print("Data fetched successfully.\n")

    # Iterate through each line and extract first column values containing 'al'
    for line in response.text.splitlines():
        first_col = line.split()[0]  # Split by any whitespace to get the first column
        if 'al' in first_col.lower():
            print(f"Processing first column: {first_col}")
            cyclone_id = {first_col}
            # Create the new URL using first_col and convert to uppercase as needed
            url2 = f"https://www.nrlmry.navy.mil/tcdat/tc2024/AL/{first_col.upper()}/txt/trackfile.txt"

            # Fetch data from the second URL
            response2 = requests.get(url2, verify=False)

            if response2.status_code == 200:
                print(f"Data fetched from {url2}.\n")

                # Define the column names
                columns = ["Id", "Name", "Date", "Time", "Latitude", "Longitude", "Basin", "Intensity", "Pressure"]

                # Load the text data into a pandas dataframe
                data = StringIO(response2.text)
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

                # Append the DataFrame to the datasets list
                datasets.append(df)

                # Write the processed DataFrame to the byte stream
                df.to_csv(csv_byte_stream, index=False)

                # Reset the stream position to the beginning
                csv_byte_stream.seek(0)
    

# Allow larger images
Image.MAX_IMAGE_PIXELS = None


# Function to fetch and process cyclone data
def fetch_and_process_data(cyclone_id):
    url = f"https://www.nrlmry.navy.mil/tcdat/tc2024/AL/{cyclone_id}/txt/trackfile.txt"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch data for {cyclone_id}: {e}")
        return None
        
        # Load data into DataFrame
    data = StringIO(response.text)
    columns = ["Id", "Name", "Date", "Time", "Latitude", "Longitude", "Basin", "Intensity", "Pressure"]
    df = pd.read_csv(data, delim_whitespace=True, header=None, names=columns)

    # Process Date and Time
    df['Time'] = df['Time'].astype(int).apply(lambda x: f"{x//100:02}:{x%100:02}")
    df['Date'] = df['Date'].astype(str).apply(lambda x: f"20{x[:2]}-{x[2:4]}-{x[4:]}")
    df = df.iloc[::-1].reset_index(drop=True)
    df['Synoptic Time'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
    df['Latitude'] = df['Latitude'].apply(lambda x: -float(x[:-1]) if x.endswith('S') else float(x[:-1]))
    df['Longitude'] = df['Longitude'].apply(lambda x: -float(x[:-1]) if x.endswith('W') else float(x[:-1]))

    return df
    
    
    # Function to plot the Cyclone Track
def plot_cyclone_track(track_data, cyclone_id):
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
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)

    # Load and downscale the background image
    img = Image.open("../TCs/map.jpg")
    img = img.resize((int(img.width / 2), int(img.height / 2)), Image.Resampling.LANCZOS)  # Downscale by 2x
    background_image = np.array(img)

    # Define the latitude and longitude limits
    lat_min, lat_max = -90, 90
    lon_min, lon_max = -180, 180


    # Get the last latitude and longitude values for adjusting limits
    last_lat = track_data["Latitude"].iloc[-1]
    last_lon = track_data["Longitude"].iloc[-1]

    # Set the latitude and longitude limits based on the last values with a buffer
    ax.set_xlim(last_lon - 10, last_lon + 10)
    ax.set_ylim(last_lat - 10, last_lat + 10)

    # Set the extent of the background image
    ax.imshow(background_image, extent=[lon_min, lon_max, lat_min, lat_max])

    # Initialize variables for the first point
    prev_lat = track_data["Latitude"].iloc[0]
    prev_lon = track_data["Longitude"].iloc[0]

    # Plot the cyclone track with conditional marker color
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

        ax.plot([prev_lon, lon], [prev_lat, lat], linestyle='-', color='white', linewidth=0.7, zorder=1)
        ax.plot(lon, lat, marker='o', color=marker_color, markersize=8, zorder=2, mec='k')
        prev_lat, prev_lon = lat, lon

    # Add title and legend
    observed_start_time = track_data['Synoptic Time'].iloc[0].strftime("%HZ %d-%b-%Y")
    observed_end_time = track_data['Synoptic Time'].iloc[-1].strftime("%HZ %d-%b-%Y")

    title = f"Formed: {observed_start_time} | Latest: {observed_end_time}"
    ax.set_title(title, fontsize=13, fontweight='bold', x=0.475, fontdict={'horizontalalignment': 'center'})

    legend = ax.legend(handles=legend_elements_prev, title='COLOR LEGENDS', loc='upper right')
    legend.get_title().set_fontweight('bold')

    # Add custom text and wind speed info
    cc = ax.text(0.99, 0.01, "© XP WEATHER", fontsize=14, ha="right", va="bottom", color='white', transform=ax.transAxes)
    cc.set_bbox(dict(facecolor='white', alpha=0.4, edgecolor='none'))

    # Max wind speed information (this assumes you've calculated max_wind and max_wind_time)
    max_wind = track_data['Intensity'].max()  # Update this logic as per your calculation
    max_wind_time = track_data.loc[track_data['Intensity'].idxmax(), 'Synoptic Time']  # Get time for max wind
    maxtime = max_wind_time.strftime("%HZ UTC - %d %b %Y")

    up = ax.text(0.01, 0.01, f"MAX WIND SPEED: {max_wind}KT | {maxtime}", fontsize=14, ha="left", va="bottom", color='white', transform=ax.transAxes)
    up.set_bbox(dict(facecolor='white', alpha=0.4, edgecolor='none'))

    # Determine storm type
    cyclone_name = track_data["Name"].iloc[0]  # Get cyclone name for title
    if 'L' in cyclone_id or 'E' in cyclone_id:
        storm_type = "Hurricane"
    elif 'A' in cyclone_id or 'B' in cyclone_id:
        storm_type = "Cyclone"
    elif 'W' in cyclone_id:
        storm_type = "Typhoon"
    else:
        storm_type = "Storm"  # Default if none of the conditions are met

    # Set the main title
    title_text = f'Xp Weather {storm_type} "{cyclone_name.upper()}" Track'
    plt.suptitle(title_text, fontsize=20, color='red', fontweight='bold', y=0.945)

    # Set xlabel and grid lines
    ax.set_xlabel("(1-MINUTE SUSTAINED WIND SCALE)")
    ax.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.5)

    # Save the plot as an image file
    plot_file_name = os.path.join(base_dir, f"{cyclone_name}_1M.png")
    plt.savefig(plot_file_name, dpi=300, bbox_inches='tight')

    # Upload to FTP server
    ftp = ftplib.FTP('ftpupload.net')
    ftp.login('epiz_32144154', 'Im80K123')
    ftp.cwd('htdocs/tc')
    
    # Upload the plot to the server
    with open(plot_file_name, 'rb') as f:
        ftp.storbinary(f"STOR {cyclone_name.lower()} (1M).jpg", f)
    ftp.quit()

# Main execution
for cyclone_id in cyclone_id:
    print(f"Processing data for {cyclone_id}...")
    cyclone_data = fetch_and_process_data(cyclone_id)

    if cyclone_data is not None:
        data_files[cyclone_id] = cyclone_data
        plot_cyclone_track(cyclone_data, cyclone_id)

print("All cyclone data processed and plots generated.")
