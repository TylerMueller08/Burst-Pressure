import os
import pandas as pd
import matplotlib.pyplot as plt

# User-Adjusted Settings
DATA_FILE = "../Data/VideoDiameters_TESTING.csv" # Change to pressure file.
SAVE_DIR = "../Results/"
DIAMETER_COL = "Diameter [pixels]" # CSV diameter column.
PRESSURE_COL = "Pressure [PSI]"    # CSV pressure column.
TUBE_DIAMETER_MM = 10.0            # Outer diameter of the tube in mm
WALL_THICKNESS_MM = 1.0            # Thickness of the tube wall in mm

# Analysis Functions
def compute_scale(diameters_px, diameter_mm):
    # Compute mm/px based on first measured diameter.
    first_px = diameters_px.iloc[0]
    return diameter_mm / first_px

def compute_strain(diameters_mm):
    # strain = (D-D0)/D0, where D0 is initial diameter before pressurization and D is current diameter.
    D0 = diameters_mm.iloc[0]
    return (diameters_mm - D0) / D0

def compute_stress(pressures_kpa, diameters_mm, wall_thickness_mm):
    # stress = (P*r)/t, where P is internal pressure, r is inner radius of tube, and t is wall thickness (r units = t units).
    radius_mm = diameters_mm / 2
    return (pressures_kpa * radius_mm) / wall_thickness_mm

def main():
    os.makedirs(SAVE_DIR, exist_ok=True)

    df = pd.read_csv(DATA_FILE) # Import pressure data.

    # Calibration.
    scale_mm_per_px = compute_scale(df[DIAMETER_COL], TUBE_DIAMETER_MM)
    diameters_mm = df[DIAMETER_COL] * scale_mm_per_px

    # Compute strain & stress.
    strain = compute_strain(diameters_mm)
    stress = compute_stress(df[PRESSURE_COL], diameters_mm, WALL_THICKNESS_MM)

    # Plot stress vs. strain.
    plt.figure(figsize=(8,6))
    plt.plot(strain, stress, label="Trial #", color="blue")
    plt.xlabel("Strain [Unitless]")
    plt.ylabel("Stress [PSI]")
    plt.title("Stress-Strain Curve")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Save plot.
    save_path = os.path.join(SAVE_DIR, "stress_strain_trial#.png")
    plt.savefig(save_path, dpi=300)
    plt.show()

    print(f"Saved Stress-Strain Plot: {save_path}")

if __name__ == "__main__":
    main()