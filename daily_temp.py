import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import detrend
import requests
import io
import ftplib

# Define URL and custom headers
url = 'https://climatlas.com/temperature/jra55/JRA55_global_1958_2023.csv'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}

# Send a GET request with custom headers
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Load the data from the response content
    df = pd.read_csv(io.StringIO(response.text), names=['Date', 'Temp', 'Ta'])

    # Convert the 'Date' column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Group data by date and calculate daily mean temperature
    daily_mean = df.groupby(df['Date'].dt.date)['Ta'].mean()
    
    # Select only the latest 90 days of data
    data = daily_mean.iloc[-180:]
    
    # Detrend the data
    data_dt = detrend(data.values)
    
    # Design Part start from here
    fig = plt.figure(figsize=(11, 8), dpi=300)
    ax = fig.add_subplot()

    font1 = {'family':'serif','color':'purple','size':15, 'weight':'bold'}
    font2 = {'family':'serif','color':'blue','size':15}

    # Plotting
    ax.plot(data.index, data.values, '-o', label='Daily Trend Mean', color='black', linewidth=0.9, markersize=5)
    ax.plot(data.index, data_dt, '-o', label='Daily Detrend Mean', color='brown', linewidth=0.9, markersize=5)
    
    # Title and labels
    plt.suptitle('2-Meter Global Temperature Anomaly', fontsize=20, color='red', fontweight='bold') 
    ax.set_title(f"Daily Trend: {data.iloc[-1]:.2f}°C | Daily Detrend: {data_dt[-1]:.2f}°C", fontsize=14, fontname='serif')
    ax.set_xlabel(f"\nData From {data.index[0]} To {data.index[-1]}", fontdict=font2)
    ax.set_ylabel("Temperature Anomaly(°C)", fontdict=font2)
    
    # Texts
    ax.text(1.00, 1.01, "(1990-2020 Climo)", fontsize=14, ha="right", va="bottom", color='.1', transform=ax.transAxes)
    ax.text(0.00, 1.01, "JRA-JRA55-3Q", fontsize=14, ha="left", va="bottom", color='.1', transform=ax.transAxes)
    plt.text(0.99, 0.01, "Made by http://fb.com/xpweather", fontsize=12, ha="right", va="bottom", color='.4', zorder=-1, transform=plt.gca().transAxes)
    
    # Set xlim without padding and extend the right limit slightly
    ax.set_xlim(data.index[0], data.index[-1] + pd.Timedelta(days=1))
    
    # Legend
    ax.legend()
    
    # Customize grid lines
    ax.grid(True, linewidth=0.6, linestyle='--', color='gray')
    
    # Add horizontal line at y=0
    ax.axhline(0, color='gray', linewidth=1.0)
    
    # Improve spacing
    plt.tight_layout()
    
    # Save the plot to a BytesIO buffer
    plot_buffer = io.BytesIO()
    plt.savefig(plot_buffer, format="jpg", transparent=True)
    plot_buffer.seek(0)

    # FTP Server Details
    ftp_host = "ftpupload.net"
    ftp_username = "epiz_32144154"
    ftp_password = "Im80K123"

    # Connect to the FTP server and upload the plot directly
    with ftplib.FTP(ftp_host) as ftp:
        ftp.login(ftp_username, ftp_password)
        ftp.cwd('htdocs/wx')  # Change directory to your desired location on the FTP server
        ftp.storbinary('STOR dt.jpg', plot_buffer)

    plt.show()
else:
    print("Failed to fetch data from the website. Status code:", response.status_code)
