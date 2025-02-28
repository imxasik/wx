import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
import requests
from io import StringIO
import ftplib
import io

# Function to fetch and parse RMM data from NOAA
def fetch_rmm_data():
    url = "https://psl.noaa.gov/mjo/mjoindex/vpm.1x.txt"
    try:
        response = requests.get(url)
        data = response.text
        lines = data.splitlines()[1:]  # Skip first header line
        dates, rmm1, rmm2 = [], [], []
        for line in lines:
            cols = line.split()
            if len(cols) >= 7:
                dates.append(f"{cols[2]}-{cols[1]}-{cols[0]}")
                rmm1.append(float(cols[4]))  # RMM2 as RMM1
                rmm2.append(float(cols[5]))  # RMM3 as RMM2
        return np.array(dates), np.array(rmm1), np.array(rmm2)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None, None

# Fetch the data
dates, rmm1, rmm2 = fetch_rmm_data()

# Fallback sample data if fetch fails
if dates is None or len(dates) == 0:
    print("Fetch failed, using sample data instead.")
    dates = ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04", "2025-01-05"]
    rmm1 = [1.0, 1.5, 0.5, -0.5, -1.0]
    rmm2 = [0.5, 1.0, 1.5, 1.0, 0.0]
else:
    print(f"Successfully fetched {len(dates)} data points.")

# Limit to last 40 days
if len(dates) > 40:
    dates = dates[-40:]
    rmm1 = rmm1[-40:]
    rmm2 = rmm2[-40:]

# Flip RMM1 horizontally
rmm1 = -rmm1

# Define start and end points
start_date, end_date = dates[0], dates[-1]

# Create figure with a subtle gradient background
fig, ax = plt.subplots(figsize=(8, 8), facecolor='#f0f2f5')
ax.set_facecolor('#f7f9fc')

# Gradient trajectory line
points = np.array([rmm1, rmm2]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
norm = plt.Normalize(0, len(rmm1)-1)
lc = LineCollection(segments, cmap='viridis', norm=norm, linewidth=1.0, alpha=0.8)
lc.set_array(np.arange(len(rmm1)))
ax.add_collection(lc)

# Scatter points with edge
plt.scatter(rmm1, rmm2, c=np.arange(len(rmm1)), cmap='viridis', s=40, edgecolor='k', linewidth=0.5, zorder=5)

# Mark start and end points
plt.scatter(rmm1[0], rmm2[0], c='limegreen', s=100, marker='*', edgecolor='k', label=f'Start: {start_date}', zorder=10)
plt.scatter(rmm1[-1], rmm2[-1], c='crimson', s=100, marker='X', edgecolor='k', label=f'End: {end_date}', zorder=10)

# Grid lines and unit circle
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=1.0)
ax.axvline(0, color='gray', linestyle='--', linewidth=0.8, alpha=1.0)
for i in [-3, -2, -1, 1, 2, 3]:
    ax.axhline(i, color='gray', linestyle='--', linewidth=0.5, alpha=0.3)
    ax.axvline(i, color='gray', linestyle='--', linewidth=0.5, alpha=0.3)
circle = plt.Circle((0, 0), 1, color='black', fill=False, linestyle='-', linewidth=1.0, alpha=0.7)
ax.add_artist(circle)

# Phase boundaries
ax.plot([-4, 4], [4, -4], 'k--', linewidth=0.8, alpha=0.5)
ax.plot([-4, 4], [-4, 4], 'k--', linewidth=0.8, alpha=0.5)

# Label MJO phases with shadow effect
for x, y, label in [(-3.5, -1.5, '1'), (-1.5, -3.5, '2'), (1.5, -3.5, '3'), 
                    (3.5, -1.5, '4'), (3.5, 1.5, '5'), (1.5, 3.5, '6'), 
                    (-1.5, 3.5, '7'), (-3.5, 1.5, '8')]:
    ax.text(x, y, label, fontsize=12, ha='center', color='darkblue', weight='bold',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))

# Add region labels with elegant styling
ax.text(0, -3.8, 'INDIAN OCEAN', fontsize=10, ha='center', color='teal', fontstyle='italic', va='center')
ax.text(3.8, 0, 'MARITIME CONTINENT', fontsize=10, rotation=90, ha='center', color='teal', fontstyle='italic', va='center')
ax.text(0, 3.8, 'WESTERN PACIFIC', fontsize=10, ha='center', color='teal', fontstyle='italic', va='center')
ax.text(-3.8, 0, 'WEST HEMP & AFRICA', fontsize=10, rotation=90, ha='center', color='teal', fontstyle='italic', va='center')

# Set limits and labels with professional font
ax.set_xlim(-4, 4)
ax.set_ylim(-4, 4)
ax.set_xlabel('RMM1', fontsize=12, color='navy')
ax.set_ylabel('RMM2', fontsize=12, color='navy')

# Title with a box
title = ax.set_title(f'[RMM1, 2] MJO PHASE FROM {start_date} TO {end_date}', fontsize=14, weight='bold', color='navy', pad=12,
                     bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.5', alpha=0.9))
                     
cc = ax.text(0.99, 0.01, "© XP WEATHER", fontsize=10, ha="right", va="bottom", color='white', transform=ax.transAxes)
cc.set_bbox(dict(facecolor='black', alpha=0.3, edgecolor='none'))

# Improve spacing
plt.tight_layout()

# Save the plot to a BytesIO buffer
plot_buffer = io.BytesIO()
plt.savefig(plot_buffer, format="jpg", transparent=True,  dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
plot_buffer.seek(0)

# FTP Server Details
ftp_host = "ftpupload.net"
ftp_username = "epiz_32144154"
ftp_password = "Im80K123"

    # Connect to the FTP server and upload the plot directly
with ftplib.FTP(ftp_host) as ftp:
        ftp.login(ftp_username, ftp_password)
        ftp.cwd('htdocs/wx')  # Change directory to your desired location on the FTP server
        ftp.storbinary('STOR mjo.jpg', plot_buffer)
        plt.show()
