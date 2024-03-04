import matplotlib.pyplot as plt
import numpy as np
import requests
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import ftplib

today = datetime.today()
up = today.strftime("%d %b %Y")
end = datetime.today() - timedelta(days=2)
end = end.strftime("%d %b %Y")
opn = datetime.today() - timedelta(days=61)
opn = opn.strftime("%d %b %Y")

url = 'https://ds.data.jma.go.jp/tcc/tcc/products/clisys/mjo/figs/olr0-sst1_1990-2020/rmm8.csv'

r = requests.get(url)
open('../MJO Data.csv', 'wb').write(r.content)
dl = pd.read_csv('../MJO Data.csv')


#dy = df['#year'].iloc[-1]
#dl = df[df['#year'] == dy]
df = dl.iloc[-60:]


x = df.iloc[:, 6]
y = df.iloc[:, 7]
z = df.iloc[:, 2]


xa = x.iloc[:1]
xb = y.iloc[:1]
ya = x.iloc[-1:]
yb = y.iloc[-1:]
 

employee = ["EAST 1", "", "WEST 1", ""]

font1 = {'family':'serif','color':'purple','size':20, 'weight':'bold'}
font2 = {'family':'serif','color':'blue','size':20}

 
a = [2, 3, 2 ,3, 2, 3, 2, 3]
b = [0, 0, 90, 90, 180, 180, 270, 270]
  
x = [x/180.0*3.141593 for x in x]
b = [x/180.0*3.141593 for x in b]
xa = [x/180.0*3.141593 for x in xa]
ya = [x/180.0*3.141593 for x in ya]

fig = plt.figure(figsize=(12, 13), dpi=300)
ax = fig.add_subplot(polar = True)
ax.set_theta_zero_location("S")
ax.set_ylim(0, 4)
ax.xaxis.grid(True, color='k', linestyle='-')
ax.yaxis.grid(True, color='k', linestyle='-', lw='1.2')
ax.set_yticks(np. arange(2))

lines, labels = plt.thetagrids(range(0, 360, int(360/len(employee))), (employee), fontsize=16)

plt.plot(x, y, c ='green', marker='o', linewidth='1')
plt.plot(xa, xb, c ='blue', marker='o', label='START')
plt.plot(ya, yb, c ='red', marker='o', label='STOP')

plt.suptitle('Madden–Julian Oscillation', fontsize = 30, color = 'red', fontweight = 'bold')
ax.set_title('Analysis From ' +str(opn)+ ' To ' +str(end)+'\n', fontdict = font1)
ax.legend(title='Xp Weather', title_fontsize=15)
ax.set_xlabel("\nMJO Modifed Phase", fontdict = font2)
#ax.set_ylabel("WEST 2", fontsize=15)
ax.text(7.839, 4.456, "EAST 2", fontsize=16, ha="center", color='black')
ax.text(4.727, 4.46, "WEST 2", fontsize=16, ha="center", color='black')
ax.text(5.70, 6.25, "Last Update: " +str(up), fontsize=20, ha="center", color='black')



for a, b in zip(a, b):
    label = "{:}".format(a)
    plt.annotate(label, (b, a), textcoords="offset points", xytext=(2,0),
                 ha='left',
                 color='black',
                 fontsize=15)
                 


plt.savefig("../MJO Index.jpg", transparent = True)

ftp = ftplib.FTP('ftpupload.net')
ftp.login('epiz_32144154', 'Im80K123')
ftp.cwd('htdocs/wx')

# Upload the plot to the server
with open('../MJO Index.jpg', 'rb') as f:
    ftp.storbinary('STOR mjo.jpg', f)

# Close the connection to the server
ftp.quit() 
plt.show()
