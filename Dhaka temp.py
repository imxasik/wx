import requests
import pandas as pd
import matplotlib.pyplot as plt

url = 'https://metar-taf.com/history/VGHS'
un = 'Dhaka'

df_list = pd.read_html(url)
df = df_list[-1]

dl = df.iloc[2:21]
dt = df.head(5)

x = dl.iloc[: :-1, 0]
y = dl.iloc[: :-1, 3]

yya = dl.iloc[:, 3].min()
xxa = dl[dl.iloc[:, 3] == yya]
xxxa= xxa.iloc[-1:, 0]

yyb = dl.iloc[:, 3].max()
xxb = dl[dl.iloc[:, 3] == yyb]
xxxb= xxb.iloc[-1:, 0]

#xtxt = dl.iloc[:1, 1]
#ytxt = dl.iloc[-1:, 3]
dd = dt.iloc[0, 3]


#dl.to_csv('Teknaf.csv')

fig = plt.figure(figsize=(15, 12))
ax = fig.add_subplot()

#ax.set_xlim(limb, lime)

font1 = {'family':'serif','color':'purple','size':15, 'weight':'bold'}
font2 = {'family':'serif','color':'blue','size':15}


ax.plot(x, y, '-o', label = str(un)+ ' Temp', color='blue', lw ='0.8')
ax.plot(xxxa, yya, '-o', label='Min Temp', color='green')
ax.plot(xxxb, yyb, '-o', label='Max Temp', color='red')

ax.grid(True)

#ax.axvline(90, color='grey', linestyle='-', lw = '1')


plt.suptitle(str(un)+ ' Weather Observation Data', fontsize = 20, color = 'red', fontweight = 'bold')

ax.set_title('Data For: ' +str(dd)+ '\n', fontdict = font1)

ax.legend(title='Xp Weather', title_fontsize=15)
ax.set_xlabel("\nTime Frame", fontdict = font2)
ax.set_ylabel("Temp Value (C)", fontdict = font2)
      
             
#ax.text(xtxt, ytxt, "Made by http://fb.com/xpweather", fontsize=12, ha="right", color='.4')


plt.savefig("../"+str(un)+ " Temp.jpg", transparent = True)
plt.show()
