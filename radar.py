import requests
import re
import io
import matplotlib.pyplot as plt
import ftplib

# URL of the website
url = "https://data.rainviewer.com/images/BDCOMP/"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Use regular expressions to find the links that end with "source.jpeg"
pattern = r'<a\s+href="([^"]*source\.jpeg)"[^>]*>'
matches = re.findall(pattern, response.text)
if matches:
    latest_source_link = matches[-1]
    latest_source_url = url + latest_source_link

    # Download the latest source.jpeg
    file_content = requests.get(latest_source_url).content

    # Save the downloaded file
    with open("mos.jpg", "wb") as f:
        f.write(file_content)
    print("Latest source.jpeg downloaded successfully.")

    # Plot your data
    # Assuming you have already created a plot here

    # Save the plot to a buffer
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
        ftp.cwd('htdocs/radar')  # Change directory to your desired location on the FTP server
        ftp.storbinary('STOR com.jpg', plot_buffer)
        print("Plot uploaded successfully to FTP server.")
else:
    print("No source.jpeg files found on the website.")
