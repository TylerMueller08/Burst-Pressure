import pandas as pd
import os

PRESSURE_FILE = "../Data/Pressure_10-10-2025_13-29-22.csv"
DIAMETERS_FILE = "../Data/VideoDiameters_TESTING.csv"
OUTPUT_FILE = "../Data/MergedData_TESTING.csv"

def merge_data(pressure_file, video_file, output_file):
    df_pressure = pd.read_csv(pressure_file)
    df_video = pd.read_csv(video_file)

    if len(df_pressure) != len(df_video):
        print(f"Warning: Pressure rows = {len(df_pressure)}, Video frames = {len(df_video)}")

        # Could be a poor decision, but interpolating diameters to match pressure timestamps:
        df_video_interp = pd.DataFrame()
        df_video_interp["Diameter [pixels]"] = pd.Series(
            np.interp(
                range(len(df_pressure)),
                range(len(df_video)),
                df_video["Diameter [pixels]"].fillna(method="ffill")
            )
        )
        df_video = df_video_interp

    df_merged = pd.concat([df_pressure.reset_index(drop=True), df_video.reset_index(drop=True)], axis=1)

    # Saving file.
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    df_merged.to_csv(output_file, index=False)
    print(f"Successfully merged data, saved to {output_file}")



if __name__ == "__main__":
    import numpy as np
    merge_data(PRESSURE_FILE, DIAMETERS_FILE, OUTPUT_FILE)