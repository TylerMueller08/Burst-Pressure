import matplotlib.pyplot as plt
import pandas as pd

internal_diameter = 1 / 16 # Inches
wall_thickness = 1 / 32 # Inches
pixels_to_inches = 0.125 / 185

df = pd.read_csv("data.csv")

pressure = df["Pressure [PSI]"].astype(float)
diameter = df["Diameter [px]"].astype(float) * pixels_to_inches
initial_diameter = diameter.iloc[0]

df["Stress"] = (pressure * diameter) / (2 * wall_thickness)
df["Strain"] = (diameter - initial_diameter) / initial_diameter

df_sorted = df.sort_values("Strain")

plt.figure(figsize=(8, 5))
plt.plot(df_sorted["Strain"], df_sorted["Stress"], linewidth=2)
plt.xlabel("Strain")
plt.ylabel("Stress [PSI]")
plt.title("Stress-Strain Curve")
plt.grid(True)
plt.tight_layout()
plt.show()

df.to_csv("output.csv", index=False)
