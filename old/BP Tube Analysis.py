# libraries
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


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

# initializing arrays and variables, don't change these
frame_tube_diameter = []
vid_tube_diameter = []
array_test = []
frame_num = 1

# stuff to change
fileName = 'KH_T_SF_20240422_2'  # change the file name if needed
export = 'N'        # Y or N to export to a csv file
export_name = 'cropping test 2'   # name of data file to export
vid_export = 'N'        # Y or N to export the analyzed video file (what you see when it plays)
vid_export_name = 'fileName'   # name of video file to export
fps = 30    # fps of recording, check by looking at video properties

# load pressure data
pressure_time, pressure = np.loadtxt('Burst Pressure txt/' + fileName + '.txt', delimiter=';', skiprows=4, usecols=(0, 1), unpack=True)
# pressure_time, pressure = np.loadtxt('SA_Tube_4.csv', delimiter=',', skiprows=4, usecols=(0, 1), unpack=True)
pressure = pressure - pressure[0]

# load the video
cap = cv.VideoCapture('Burst Pressure Vids/' + fileName + '.mov')
# cap = cv.VideoCapture(fileName + '.mov')

# save video
if vid_export == 'Y':
    vid_result = cv.VideoWriter(vid_export_name + '.avi', cv.VideoWriter_fourcc(*'MJPG'), 30, (375, 667))

# play the video by reading frame by frame
while cap.isOpened():
    ret, frame = cap.read()
    if ret:

        # Resize video consistently for comparisons
        og_img = cv.resize(frame, (375, 667))
        resize = cv.resize(frame, (375, 667))

        # load the input image cv.IMREAD_GRAYSCALE
        BW_img = cv.cvtColor(og_img, cv.COLOR_BGR2GRAY)

        # plt.matshow(BW_img)
        # plt.show()

        h, w = BW_img.shape

        # apply thresholding to convert grayscale to binary image 70,1,0
        ret, BW_img_thresh = cv.threshold(BW_img, 90, 1, 0)

        # plt.matshow(BW_img_thresh)
        # plt.show()

        # find first and last zero val for each row
        first_zero_val = first_zero(BW_img_thresh, axis=1, invalid_val=-1)
        last_zero_val = last_zero(BW_img_thresh, axis=1, invalid_val=-1)

        # draw line on border of tube
        for cols in range(h):

            resize[cols, first_zero_val[cols]: first_zero_val[cols] + 5] = [255, 255, 0]
            resize[cols, last_zero_val[cols]: last_zero_val[cols] + 5] = [255, 255, 0]

            # calculate tube diameter for each row for one frame
            frame_tube_diameter = [last_zero_val - first_zero_val]

        # store each frame's average diameter at every .1 of a second
        if (frame_num % 3 == 0) and (len(pressure_time) > len(vid_tube_diameter)):
            vid_tube_diameter.append([np.average(frame_tube_diameter), frame_num/fps])
        frame_num += 1

        # write to video
        if vid_export == 'Y':
            vid_result.write(resize)

        cv.imshow('frame', resize)  # show the video
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# print(vid_tube_diameter)
# print(len(vid_tube_diameter))

# unzip vid data collected
y, x = zip(*vid_tube_diameter)

# y = y / 34.33
# pressure = pressure * 51.715
# print(str(h) + "height")
# print(str(w) + "width")


print(vid_tube_diameter)

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

if export == 'Y':
    # # dictionary of lists
    dict = {'tube_time': x, 'tube_diameter': y, 'pressure time': pressure_time, 'pressure': pressure}
    df = pd.DataFrame(dict)
    # # saving the dataframe
    df.to_csv('Burst Pressure Files/' + export_name + '.csv', index=False)

# ax1.plot(x, y, 'ob')
# # plt.title("Diameter of Each Frame and Pressure vs Time")
# ax1.set_xlabel('Time (s)')
# ax1.set_ylabel('Tube Diameter (pixels)', color='tab:blue')
#
# ax2.plot(pressure_time, pressure, 'or')
# ax2.set_ylabel('pressure (psi)', color='tab:red')
#
#
# plt.show()


cap.release()
cv.destroyAllWindows()
