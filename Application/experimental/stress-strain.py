import pandas as pd
import matplotlib.pyplot as plt

internal_diameter = 2/32 
wall_thickness = 1/32

df = pd.read_csv("data.csv")

pressure = df["Pressure [PSI]"]
diameter = df["Diameter [px]"]
initial_diameter = diameter.iloc[0]

df["Stress"] = (pressure * diameter) / (2 * wall_thickness)
df["Strain"] = (diameter - initial_diameter) / initial_diameter

df.to_csv("output.csv", index=False)


df = pd.read_csv("output.csv")

stress = df["Stress"]
strain = df["Strain"]

plt.figure()
plt.plot(strain, stress, linewidth=2)
plt.xlabel("Strain")
plt.ylabel("Stress")
plt.title("Stress-Strain Curve")
plt.grid(True)

plt.show()
