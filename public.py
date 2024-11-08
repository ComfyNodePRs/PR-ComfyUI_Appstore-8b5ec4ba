import hashlib
import os
import json

import stat
import uuid

from datetime import datetime
import folder_paths
import sys
import uuid
import re
from comfy.cli_args import parser
import urllib
import urllib.request
import urllib.parse
args = parser.parse_args()
if args and args.listen:
    pass
else:
    args = parser.parse_args([])
import time



def read_json_from_file(name, path='json/', type_1='json'):
    base_url = find_project_custiom_nodes_path() + 'ComfyUI_Appstore/config/' + path
    if not os.path.exists(base_url + name):
        return None
    with open(base_url + name, 'r') as f:
        data = f.read()
        if data == '':
            return None
        if type_1 == 'json':
            try:
                data = json.loads(data)
                return data
            except ValueError as e:
                return None
        if type_1 == 'str':
            return data
def write_json_to_file(data, name, path='json/', type_1='str'):
    
    base_url = find_project_custiom_nodes_path() + 'ComfyUI_Appstore/config/' + path
    if not os.path.exists(base_url):
        os.makedirs(base_url)
    if type_1 == 'str':
        str_data = str(data)
        with open(base_url + name, 'w') as f:
            f.write(str_data)
    elif type_1 == 'json':
        with open(base_url + name, 'w') as f:
            json.dump(data, f, indent=2)

def get_output(uniqueid, path='json/api/'):
    output = read_json_from_file(uniqueid, path, 'json')
    if output is not None:
        return output
    return None

def get_port_from_cmdline():
    for i, arg in enumerate(sys.argv):
        if arg == '--port' and i + 1 < len(sys.argv):
            try:
                return int(sys.argv[i + 1])
            except ValueError:
                pass
        match = re.search(r'--port[=\s]*(\d+)', arg)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
    return 8188




def replace_time_format_in_filename(filename_prefix):
    def compute_vars(input):
        now = datetime.now()
        custom_formats = {
            "yyyy": "%Y",
            "yy": "%y",
            "MM": "%m",
            "dd": "%d",
            "HH": "%H",
            "mm": "%M",
            "ss": "%S",
        }
        date_formats = re.findall(r"%date:(.*?)%", input)
        for date_format in date_formats:
            original_format = date_format
            for custom_format, strftime_format in custom_formats.items():
                date_format = date_format.replace(custom_format, strftime_format)
            formatted_date = now.strftime(date_format)
            input = input.replace(f"%date:{original_format}%", formatted_date)
        return input
    return compute_vars(filename_prefix)
def is_execution_model_version_supported():
    try:
        import comfy_execution
        return True
    except:
        return False



def find_project_custiom_nodes_path():
    absolute_path = folder_paths.folder_names_and_paths["custom_nodes"][0][0]
    if not absolute_path.endswith(os.sep):
        absolute_path += os.sep
    return absolute_path


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(('%012X' % mac)[i:i + 2] for i in range(0, 12, 2))
def generate_unique_subdomain(mac_address, port):
    unique_key = f"{mac_address}:{port}"
    hash_object = hashlib.sha256(unique_key.encode())
    subdomain = hash_object.hexdigest()[:12]
    return subdomain
def set_executable_permission(file_path):
    try:
        st = os.stat(file_path)
        os.chmod(file_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"Execution permissions set on {file_path}")
    except Exception as e:
        print(f"Failed to set execution permissions: {e}")
def download_file(url, dest_path):
    try:
        
        with urllib.request.urlopen(url) as response, open(dest_path, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
    except Exception as e:
        print(f"Failed to download the file: {e}")
