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
    # Define conditions and corresponding colors for cyclone categories
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

    # Increase the figure size
    fig, ax = plt.subplots(figsize=(15, 10), dpi=300)

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


    # Define latitude and longitude limits
    last_lat = track_data["Latitude"].iloc[-1] - 3
    last_lon = track_data["Longitude"].iloc[-1] + 3
    ax.set_xlim(last_lon - 10, last_lon + 10)
    ax.set_ylim(last_lat - 10, last_lat + 10)
    ax.imshow(background_image, extent=[-180, 180, -90, 90])

    # Plot the cyclone track with conditional marker color
    prev_lat = track_data["Latitude"].iloc[0]
    prev_lon = track_data["Longitude"].iloc[0]

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
    observed_start_time = pd.to_datetime(track_data['Synoptic Time'].iloc[0]).strftime("%HZ %d-%b-%Y")
    observed_end_time = pd.to_datetime(track_data['Synoptic Time'].iloc[-1]).strftime("%HZ %d-%b-%Y")
    ax.set_title(f"Formed: {observed_start_time} | Latest: {observed_end_time}", fontsize=13, fontweight='bold', x=0.475)

    legend = ax.legend(handles=legend_elements_prev, title='COLOR LEGENDS', loc='upper right')
    legend.get_title().set_fontweight('bold')

    # Add additional information
    max_wind_time = track_data['Synoptic Time'].iloc[track_data['Intensity'].idxmax()]
    max_wind = track_data['Intensity'].max()
    ax.text(0.99, 0.01, f"MAX WIND SPEED: {max_wind}KT | {max_wind_time.strftime('%HZ UTC - %d %b %Y')}", fontsize=14, ha="right", va="bottom", color='white', transform=ax.transAxes)

    # Save the plot as an image file
    plot_filename = f"{cyclone_name}_1M.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    
    # Upload to FTP
    try:
        ftp = ftplib.FTP('ftpupload.net')
        ftp.login('epiz_32144154', 'Im80K123')
        ftp.cwd('htdocs/tc')
        with open(plot_filename, 'rb') as f:
            ftp.storbinary(f"STOR {cyclone_name.lower()} (1M).jpg", f)
        print(f"Uploaded {plot_filename} to FTP server.")
    except Exception as e:
        print(f"Error uploading file: {e}")
    finally:
        ftp.quit()  # Ensure FTP session is closed
    
    # Clean up the local file
    os.remove(plot_filename)

    plt.close()

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
