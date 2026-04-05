import subprocess
import os
import math

# load config
with open("config.json") as f:
    config = json.load(f)

chunk_size_mb = config["chunk_size_mb"]

def file_split_7z(file_path, split_size_mb=50):
    file_path_7z_list = []

    origin_file_path = ""

    # اگر فایل از قبل 7z بود
    if os.path.splitext(file_path)[1] == ".7z":
        origin_file_path = file_path
        file_path = os.path.splitext(origin_file_path)[0] + ".7zo"
        os.rename(origin_file_path, file_path)

    file_size_mb = os.path.getsize(file_path) / 1024 / 1024
    parts_count = math.ceil(file_size_mb / split_size_mb)

    head, ext = os.path.splitext(os.path.abspath(file_path))
    archive_head = "".join((head, ext.replace(".", "_"))) + ".7z"

    # پاک کردن فایل‌های قبلی
    for i in range(parts_count):
        check_file = "{}.{:03d}".format(archive_head, i + 1)
        if os.path.isfile(check_file):
            os.remove(check_file)

    cmd_7z = [
        "7z", "a",
        f"-v{split_size_mb}m",
        "-y",
        "-mx0",
        archive_head,
        file_path
    ]

    proc = subprocess.Popen(cmd_7z, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if b"Everything is Ok" not in out:
        raise Exception(err.decode("utf-8"))

    for i in range(parts_count):
        file_path_7z_list.append(f"{archive_head}.{i + 1:03d}")

    if origin_file_path:
        os.rename(file_path, origin_file_path)

    return file_path_7z_list


def do_file_split(file_path):
    split_size_mb = chunk_size_mb

    file_size_mb = os.path.getsize(file_path) / 1024 / 1024
    split_parts = math.ceil(file_size_mb / split_size_mb)

    real_split_size = math.ceil(file_size_mb / split_parts)

    file_list = file_split_7z(file_path, split_size_mb=real_split_size)

    return {
        "file": file_path,
        "total_size_mb": file_size_mb,
        "parts": len(file_list),
        "split_size_mb": real_split_size,
        "files": file_list
    }