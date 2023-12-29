import socket
from pathlib import Path
from multiprocessing import Process
from datetime import datetime
import requests
import json
def raw_body_to_dict(raw_body:str):
    raw_values_dict = raw_body.split("&")
    result = dict()
    for key_value in raw_values_dict:
        key, value = key_value.split("=")
        result[key] = value
    return result

def get_server(port=3000):

    HOST, PORT = '127.0.0.1',port

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind((HOST, PORT))
    my_socket.listen(1)

    print('Serving on port ', PORT)

    while True:
        connection, address = my_socket.accept()
        request = connection.recv(1024).decode('utf-8')
        string_list = request.split(' ')

        method = string_list[0]
        requesting_file = string_list[1]
        if method == "POST" and requesting_file == "/message":
            raw_body=request.split("\r\n\r\n")[1]
            body = raw_body_to_dict(raw_body)
            requests.post(f"http://{HOST}:5000/message",data=json.dumps(body))
        print('Client request ', requesting_file)

        myfile = requesting_file.split('?')[0]
        myfile = myfile.lstrip('/')
        if (myfile == ''):
            myfile = 'index.html'

        try:
            dirpath = Path(r"src")
            file = open(dirpath / myfile, 'rb')
            response = file.read()
            file.close()

            header = 'HTTP/1.1 200 OK\n'

            if (myfile.endswith(".jpg")):
                mimetype = 'image/jpg'
            elif (myfile.endswith(".css")):
                mimetype = 'text/css'
            else:
                mimetype = 'text/html'

            header += 'Content-Type: ' + str(mimetype) + '\n\n'

        except Exception as e:
            header = 'HTTP/1.1 404 Not Found\n\n'
            dirpath = Path(r"src")
            file = open(dirpath / "error.html", 'rb')
            response = file.read()
            file.close()

        final_response = header.encode('utf-8')
        final_response += response
        connection.send(final_response)
        connection.close()

def post_server(port):
    HOST, PORT = '127.0.0.1', port

    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    my_socket.bind((HOST, PORT))
    my_socket.listen(1)

    print('Serving on port ', PORT)

    while True:
        connection, address = my_socket.accept()
        request = connection.recv(2048).decode('utf-8')
        string_list = request.split(' ')

        method = string_list[0]
        if method != "POST":
            raise Exception("Unsupported method")
        http_path = string_list[1]
        if http_path == "/message":
            raw_body = request.split("\r\n\r\n")[1]
            body = json.loads(raw_body)
            with open(Path(r"src") / "storage" / "data.json", 'rb') as f:
                try:
                    storage_data = json.load(f)
                except Exception:
                    storage_data = {}
            storage_data[datetime.now().isoformat()] = body
            with open(Path(r"src") / "storage" / "data.json", 'w')as f:
                json.dump(storage_data, f)

        header = 'HTTP/1.1 200 OK\n'
        final_response = header.encode('utf-8')
        connection.send(final_response)
        connection.close()


if __name__ == "__main__":
    p1 = Process(target=get_server, args=(3000,))
    p1.start()
    p2 = Process(target=post_server, args=(5000,))
    p2.start()
    p1.join()
    p2.join()