def process_frame(self, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Mask edges to avoid false edges near borders (optional, tweak as needed)
    h, w = edges.shape
    mask = np.zeros_like(edges)
    mask[int(0.1*h):int(0.9*h), :] = 255
    edges = cv2.bitwise_and(edges, mask)

    # Get all edge coordinates
    ys, xs = np.where(edges > 0)
    if len(xs) == 0:
        return frame, None

    # Split into left side and right side based on midpoint
    mid = w // 2
    left_points = np.array([(x, y) for x, y in zip(xs, ys) if x < mid])
    right_points = np.array([(x, y) for x, y in zip(xs, ys) if x >= mid])

    if len(left_points) < 20 or len(right_points) < 20:
        return frame, None

    # Fit 2nd-degree polynomials (x as function of y)
    left_fit = np.polyfit(left_points[:,1], left_points[:,0], deg=2)
    right_fit = np.polyfit(right_points[:,1], right_points[:,0], deg=2)

    # Draw fitted curves and compute diameters
    diameters = []
    for y in range(0, h, 10):  # sample every 10 pixels vertically
        left_x = int(np.polyval(left_fit, y))
        right_x = int(np.polyval(right_fit, y))
        
        if 0 <= left_x < w and 0 <= right_x < w:
            diameters.append(right_x - left_x)
            cv2.circle(frame, (left_x, y), 2, (0,255,0), -1)
            cv2.circle(frame, (right_x, y), 2, (0,255,0), -1)
            cv2.line(frame, (left_x, y), (right_x, y), (255,0,0), 1)

    if not diameters:
        return frame, None

    smoothed_diameter = np.mean(diameters)
    self.diameter_history.append(smoothed_diameter)
    smoothed_diameter = int(np.mean(self.diameter_history))

    cv2.putText(frame, f"Diameter: {smoothed_diameter:.1f}px", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    return frame, smoothed_diameter
