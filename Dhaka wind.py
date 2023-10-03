import matplotlib.pyplot as plt
import pandas as pd
import ftplib
import io

url = 'https://metar-taf.com/history/VGHS'
un = 'Dhaka'

df_list = pd.read_html(url)
df = df_list[-1]

dl = df.iloc[2:21]
dt = df.head(5)

x = dl.iloc[::-1, 0]
y = dl.iloc[::-1, 7]

dd = dt.iloc[0, 3]

fig = plt.figure(figsize=(15, 12), dpi=300)
ax = fig.add_subplot()

font1 = {'family': 'serif', 'color': 'purple', 'size': 15, 'weight': 'bold'}
font2 = {'family': 'serif', 'color': 'blue', 'size': 15}

ax.plot(x, y, '-o', label=str(un) + ' Temp', color='blue', lw='0.8')

ax.grid(True)

plt.suptitle(str(un) + ' Weather Observation Data', fontsize=20, color='red', fontweight='bold')

ax.set_title('Data For: ' + str(dd) + '\n', fontdict=font1)
ax.legend(title='Xp Weather', title_fontsize=15)
ax.set_xlabel("\nTime Frame", fontdict=font2)
ax.set_ylabel("Temp Value (C)", fontdict=font2)

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
    ftp.storbinary(f'STOR {un}wind.jpg'.format(un), plot_buffer)

plt.show()
