from http.server import SimpleHTTPRequestHandler, HTTPServer,BaseHTTPRequestHandler
import json
import yaml
import os 
import datetime
import socketserver
from io import BytesIO
class handler(SimpleHTTPRequestHandler):
    def do_GET(self):

        if self.path == '/getdata':
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            data_json_conv = json.dumps(data_json)
            self.wfile.write(data_json_conv.encode("utf-8"))
            return
        
        if not self.path.startswith('/data'):
             self.send_response_only(404)
             return
        
        super().do_GET()
        return
    

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()


        #send data length as well
        length  = int(self.headers.get('content-length'))
        data = self.rfile.read(length)
        time = str(datetime.datetime.now()).replace(' ','_').replace(":","_")
        with open(f"eye_tracking_data/{time}.txt",'w') as file:
            print("got data")
            file.write(str(data,encoding='utf-8'))
        print(data)
        message = "Hello, World! Here is a POST response"
        self.wfile.write(bytes(message, "utf8"))

        return


    def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()

data_json = {"recipies" : {},"recipie_names" : []}
data_path = "./data"
recipies = os.listdir(data_path)
recipies = list(filter(lambda path : not ".yaml" in path,recipies))

with open("data/localisation.yaml") as file:
    localisation_data = yaml.full_load(file)

 
for recipie in recipies:

    data_json["recipie_names"].append(localisation_data["recipie_names"].pop())
    data_json["recipies"][recipie] = []
    steps = os.listdir(f"{data_path}/{recipie}")
    steps.sort(key=lambda x : int(x.split("_")[-1]))
    for i,step in enumerate(steps):
        data_json["recipies"][recipie].append({})
        step_data = os.listdir(f"{data_path}/{recipie}/{step}")
        data_json["recipies"][recipie][i]['text'] = list(map(lambda x : f"{data_path}/{recipie}/{step}/{x}",filter(lambda x : ".txt" in x,step_data)))
        data_json["recipies"][recipie][i]['image'] = list(map(lambda x : f"{data_path}/{recipie}/{step}/{x}",filter(lambda x : ".jpeg" in x,step_data)))
        data_json["recipies"][recipie][i]['video'] = list(map(lambda x : f"{data_path}/{recipie}/{step}/{x}",filter(lambda x : ".mp4" in x,step_data)))






    
with socketserver.TCPServer(("", 8000), handler) as httpd:
    print("Server running at port", 8000)
    httpd.serve_forever()