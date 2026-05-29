"""暗标检查工具 - 桌面应用入口 v1.0.1"""
import os
import sys
import threading
import time
import shutil
import urllib.parse
import webview
import uvicorn

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)

def start_backend():
    backend_path = resource_path('backend')
    os.chdir(backend_path)
    sys.path.insert(0, backend_path)
    import main as backend_main
    uvicorn.run(backend_main.app, host='127.0.0.1', port=8000, log_level='error')

def wait_for_backend():
    import urllib.request
    for i in range(20):
        try:
            urllib.request.urlopen('http://127.0.0.1:8000/')
            return True
        except:
            time.sleep(0.3)
    return False

class Api:
    def save_fixed_file(self, file_id, filename):
        safe_name = os.path.basename(filename or f'fixed_{file_id}.docx')
        if not safe_name.lower().endswith('.docx'):
            safe_name += '.docx'

        paths = webview.windows[0].create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=safe_name,
            file_types=('Word 文档 (*.docx)',)
        )
        if not paths:
            return {"success": False, "cancelled": True}

        target_path = paths[0]
        download_url = f'http://127.0.0.1:8000/api/download/{urllib.parse.quote(file_id)}'
        with urllib.request.urlopen(download_url, timeout=120) as response, open(target_path, 'wb') as output:
            shutil.copyfileobj(response, output)
        return {"success": True, "path": target_path}

if __name__ == '__main__':
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    print("正在启动...")
    wait_for_backend()
    print("启动完成")

    window = webview.create_window(
        '暗标检查工具',
        url='http://127.0.0.1:8000',
        width=1400,
        height=900,
        min_size=(1000, 700),
        js_api=Api()
    )
    webview.start()
