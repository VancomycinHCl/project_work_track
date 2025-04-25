import threading
import queue
import time
import numpy as np
import cv2
from natnet_client import NatNetClient, DataDescriptions, DataFrame

# Shared FIFO queue
data_queue = queue.Queue()
num_frames = 0
running = True  # Toggle by key press

# Called when new mocap frame is received
def receive_new_frame(data_frame):
    global num_frames
    num_frames += 1

    for rb in data_frame.rigid_bodies:
        data_queue.put(rb.pos)  # Enqueue new data
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
                cutoff_cnt = 0
                # print(f"[PLOTTING] Position: {pos}")
                # Simple visualization example:
                canvas = np.ones((500, 500, 3), dtype="uint8") * 255
                x, y = int(pos[0]*100 + 250), int(pos[1]*100 + 250)
                cv2.circle(canvas, (x, y), 10, (255, 0, 0), -1)
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
    # Setup NatNet connection
    motive_ip = "192.168.43.155"
    local_ip = "192.168.43.137"

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
            time.sleep(0.005)
            client.update_sync()
            # print(f"{i+1}s - Total frames received: {num_frames}\n")
            i += 1

    plot_thread.join()
    cv2.destroyAllWindows()
    print("Program exited.")
