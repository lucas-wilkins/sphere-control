import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("data.csv", delimiter=',')

print(data)

direction, delay, position, target, index = data.T

delay[direction == 0] = 100

time = np.cumsum(delay)

delay += 4

plt.subplot(2,1,1)
plt.plot(time, position)
plt.plot(time, target)

plt.subplot(2,1,2)

velocity = 1e6 * direction / delay # dx/dt

plt.plot(time, velocity)




plt.show()