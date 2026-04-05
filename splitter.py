import os
import json
import math

# load config
with open("config.json") as f:
    config = json.load(f)

CHUNK_SIZE = config["chunk_size_mb"] * 1024 * 1024  # به بایت


def split_file(file_path):
    if not os.path.exists(file_path):
        raise Exception("File not found")

    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    output_dir = file_path + "_parts"
    os.makedirs(output_dir, exist_ok=True)

    parts_dict = {}

    total_parts = math.ceil(file_size / CHUNK_SIZE)

    with open(file_path, "rb") as f:
        for i in range(total_parts):
            part_filename = f"{file_name}.part{i+1:03d}.zip"
            part_path = os.path.join(output_dir, part_filename)

            with open(part_path, "wb") as part_file:
                remaining = CHUNK_SIZE
                while remaining > 0:
                    chunk = f.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    part_file.write(chunk)
                    remaining -= len(chunk)

            parts_dict[i + 1] = part_path

    print("📦 Parts:")
    for k, v in parts_dict.items():
        print(f"{k} -> {v}")

    return parts_dict