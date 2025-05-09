import threading
import queue
import time
import numpy as np
import cv2
from arrow import get_dest
from dataclasses import dataclass, field
import math
import ast  # To safely evaluate dicts from strings

# Shared FIFO queue
data_queue = queue.Queue()
running = True

# Load background image (global)
background = None
canvas_size = (1600, 750)
video_path = "test_video.mp4"  # Your video file path
video_cap = cv2.VideoCapture(video_path)


@dataclass
class pos_2d:
    x: float = field(default=0)
    y: float = field(default=0)
    h: float = field(default=0)

def qu2h1(w, x, y, z):
    sr_cp = 2 * (w * x + z * y)
    cr_cp = 1 - 2 * (y * y + x * x)
    return math.atan2(sr_cp, cr_cp)

# Visualization thread
def plot_from_queue():
    global running
    cutoff_rate: int = 10
    cutoff_cnt: int = 0
    while running:
        try:
            pos = data_queue.get(timeout=1)
            rot = data_queue.get(timeout=1)
            if cutoff_cnt == (cutoff_rate - 1):
                x0, y0, h0 = pos.x, pos.y,  pos.h
                print(f"x0: {x0}, y0: {y0}, h0: {h0}")
                cutoff_cnt = 0
                # Start with the background image
                ret, frame = video_cap.read()
                if not ret:
                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
                    ret, frame = video_cap.read()

                background = cv2.resize(frame, canvas_size)
                canvas = background.copy()
    
                
                x, y = int(x0 * 100 + canvas_size[0]/2), int(y0 * 100 + canvas_size[1]/2)
                cv2.circle(canvas, (x, y), 10, (255, 0, 0), -1)
                x1, y1 = get_dest(50, h0)
                x1 = x1 + x
                y1 = y1 + y
                cv2.arrowedLine(canvas, (x, y), (x1, y1), color=(0, 0, 255), thickness=2, tipLength=0.1)
                cv2.imshow("Live Plot", canvas)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    running = False
            else:
                cutoff_cnt += 1
        except queue.Empty:
            pass

# Read and parse mocap data from text file
def load_data_from_file(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = ast.literal_eval(line.strip())
                pos_3d = data.get('pos')
                rot = data.get('rot')
                if pos_3d and rot:
                    x = float(pos_3d[0])
                    y = float(pos_3d[1])
                    w, x_q, y_q, z_q = map(float, rot)
                    h = qu2h1(w, x_q, y_q, z_q)
                    pos = pos_2d(x, y, h)
                    data_queue.put(pos)
                    time.sleep(0.001)  # Simulate live feed 0.001 =1ms delay
            except Exception as e:
                print(f"Error parsing line: {line}\n{e}")
    f.close()

if __name__ == "__main__":
    
    # Load background image
    background_path = "test.png"  # Change to your image
    if not video_cap.isOpened():
        print("Failed to open video file.")
    else:
        print("Video background loaded.")


    plot_thread = threading.Thread(target=plot_from_queue)
    plot_thread.start()

    file_path = "sample_data.txt"  # Replace with your file
    load_data_from_file(file_path)

    plot_thread.join()
    cv2.destroyAllWindows()
    print("Program exited.")
