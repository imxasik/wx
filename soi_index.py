import pandas as pd
import matplotlib.pyplot as plt
import requests
import io

# Define URL and custom headers
url = 'https://data.longpaddock.qld.gov.au/SeasonalClimateOutlook/SouthernOscillationIndex/SOIDataFiles/DailySOI1933-1992Base.txt'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}

# Send a GET request with custom headers
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Load the data from the response content
    df = pd.read_csv(io.StringIO(response.text), sep='\s+')

    # Convert the 'Date' column to datetime format
    # Convert the 'Year' and 'Day' columns to datetime format
    df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Day'].astype(str), format='%Y-%j')
    df['DM'] = df['Date'].dt.strftime('%d-%m')

    # Calculate moving averages
    df['7-Day Mean'] = df['SOI'].rolling(window=7).mean()
    df['30-Day Mean'] = df['SOI'].rolling(window=30).mean()
    df['90-Day Mean'] = df['SOI'].rolling(window=90).mean()

    # Select the last 25 data points
    df = df.tail(20)

    # Design Part start from here
    fig = plt.figure(figsize=(12, 8), dpi=300)
    ax = fig.add_subplot()

    font1 = {'family': 'serif', 'color': 'purple', 'size': 15, 'weight': 'bold'}
    font2 = {'family': 'serif', 'color': 'blue', 'size': 15}

    # Plotting
    ax.plot(df['DM'], df['7-Day Mean'], '-o', label='7-Day Mean', color='black', linewidth=1.0, markersize=5)
    ax.plot(df['DM'], df['30-Day Mean'], '-', label='30-Day Mean', color='blue', linewidth=1.2, markersize=5)
    ax.plot(df['DM'], df['90-Day Mean'], '--', label='90-Day Mean', color='red', linewidth=1.5, markersize=6)

    # Title and labels
    plt.suptitle('Southern Oscillation Index (SOI) Anomaly', fontsize=20, color='red', fontweight='bold')
    ax.set_title(f"Weekly Mean: {df['7-Day Mean'].iloc[-1]:.2f} | Monthly Mean: {df['30-Day Mean'].iloc[-1]:.2f} | Seasonal Mean: {df['90-Day Mean'].iloc[-1]:.2f}", fontsize=14, fontname='serif')
    ax.set_xlabel(f"\nData From {df['Date'].iloc[0].strftime('%d %B %Y')} To {df['Date'].iloc[-1].strftime('%d %B %Y')}", fontdict=font2)
    ax.set_ylabel("SOI Values", fontdict=font2)

    # Texts
    ax.text(1.00, 1.01, "(1933-1992 Climo)", fontsize=14, ha="right", va="bottom", color='.1', transform=ax.transAxes)
    ax.text(0.00, 1.01, "BOM-QLD", fontsize=14, ha="left", va="bottom", color='.1', transform=ax.transAxes)
    plt.text(0.99, 0.01, "Made by http://fb.com/xpweather", fontsize=12, ha="right", va="bottom", color='.4', zorder=-1, transform=plt.gca().transAxes)

    # Set xlim without padding and extend the right limit slightly
    ax.set_xlim(df['DM'].iloc[0], df['DM'].iloc[-1])

    # Legend
    ax.legend()

    # Customize grid lines
    ax.grid(True, linewidth=0.6, linestyle='--', color='gray')

    # Add horizontal line at y=0
    ax.axhline(0, color='gray', linewidth=1.0)

    # Improve spacing
    plt.tight_layout()

    # Save and show plot
    plt.savefig("../Plot Files/Daily SOI.jpg", transparent=True)
    plt.show()

else:
    print("Failed to fetch data from the website. Status code:", response.status_code)
