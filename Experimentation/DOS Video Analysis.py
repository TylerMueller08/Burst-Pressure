# libraries
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

# Try to use local dm style if available, otherwise fall back to default style
try:
    plt.style.use('dm.mplstyle/dm.mplstyle')
except Exception:
    # attempt to load from same directory as this script
    import pathlib
    script_dir = pathlib.Path(__file__).resolve().parent
    alt_style = script_dir / 'dm.mplstyle' / 'dm.mplstyle'
    try:
        plt.style.use(str(alt_style))
    except Exception:
        # final fallback: use default style
        plt.style.use('default')
#################################################################
# FUNCTIONS
#################################################################

def first_zero(arr, axis, invalid_val=-1):
    mask = arr == 0
    return np.where(mask.any(axis=axis), mask.argmax(axis=axis), invalid_val)


def last_zero(arr, axis, invalid_val=-1):
    mask = arr == 0
    val = arr.shape[axis] - np.flip(mask, axis=axis).argmax(axis=axis) - 1
    return np.where(mask.any(axis=axis), val, invalid_val)


#################################################################
# MAIN
#################################################################


# Stuff to Edit
file_path = 'C:/Users/Mols/Desktop/Burst Pressure/old/Testing'  # where the file is stored in relation to the script
file_name = 'Video_10-10-2025_13-29-22'  # name of file for analysis, leave off any file extensions (like .mp4)
vid_export_name = 'DOS ex final1'       # name of video to export, leave off file extensions (like .avi)
export = 'N'        # export data to .csv (Y or N) will export 2 files, one being the whole analyzed video and other will be only cropped data
vid_export = 'N'    # export analyzed video (Y or N)
fps = 30          # fps of the video captured
delay = 1           # delay between each frame during video playback (does not affect analysis), in ms
miny = 425         # region of interest bounds for analysis, the y-axis numbering is backwards (zero starts at the top)
maxy = 550
minx = 200
maxx = 375
lcrop = 200   # points on left side cropped (min 1)
rcrop = 1        # points on right side cropped (min 1)
thresh_num = 235    # brightness value of edge for threshold (max 255, which is white) 235 is a good starting point

# Initialize arrays and constants
frame_diameter = []
total_diameter = []
frame_num = 1

# save video
if vid_export == 'Y':
    vid_result = cv.VideoWriter(vid_export_name + '.avi', cv.VideoWriter_fourcc(*'MJPG'), 30, (1280, 1024)) #(1280, 1024)

# load the video
video_fullpath = os.path.join(file_path, file_name + '.mp4')
if not os.path.isfile(video_fullpath):
    raise FileNotFoundError(f"Video file not found: {video_fullpath}")

cap = cv.VideoCapture(video_fullpath)
if not cap.isOpened():
    raise RuntimeError(f"Failed to open video capture for: {video_fullpath}")

# play the video by reading frame by frame
while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        frame = cv.resize(frame, (512, 640))
        # plt.matshow(frame)
        # plt.show()

        ROI_img = frame[miny:maxy, minx:maxx]

        # load the input image cv.IMREAD_GRAYSCALE
        BW_img = cv.cvtColor(ROI_img, cv.COLOR_BGR2GRAY)

        # plt.matshow(BW_img)
        # plt.show()

        h, w = BW_img.shape

        # apply thresholding to convert grayscale to binary image 70,1,0
        ret, BW_img_thresh = cv.threshold(BW_img, thresh_num, 1, 0)

        # plt.matshow(BW_img_thresh)
        # plt.show()

        # find first and last zero val for each row
        first_zero_val = first_zero(BW_img_thresh, axis=1, invalid_val=-1)
        last_zero_val = last_zero(BW_img_thresh, axis=1, invalid_val=-1)

        # draw box around ROI
        cv.rectangle(frame, (minx, miny), (maxx, maxy), color=(0, 0, 0), thickness=2)

        # draw line on border of tube and compute diameters per row
        frame_diameter_rows = []
        for cols in range(h):
            fv = int(first_zero_val[cols])
            lv = int(last_zero_val[cols])

            # only draw and compute when both edges were found
            if fv >= 0 and lv >= 0:
                # guard slice indices to be within frame bounds
                left_start = max(0, fv + minx - 2)
                left_end = min(frame.shape[1], fv + minx)
                right_start = max(0, lv + minx)
                right_end = min(frame.shape[1], lv + minx + 2)

                try:
                    frame[cols + miny, left_start:left_end] = [0, 0, 255]
                except Exception:
                    pass
                try:
                    frame[cols + miny, right_start:right_end] = [255, 0, 0]
                except Exception:
                    pass

                if lv >= fv:
                    frame_diameter_rows.append(lv - fv)

        # store each frame's average diameter and update frame num
        if frame_diameter_rows:
            total_diameter.append([float(np.average(frame_diameter_rows)), frame_num / fps])
        # else: no valid diameter detected in this frame -> skip
        frame_num += 1

        # save to video
        if vid_export == 'Y':
            vid_result.write(frame)

        cv.imshow('frame', frame)  # show the video
        if cv.waitKey(delay) & 0xFF == ord('q'):
            break
    else:
        break

# ensure we collected some diameter data
if not total_diameter:
    raise RuntimeError(f"No diameter data collected from video: {video_fullpath}. Check ROI and threshold settings.")

# unzip data points
y, t = zip(*total_diameter)
crop_y, crop_t = zip(*total_diameter[lcrop:len(y)-rcrop])
# crop_y, crop_t = zip(*total_diameter[lcrop:])

print("og len:", len(y))
print("new len", len(crop_y))
# calculate Dt/D0
dtdo_diameter = crop_y/crop_y[0]
dtdo_diameter_uncrop = y/y[0]

# # calculate linear regression
p_fit = np.polyfit(crop_t, np.log(dtdo_diameter), 1)
p = np.poly1d(p_fit)

# calculate relaxation time
lambda_E = (-1 / (3 * p[1])) * 1000
print("linear fit:", p)
print("Relaxation time:", lambda_E, "ms")

# plot graph

plt.plot(t[:lcrop], (y[:lcrop]), 'ok')
plt.plot(t[len(y)-rcrop:], (y[len(y)-rcrop:]), 'ok')
plt.plot(crop_t, crop_y, 'oc')

plt.title("Change of Diameter (not log)")
plt.xlabel('Time (s)')
plt.ylabel('Diameter (pixels)')

plt.show()

plt.plot(t[:lcrop], np.log(y[:lcrop]), 'ok')
plt.plot(t[len(y)-rcrop:], np.log(y[len(y)-rcrop:]), 'ok')
plt.plot(crop_t, np.log(crop_y), 'oc')

# plt.title("Change of Diameter (log)")
plt.xlabel(r'$t~/~\mathrm{s}$')
plt.ylabel(r'$\log_{10}( D )~/~\mathrm{pixels}$')
# plt.xlim(0, 6.5)
plt.show()

# plt.plot(t, np.log(dtdo_diameter_uncrop), 'ok')
plt.plot(crop_t, np.log(dtdo_diameter), 'oc')
plt.plot(crop_t, p(crop_t), linestyle='--', color='k')

# plt.title("Relaxation Time")
plt.xlabel(r'$t~/~\mathrm{s}$')
plt.ylabel(r'$\log_{10}(D/Do)$')

# plt.text(3.1, -0.1, "{:.2f}ms".format(lambda_E), fontsize=10)
plt.ylim(4, 6.5)
plt.ylim(-.35, 0)
plt.show()

if export == 'Y':
    # # export analyzed vis data
    export_name_uncrop = file_name + '_uncrop.csv'
    # dictionary of lists
    dict = {'time (s)': t, 'diameter (pixels)': y}
    df = pd.DataFrame(dict)
    # saving the dataframe
    df.to_csv(file_path + 'export/' + export_name_uncrop, index=False)

    export_name_crop = file_name + '_crop.csv'
    # dictionary of lists
    dict = {'time (s)': crop_t, 'diameter (pixels)': crop_y}
    df = pd.DataFrame(dict)
    # saving the dataframe
    df.to_csv(file_path + 'export/' + export_name_crop, index=False)