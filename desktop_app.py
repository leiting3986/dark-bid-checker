"""暗标检查工具 - 桌面应用入口"""
import os
import sys
import threading
import time
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
        min_size=(1000, 700)
    )
    webview.start()
