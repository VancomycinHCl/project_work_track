import time
import sys
from typing import Dict
from natnet_client import NatNetClient, DataDescriptions, DataFrame


rigid_body_names: Dict[int, str] = {}
num_frames = 0

# Open a file to store all the output
output_file = open("calibration_y_longer_side.txt", "w")

def receive_new_desc(desc: DataDescriptions):
    global output_file
    print("Received data descriptions.", file=output_file)
    for rb_desc in desc.rigid_bodies:
        rigid_body_names[rb_desc.id_num] = rb_desc.name or f"RigidBody_{rb_desc.id_num}"
        print(f"  ID: {rb_desc.id_num}, Name: {rigid_body_names[rb_desc.id_num]}", file=output_file)


def receive_new_frame(data_frame: DataFrame):
    global num_frames, output_file
    num_frames += 1

    for rb in data_frame.rigid_bodies:
        print(rb.__dict__, file=output_file)
        # name = rigid_body_names.get(rb.id_num, f"RigidBody_{rb.id_num}")
        # print(f"[{name}] ID: {rb.id_num}")
        # print(f"  Position: x={rb.position.x:.3f}, y={rb.position.y:.3f}, z={rb.position.z:.3f}")
        # print(f"  Rotation: x={rb.orientation.x:.3f}, y={rb.orientation.y:.3f}, z={rb.orientation.z:.3f}, w={rb.orientation.w:.3f}")


if __name__ == "__main__":
    motive_ip = "130.233.123.100"#"192.168.10.139"  # Motive IP (NatNet server) 192.168.43.155  192.168.205.139
    local_ip = "130.233.123.110"#"192.168.10.159"  # IP (NatNet client)192.168.43.137

    client = NatNetClient(
        server_ip_address=motive_ip,
        local_ip_address=local_ip,
        use_multicast=False
    )

    client.on_data_description_received_event.handlers.append(receive_new_desc)
    client.on_data_frame_received_event.handlers.append(receive_new_frame)
    i = 0

    with client:
        client.request_modeldef()

        print("Starting to receive mocap frames...\n", file=output_file)
        while True:  # 30 
            time.sleep(1)
            client.update_sync()
            print(f"{i+1}s - Total frames received: {num_frames}\n", file=output_file)
            i += 1

    # Close the file after the script completes
    output_file.close()
