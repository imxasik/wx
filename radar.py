import requests
import io
from ftplib import FTP

# Step 1: Define the URL of the image
image_url = 'https://wx.baf.mil.bd/METBSR/images/omar/RadarSingle/mtr.jpg'

try:
    # Step 2: Download the image with SSL verification disabled
    response = requests.get(image_url, verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the image temporarily in memory
        image_data = io.BytesIO(response.content)

        # FTP Server Details
        ftp_host = "ftpupload.net"
        ftp_username = "epiz_32144154"
        ftp_password = "Im80K123"
        ftp_target_path = "htdocs/wx/mtr.jpg"  # Adjust the path as needed

        # Step 3: Upload the image to your hosting server using FTP
        with FTP(ftp_host) as ftp:
            ftp.login(ftp_username, ftp_password)
            ftp.cwd('htdocs/wx')  # Change directory to your desired location on the FTP server
            ftp.storbinary('STOR mtr.jpg', image_data)

        print("Image uploaded successfully.")
    else:
        print("Failed to fetch the image from the website. Status code:", response.status_code)
except requests.exceptions.RequestException as e:
    print("Failed to fetch the image from the website. Error:", e)
    
