import threading
import queue
import time
import numpy as np
import cv2
from natnet_client import NatNetClient, DataDescriptions, DataFrame
from arrow import get_dest
from dataclasses import dataclass, field
import math
from typing import Dict

# Open a file to store all printed output
output_file = open("test_data.txt", "w")

rigid_body_names: Dict[int, str] = {}

# Shared FIFO queue
data_queue = queue.Queue()
num_frames = 0
running = True  # Toggle by key press

@dataclass
class pos_2d:
    x: float = field(default=0)  # x position 
    y: float = field(default=0)  # y position 
    h: float = field(default=0)  # heading angle

def qu2h(w,x,y,z):
    sy_cp = 2*(w*z + x*y)
    cy_cp = 1 - 2*(y*y + z*z)
    return math.atan2(sy_cp, cy_cp)  # quaternion to yaw as radian 

def qu2h1(w,x,y,z):
    sr_cp = 2*(w*x + z*y)
    cr_cp = 1 - 2*(y*y + x*x)
    return math.atan2(sr_cp, cr_cp)  # quaternion to yaw as radian 

        
# Called when new mocap frame is received
def receive_new_frame(data_frame: DataDescriptions):
    global num_frames
    global output_file
    num_frames += 1

    for rb in data_frame.rigid_bodies:
        print(rb.__dict__, file=output_file)
        x = rb.pos[0]
        y = rb.pos[1]
        h = qu2h1(rb.rot[0], rb.rot[1], rb.rot[2], rb.rot[3])
        pos = pos_2d(x, y, h)
        data_queue.put(pos)

# Visualization thread
def plot_from_queue():
    global running
    cutoff_rate = 10
    cutoff_cnt = 0
    while running:
        try:
            pos = data_queue.get(timeout=1)
            if cutoff_cnt == (cutoff_rate - 1):
                x0, y0 = pos.x, pos.y
                h0 = pos.h
                #print(f"h0:{h0}", file=output_file)
                cutoff_cnt = 0

                canvas = np.ones((500, 500, 3), dtype="uint8") * 255
                x, y = int(x0 * 100 + 250), int(y0 * 100 + 250)
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

# Keyboard listener (commented out)
def on_press(key):
    global running
    if key.char == 'q':
        print("Quit signal received.", file=output_file)
        running = False
        return False

# Start plotting in a separate thread
plot_thread = threading.Thread(target=plot_from_queue)
plot_thread.start()

if __name__ == "__main__":
    motive_ip = "192.168.205.139"  # Motive IP (NatNet server) 192.168.43.155
    local_ip = "192.168.205.159"  # IP (NatNet client)192.168.43.137

    client = NatNetClient(
        server_ip_address=motive_ip,
        local_ip_address=local_ip,
        use_multicast=False
    )

    #client.on_data_description_received_event.handlers.append(receive_new_desc)
    client.on_data_frame_received_event.handlers.append(receive_new_frame)

    with client:
        client.request_modeldef()
        print("Starting to receive mocap frames...\n", file=output_file)

        i = 0
        while running:
            time.sleep(0.010)
            client.update_sync()
            i += 1

    plot_thread.join()
    cv2.destroyAllWindows()
    print("Program exited.", file=output_file)

    # Close the log file
    output_file.close()
