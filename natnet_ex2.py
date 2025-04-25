import time
from typing import Dict

from natnet_client import NatNetClient, DataDescriptions, DataFrame


rigid_body_names: Dict[int, str] = {}
num_frames = 0

def receive_new_desc(desc: DataDescriptions):
    print("✅ Received data descriptions.")
    for rb_desc in desc.rigid_bodies:
        rigid_body_names[rb_desc.id_num] = rb_desc.name or f"RigidBody_{rb_desc.id_num}"
        print(f"  ID: {rb_desc.id_num}, Name: {rigid_body_names[rb_desc.id_num]}")


def receive_new_frame(data_frame: DataFrame):
    global num_frames
    num_frames += 1

    for rb in data_frame.rigid_bodies:
        print(rb.__dict__)
        # name = rigid_body_names.get(rb.id_num, f"RigidBody_{rb.id_num}")
        # print(f"[{name}] ID: {rb.id_num}")
        # print(f"  Position: x={rb.position.x:.3f}, y={rb.position.y:.3f}, z={rb.position.z:.3f}")
        # print(f"  Rotation: x={rb.orientation.x:.3f}, y={rb.orientation.y:.3f}, z={rb.orientation.z:.3f}, w={rb.orientation.w:.3f}")


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

    with client:
        client.request_modeldef()

        print("Starting to receive mocap frames...\n")
        while True:  #  30 
            time.sleep(1)
            client.update_sync()
            print(f"{i+1}s - Total frames received: {num_frames}\n")
            i += 1
