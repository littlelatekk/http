import http.server
import time
import socket
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import subprocess
import re
import requests
# 指定接收方服务器地址和端口
import psutil
import subprocess
import os
import threading
import csv
'''

host="192.168.1.217"
port=8000
'''
# 创建一个简单的HTTP请求处理器
handler = http.server.SimpleHTTPRequestHandler
data_folder = "."
compute_url="http://192.168.1.217:8000"
#compute_url="http://192.168.1.212:8000"
#compute_url="http://192.168.1.213:8000"
#compute_url="http://192.168.1.214:8000"
#compute_url="http://192.168.1.215:8000"
global k
k=0

def getnumber():
    result = subprocess.run(['top', '-n', '1', 'b'], capture_output=True, text=True)
    count_nab = len(re.findall('nab', result.stdout))
    count_perlbench = len(re.findall('perlbench', result.stdout))
    count_povray = len(re.findall('povray', result.stdout))
    return int(count_nab/8),int(count_perlbench/8),int(count_povray/8)

def getvCPU():
    interval = 1
    vcpu_utilization = psutil.cpu_percent(interval=1, percpu=True)

    avg_utilization = sum(vcpu_utilization) / len(vcpu_utilization)
    print(f"Average vCPU utilization: {avg_utilization}%")
    return avg_utilization

class SimpleHTTPRequestHandler(handler):
    #发送请求

    # 处理POST请求
    def do_POST(self):
        # 设置响应状态码为200（成功）
        self.send_response(200)

        # 设置响应头，指定返回数据的类型为文本/html
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        # 自定义要返回的数据
        response_data = "Hello, this is the response data for the POST request!"

        # 将数据以字节流的形式写入到响应中
        self.wfile.write(response_data.encode())

    # 处理GET请求
    def do_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        print(query_params)
        query = query_params.get('query',[''])[0]
        app = query_params.get('app',[''])[0]

        #self.run_monitor_function(app)
        # 设置响应状态码为200（成功）
        self.send_response(200)
        # 自定义要返回的数据
        if query == 'run_app':
            # 设置响应头，指定返回数据的类型为文本/html
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response_data = "vm run app"
            monitor_thread = threading.Thread(target=self.run_monitor_function,args=(app,))
            monitor_thread.start()
            self.wfile.write(response_data.encode())
        if query == 'vcpu':
            # 设置响应头，指定返回数据的类型为文本/html
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if getvCPU()<10:
                response_data = "idle"
            else:
                response_data = "busy"
            self.wfile.write(response_data.encode())
        if query == 'number':
            # 设置响应头，指定返回数据的类型为文本/html
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            nab,per,pov=getnumber()
            response_data={
                "numberofper":per,
                "numberofpov":pov,
                "numberofnab":nab
            }
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
        #if query == 'data':
        #    response_data = "receive data, sending order to "+str(k)
        # 将数据以字节流的形式写入到响应中



    def run_monitor_function(self,app):
        self.run_function(app)
        time.sleep(5)
        target_url = "http://192.168.1.216:9000"
        if(getvCPU()<5):
            params={"query":"check","app":app}
            response = requests.get(target_url, params=params)
            if response.status_code == 200:
                # 打印接收到的响应
                print(response.text)
        else:
            params={"query":"finish","app":app}
            response = requests.get(target_url, params=params)
            if response.status_code == 200:
                print(response.text)

    def run_function(self,app):
        working_directory = "/home/xcn/cpu2017"
        os.chdir(working_directory)
        #os.system("bash -c 'source shrc'")
        subprocess.run(["bash", "-c", "source shrc"])
        working_directory = "/home/xcn/cpu2017/config"
        os.chdir(working_directory)
        if (app == "BSSN"):
            #os.system("bash -c 'runcpu --config=try1 --action=run 607.cactuBSSN_s'")
            subprocess.run(["bash", "-c", "runcpu --config=tryc=1 --action=run 607.cactuBSSN_s"])
        elif(app == "imagick"):
            #os.system("bash -c 'runcpu --config=try1 --action=run 638.imagick_s'")
            subprocess.run(["bash", "-c", "runcpu --config=tryc=1 --action=run 638.imagick_s"])
        elif(app == "500"):
            subprocess.run(["bash", "-c", "runcpu --config=tryc=8 --action=run 500.perlbench_r"])
        elif(app == "511"):
            subprocess.run(["bash", "-c", "runcpu --config=tryc=8 --action=run 511.povray_r"])
        elif(app == "544"):
            subprocess.run(["bash", "-c", "runcpu --config=tryc=8 --action=run 544.nab_r"])

def test():
    print("test")

def start_server():
    hostname = socket.gethostname()

    ip = socket.gethostbyname(hostname)
    print(ip)
    sending_host = ip
    sending_port = 8000
    # 创建HTTP服务器，并指定请求处理类为我们自定义的SimpleHTTPRequestHandler
    server = HTTPServer((sending_host, sending_port), SimpleHTTPRequestHandler)

    print(f"Starting server on http://{sending_host}:{sending_port}")
    server.serve_forever()

def send_order(url,apptype):
    param = {"query":"run_app","app":apptype}
    response = requests.get(url=url, params=param)

    if response.status_code == 200:
        response_data = response.text
        print("数据发送成功！")
    else:
        print(f"数据发送失败，状态码：{response.status_code}")

if __name__ == "__main__":
    #ftest()
    '''
    collect_data_path = "/root/code/collect_data.py"
    process = subprocess.Popen(["python3", collect_data_path], preexec_fn=os.setpgrp())

    observer_data_path = "/root/code/observer.py"
    process = subprocess.Popen(["python3", observer_data_path],preexec_fn=os.setpgrp())
    '''
    start_server()


