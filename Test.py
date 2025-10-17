def process_frame(self, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection
    edges = cv2.Canny(gray, 50, 150)

    h, w = edges.shape
    mask = np.zeros_like(edges)
    mask[int(0.1*h):int(0.9*h), :] = 255
    edges = cv2.bitwise_and(edges, mask)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    if len(contours) < 2:
        return frame, None

    # Get centers of the main contours
    contour_centers = []
    for c in contours:
        if len(c) < 20:
            continue
        [vx, vy, x0, y0] = cv2.fitLine(c, cv2.DIST_L2, 0, 0.01, 0.01)
        contour_centers.append((x0, y0, vx, vy))

    if len(contour_centers) < 2:
        return frame, None

    # Sort by x position of the line’s base point
    contour_centers = sorted(contour_centers, key=lambda k: k[0])
    left_line = contour_centers[0]
    right_line = contour_centers[-1]

    # Extend lines to top and bottom of frame
    def line_points(vx, vy, x0, y0, h):
        lefty = int((-x0*vy/vx) + y0)
        righty = int(((w-x0)*vy/vx) + y0)
        return (0, lefty), (w-1, righty)

    (lx1, ly1), (lx2, ly2) = line_points(*left_line, h)
    (rx1, ry1), (rx2, ry2) = line_points(*right_line, h)

    # Draw lines
    cv2.line(frame, (lx1, ly1), (lx2, ly2), (0, 255, 0), 2)
    cv2.line(frame, (rx1, ry1), (rx2, ry2), (0, 255, 0), 2)

    # Estimate diameter at image center
    y_mid = h // 2
    leftX = int((lx2-lx1)/(ly2-ly1) * (y_mid-ly1) + lx1) if ly2 != ly1 else lx1
    rightX = int((rx2-rx1)/(ry2-ry1) * (y_mid-ry1) + rx1) if ry2 != ry1 else rx1
    diameter = rightX - leftX

    self.diameter_history.append(diameter)
    smoothed_diameter = int(np.mean(self.diameter_history))

    cv2.putText(frame, f"Diameter: {smoothed_diameter}px", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return frame, smoothed_diameter

