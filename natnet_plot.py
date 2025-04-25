import time
from typing import Dict
import cv2
import numpy as np

from natnet_client import NatNetClient, DataDescriptions, DataFrame


rigid_body_names: Dict[int, str] = {}
num_frames = 0


# {'id_num': int, 'pos': Tuple[float, float, float], 'rot': Tuple[float, float, float, float], 'markers': None, 'tracking_valid': bool, 'marker_error': float}


def receive_new_desc(desc: DataDescriptions):
    print("✅ Received data descriptions.")
    for rb_desc in desc.rigid_bodies:
        rigid_body_names[rb_desc.id_num] = rb_desc.name or f"RigidBody_{rb_desc.id_num}"
        print(f"  ID: {rb_desc.id_num}, Name: {rigid_body_names[rb_desc.id_num]}")


def receive_new_frame(data_frame: DataFrame):
    global num_frames
    num_frames += 1

    # for key in data_frame.__dict__.keys():
    #     print(f"{key}:{data_frame.__dict__[key]}")

    for rb in data_frame.rigid_bodies:
        print(rb.pos)



def cv_init():
    # Create a blank white canvas (500x500 pixels, 3 color channels)
    canvas = np.ones((500, 500, 3), dtype="uint8") * 255
    	
    # Define top-left and bottom-right points of the square
    top_left = (150, 150)
    bottom_right = (350, 350)

    # Draw the square (BGR color, thickness)
    cv2.rectangle(canvas, top_left, bottom_right, color=(0, 0, 255), thickness=3)

    # Show the canvas
    cv2.imshow("Canvas with Square", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()






if __name__ == "__main__":
    
    motive_ip = "192.168.43.155"         # Motive  IP（NatNet server）
    local_ip = "192.168.43.137"          #  IP（NatNet client）

    client = NatNetClient(
        server_ip_address=motive_ip,
        local_ip_address=local_ip,
        use_multicast=False
    )

    client.on_data_description_received_event.handlers.append(receive_new_desc)
    client.on_data_frame_received_event.handlers.append(receive_new_frame)
    i = 0

    cv_init()

    with client:
        client.request_modeldef()

        print("Starting to receive mocap frames...\n")
        while True:  #  30 
            time.sleep(1)
            client.update_sync()
            print(f"{i+1}s - Total frames received: {num_frames}\n")
            i += 1
