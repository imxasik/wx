import matplotlib.pyplot as plt
import pandas as pd
import ftplib
import io

# Read data from the provided URL
df = pd.read_csv("https://data.longpaddock.qld.gov.au/SeasonalClimateOutlook/SouthernOscillationIndex/SOIDataFiles/DailySOI1933-1992Base.txt", sep='\s+')

df['date'] = pd.to_datetime(df['Day'], format='%j')
df['DM'] = df['date'].dt.strftime('%d %b')

dl = df.tail(25)

x = dl['DM']
y = dl['SOI']

z = y_moving_avg = y.rolling(window=7).mean()

fig = plt.figure(figsize=(13, 9), dpi=300)
ax = fig.add_subplot()

font1 = {'family': 'serif', 'color': 'purple', 'size': 15, 'weight': 'bold'}
font2 = {'family': 'serif', 'color': 'blue', 'size': 15}

ax.plot(x, z, '-o', label='SOI 7MA')
plt.suptitle('Daily Based Southern Oscillation Index', fontsize=20, color='red', fontweight='bold')
ax.set_title(f"7 Days Moving Average Data For Last 25 Days", fontdict=font1)
ax.legend(title='Xp Weather', title_fontsize=15)
ax.set_xlabel("\nDay Of Month (DOM)", fontdict=font2)
ax.set_ylabel("Moving Mean Value (MA)", fontdict=font2)

plt.text(0.99, 0.01, "Made by http://fb.com/xpweather", fontsize=12, ha="right", va="bottom", color='.4', zorder=-1, transform=plt.gca().transAxes)

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
    ftp.storbinary('STOR soi7ma.jpg', plot_buffer)

plt.show()
