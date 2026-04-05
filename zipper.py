# Source - https://stackoverflow.com/a/57114313
# Posted by Yuanmeng Xiao, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-05, License - CC BY-SA 4.0

#! /usr/bin/python3
# -*- coding:utf-8 -*-
# apt-get install p7zip-full

import subprocess
import os
import math
import logzero

logger = logzero.logger

MAX_SPLIT_SIZE = 1

    def file_split_7z(file_path, split_size=MAX_SPLIT_SIZE):
        file_path_7z_list = []
        # if origin file is 7z file rename it
        origin_file_path = ""
        if os.path.splitext(file_path)[1] == ".7z":
            origin_file_path = file_path
            file_path = os.path.splitext(origin_file_path)[0] + ".7zo"
            os.rename(origin_file_path, file_path)
        # do 7z compress
        fz = os.path.getsize(file_path) / 1024 / 1024
        pa = math.ceil(fz / split_size)
        head, ext = os.path.splitext(os.path.abspath(file_path))
        archive_head = "".join((head, ext.replace(".", "_"))) + ".7z"
        for i in range(pa):
            check_file_name = "{}.{:03d}".format(archive_head, i + 1)
            if os.path.isfile(check_file_name):
                logger.debug("remove exists file | {}".format(check_file_name))
                os.remove(check_file_name)
        cmd_7z = ["7z", "a", "-v{}m".format(split_size), "-y", "-mx0", archive_head, file_path]
        proc = subprocess.Popen(cmd_7z, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if b"Everything is Ok" not in out:
            logger.error("7z output | {}".format(out.decode("utf-8")))
            logger.error("7z error | {}".format(err.decode("utf-8")))
            return file_path_7z_list

        for i in range(pa):
            file_path_7z_list.append("{}.{:03d}".format(archive_head, i + 1))
        # if origin file is 7z file rename it back
        if origin_file_path:
            os.rename(file_path, origin_file_path)
        return file_path_7z_list

    def do_file_split(file_path, split_size=MAX_SPLIT_SIZE):
        """caculate split size 
           example max split size is 1495 file size is 2000
           than the split part num should be int(2000 / 1495 + 0.5) = 2
           so the split size should be 1000 + 1000 but not 1495 + 505
           with the file size increase the upload risk would be increase too
        """
        file_size = os.path.getsize(file_path) / 2 ** 20
        split_part = math.ceil(file_size / split_size)
        new_split_size = math.ceil(file_size / split_part)
        logger.info("file size | {} | split num | {} | split size | {}".format(file_size, split_part, new_split_size))
        file_path_7z_list = file_split_7z(file_path, split_size=new_split_size)
        return file_path_7z_list
