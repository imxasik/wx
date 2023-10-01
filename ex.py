import matplotlib.pyplot as plt
import numpy as np
import os

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Data for plotting
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='About as simple as it gets, folks')
ax.grid()

# Save the plot as "test.png" in the same directory as the script
plot_path = os.path.join(script_directory, 'test.png')
fig.savefig(plot_path)

# Show the plot (optional, for local testing)
plt.show()
