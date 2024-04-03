import requests
import io
import matplotlib.pyplot as plt
import ftplib
from bs4 import BeautifulSoup

# URL of the website
url = "https://data.rainviewer.com/images/BDCOMP/"

# Send an HTTP GET request to the URL
response = requests.get(url)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Find all anchor tags with href attribute ending with "source.jpeg"
anchor_tags = soup.find_all('a', href=lambda href: href and href.endswith("source.jpeg"))

if anchor_tags:
    latest_source_link = anchor_tags[-1]['href']
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
