import numpy as np
import math
import matplotlib.pyplot as plt

plt.style.use('dm.mplstyle/dm.mplstyle')
# import data
t1, d1, pt1, p1 = np.loadtxt('Burst Pressure Files/KH_T_SF_20240422_1_crop.csv', delimiter=',', skiprows=1, usecols=(0, 1, 2, 3), unpack=True)

# apply scale to diameter
d1 = d1 / 34.33

# convert pressure to kpa
p1 = p1 * 6.89476

# calc strain
strain1 = (d1-d1[0])/d1[0]

# Cross-sectional area calculations
CSA_rad = 2                     # original inner rad
CSA = np.pi * (CSA_rad**2)      # original CSA

# variables to change
lower_num = 11      # lower bound to calculate slope of linear region
higher_num = 28     # upper bound to calculate slope of linear region
data_crop = 66      # number of right-hand data points to crop (crop out extra points after failure)

# Calculate the diameter and pressure at the bounds
D_ex_low = d1[lower_num]
D_ex_high = d1[higher_num]
P_low = p1[lower_num]
P_high = p1[higher_num]
point1 = [strain1[lower_num], P_low]
point2 = [strain1[higher_num], P_high]
point3 = [strain1[higher_num], P_low]

D_in_low = math.sqrt((D_ex_low)**(2) - (d3[0])**2 + (4)**2)
D_in_high = math.sqrt((D_ex_high)**(2) - (d3[0])**2 + (4)**2)

# calculation of inner diameter assume incompressible

# D_in_low = 2 * math.sqrt(((D_ex_low / 2)**(2)) - (CSA / np.pi))
# D_in_high = 2 * math.sqrt(((D_ex_high / 2)**(2)) - (CSA / np.pi))

# Calculate compliance expressed as a percentage of the diameter change
comp = (((D_in_high - D_in_low) / D_in_low) * (1 / (P_high - P_low)))

# print out the different variables for comparison
print("dex0: " +str(d1[0]))
print("dex low: " + str(D_ex_low))
print("dex high: " + str(D_ex_high))
print("din low: " + str(D_in_low))
print("din high: " + str(D_in_high))
print("P low: " + str(P_low))
print("P high: " + str(P_high))
print("compliance: " + str(comp))

plt.plot(strain1[:66], p1[:66], 'sb')
plt.plot(D_ex_low, P_low, 'ok')
plt.plot(D_ex_high, P_high, 'ok')

# x_values = [point1[0], point2[0], point3[0]]
# y_values = [point1[1], point2[1], point3[1]]
# plt.plot(x_values[0:1], y_values[0:1], 'ko', linestyle="solid", linewidth='3')
# plt.plot(x_values[1:2], y_values[1:2], color='black', marker='o', linestyle="solid", linewidth='3')
# plt.plot(x_values[0::2], y_values[0::2], color='black', marker='o', linestyle="solid", linewidth='3')

plt.plot(point1[0], point1[1], 'ok', markersize='7')
plt.plot(point2[0], point2[1], 'ok', markersize='7')
plt.plot(point3[0], point3[1], marker = 'none')

# comp = 0.0122

#connecting all three points to make triangle
plt.plot(
    (point1[0], point2[0], point3[0], point1[0]),
    (point1[1], point2[1], point3[1], point1[1]), color='black', linestyle='solid', linewidth='3'
)
# plt.text(0.11, 3, "$c~=~{:.3f}~\mathrm{{kPa^{{-1}}}}$".format(comp), fontsize=15)

# plt.legend()
# plt.ylim(-2.5, 17.5)
# plt.xlim(0, 0.6)
plt.xlabel(r'$\varepsilon$')
plt.ylabel(r'$\sigma~/~\mathrm{kPa}$')
plt.show()
