# -*- coding: utf-8 -*-
import argparse
import glob
import time
import csv
import os

parser = argparse.ArgumentParser()
parser.add_argument('--scan_dir', type=str, default='.', help="the directory to scan boxs")
parser.add_argument('--sub_dir', type=bool, default=False, help="whether to include subdirectories")
parser.add_argument('--only_img', type=bool, default=False, help="whether to scan only image extensions")
args = parser.parse_args()

def create_result_file(data):
    str_time = time.strftime('%y%m%d%H%M%S', time.localtime())
    result_file = f'result_{str_time}.csv'
    if not os.path.exists(result_file):
        with open(result_file, 'w', newline='') as f:
            csv.writer(f).writerow(data)
    return result_file

def append_result_data(result_file, data):
    with open(result_file, 'a', newline='') as f:
        csv.writer(f).writerow(data)

def main():
    scan_dir = os.path.abspath(args.scan_dir)
    if not os.path.isdir(scan_dir):
        print('wrong path')
        exit(0)

    try:
        if args.sub_dir:
            scan_path = os.path.join(scan_dir, '**')
        else:
            scan_path = scan_dir

        img_ext_list = ['.png', '.jpg', '.jpeg', '.gif', '.webp']
        if args.only_img:
            ext_list = [f'*{ext}' for ext in img_ext_list]
        else:
            ext_list = ['*']

        file_list = [scan_dir]
        for ext in ext_list:
            file_list.extend(glob.glob(os.path.join(scan_path, ext), recursive=True))
        
        num_file = len(file_list)
        result_file = create_result_file(['file_name', 'is_box'])

        img_sig_list = [b'\x60\x82', b'\xFF\xD9', b'\x00\x3B']
        zip_sig = b'\x50\x4B\x05\x06'
        certain_count = 0
        suspect_count = 0
        for i, file in enumerate(file_list):
            if os.path.isdir(file):
                is_box = 'dir'
            else:
                file_size = os.path.getsize(file)
                if file_size < 100:
                    is_box = 'not'
                else:
                    with open(file, 'rb') as f:
                        f.seek(4, 0)
                        is_webp = int.from_bytes(f.read(4), byteorder='little') + 8
                        f.seek(-22, 2)
                        is_zip = f.read(4)
                        f.seek(-2, 2)
                        is_img = f.read()
                    
                    if is_zip == zip_sig:
                        is_box = 'certain'
                        certain_count += 1
                    elif is_webp == file_size or is_img in img_sig_list:
                        is_box = 'not'
                    else:
                        file_ext = os.path.splitext(file)[1]
                        if args.only_img or file_ext in img_ext_list:
                            is_box = 'suspect'
                            suspect_count += 1
                        else:
                            is_box = 'unknown'

            append_result_data(result_file, [file, is_box])
            print(f'({i+1}/{num_file}) Scan')
    except KeyboardInterrupt:
        if not 'num_file' in locals():
            num_file = 0
            certain_count = 0
            suspect_count = 0
    finally:
        print(f'box(suspect)/total: {certain_count}({suspect_count})/{num_file} Completed')

if __name__ == '__main__':
    main()
