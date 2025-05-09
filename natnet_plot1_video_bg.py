import threading
import queue
import time
import numpy as np
import cv2
from natnet_client import NatNetClient, DataDescriptions, DataFrame
from arrow import get_dest
from dataclasses import dataclass, field
import math
import os

image_path = os.environ.get("IMAGE_PATH")
canvas_width = int(os.environ.get("CANVAS_WIDTH", 0))
canvas_height = int(os.environ.get("CANVAS_HEIGHT", 0))
video_path = "background_video.mp4"  # Your video file path
video_cap = cv2.VideoCapture(video_path)

print(f"Using image: {image_path}")
print(f"Canvas size: {canvas_width}x{canvas_height}")

# Shared FIFO queue
data_queue = queue.Queue()
num_frames = 0
running = True  # Toggle by key press

# Load background image (global)
background = None
canvas_size = (500, 500)

@dataclass
class pos_2d:
    x: float = field(default=0)  # x position 
    y: float = field(default=0)  # y position 
    h: float = field(default=0)  # heading angle


def qu2h(w,x,y,z):
    sy_cp = 2*(w*z+x*y)
    cy_cp = 1-2*(y*y+z*z)
    return math.atan2(sy_cp, cy_cp) # quaternion to yaw as radian 

def qu2h1(w,x,y,z):
    sr_cp = 2*(w*x+z*y)
    cr_cp = 1-2*(y*y+x*x)
    return math.atan2(sr_cp, cr_cp) # quaternion to yaw as radian 


# Called when new mocap frame is received
def receive_new_frame(data_frame):
    global num_frames
    num_frames += 1

    for rb in data_frame.rigid_bodies:
        # `print(rb.__dict__)
        x = rb.pos[0]
        y = rb.pos[1]
        # h = rb.rot[2]
        h = qu2h1(rb.rot[0],rb.rot[1],rb.rot[2],rb.rot[3])
        pos = pos_2d(x,y,h)
        data_queue.put(pos)  # Enqueue new data
        # print(f"[DATA RECEIVED] Frame #{num_frames} - Position: {rb.pos}")

# Visualization thread
def plot_from_queue():
    global running
    cutoff_rate: int = 10
    cutoff_cnt: int = 0
    while running:
        try:
            pos = data_queue.get(timeout=1)
            if cutoff_cnt == (cutoff_rate - 1):
                x0,y0 = pos.x, pos.y
                h0 = pos.h # / (math.pi*2) * 360 
                #print(f"h0:{h0}")
                cutoff_cnt = 0
                # print(f"[PLOTTING] Position: {pos}")
                # Simple visualization example:
                # Start with the background video
                
                ret, frame = video_cap.read()
                if not ret:
                    video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
                    ret, frame = video_cap.read()

                background = cv2.resize(frame, canvas_size)
                canvas = background.copy()
                
                x, y = int(x0*100 + canvas_size[0]/2), int(y0*100 + canvas_size[1]/2)
                cv2.circle(canvas, (x, y), 10, (255, 0, 0), -1)              
                x1, y1 = get_dest(50,h0)
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

# Keyboard listener
def on_press(key):
    global running
    if key.char == 'q':
        print("Quit signal received.")
        running = False
        return False  # Stop listener

# Start listener in background
# listener = keyboard.Listener(on_press=on_press)
# listener.start()

# Start plotting in a separate thread
plot_thread = threading.Thread(target=plot_from_queue)
plot_thread.start()

# In your main function:
if __name__ == "__main__":
    
    # Load background video
    if not video_cap.isOpened():
        print("Failed to open video file.")
    else:
        print("Video background loaded.")
    
    
    # Setup NatNet connection
    motive_ip = "131.233.123.181" #"192.168.43.155"
    local_ip = "130.233.123.101"

    client = NatNetClient(
        server_ip_address=motive_ip,
        local_ip_address=local_ip,
        use_multicast=False
    )

    # client.on_data_description_received_event.handlers.append(receive_new_desc)
    client.on_data_frame_received_event.handlers.append(receive_new_frame)

    with client:
        client.request_modeldef()
        print("Starting to receive mocap frames...\n")

        i = 0
        while running:
            time.sleep(0.010)
            client.update_sync()
            # print(f"{i+1}s - Total frames received: {num_frames}\n")
            i += 1

    plot_thread.join()
    cv2.destroyAllWindows()
    print("Program exited.")
