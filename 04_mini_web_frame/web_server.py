import socket
import re
import sys
import multiprocessing
# import dynamic.mini_frame

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'

class WSGIserver():
    def __init__(self, port, app, static_path):
        # create tcp socket
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind port
        self.tcp_server_socket.bind(('',port))
        # set listen state
        self.tcp_server_socket.listen(128)
        # get frame app name
        self.application = app
        # get static file path
        self.static_path = static_path 


    def serve_client(self, new_client_socket):
        # receive client request
        request = b''
        while EOL1 not in request and EOL2 not in request:
            request += new_client_socket.recv(1024)
        # print(request)
        request_lines = request.decode('utf-8').splitlines()
        print(request_lines)
        # GET /index.html HTTP/1.1:match example
        file_name = ''
        ret = re.match(r'[^/]+(/[^ ]*)', request_lines[0])
        if ret:
            file_name = ret.group(1)
            if file_name == '/':
                file_name = '/index.html'
        if not file_name.endswith('.html'):
            file_path = self.static_path + file_name
            try:
                f = open(file_path, 'rb')
            except:
                response = 'HTTP/1.1 404 NOT FOUND\r\n'
                response += '\r\n'
                response += '------file not found------'
                new_client_socket.send(response.encode('utf-8'))
            else:
                # get response body
                file_contend = f.read()
                f.close()
                # response the client request
                # get response header
                response = 'HTTP/1.1 200 OK\r\n'
                response += '\r\n'
                new_client_socket.send(response.encode('utf-8'))
                new_client_socket.send(file_contend)
        else:
            env = {}
            env['file_path'] = file_name
            body = self.application(env, self.start_response_header)
            header = 'HTTP/1.1 {}\r\n'.format(self.status)
            for temp in self.response_headers:
                header += '{}:{}'.format(temp[0],temp[1])
                header +='\r\n'
            header += '\r\n'
            # print(header)
            response = header + body
            # print(response)
            new_client_socket.send(response.encode('utf-8'))

        new_client_socket.close()


    def start_response_header(self, status, headers):
        self.status = status
        self.response_headers = headers


    def server_run(self):
        # accept client message
        while True:
            new_client_socket, _ = self.tcp_server_socket.accept()
            # serve_client(new_client_socket)
            p = multiprocessing.Process(target=self.serve_client,args=(new_client_socket,))
            p.start()
            new_client_socket.close()
        # close socket
        tcp_server_socket.close()


def main():
    print(sys.argv)
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[1])
            frame_app_name = sys.argv[2]
        except:
            print('The port value is wrong')
            return
    else:
        print('please input command line as: python3 7890 mini_frame:application')
        return
    # mini_frame:application
    ret = re.match(r'([^:]+):(.*)', frame_app_name)
    if ret:
        frame_name = ret.group(1)
        app_name = ret.group(2)
    else:
        print('please input command line as: python3 7890 mini_frame:application')
        return

    with open('./web_server.conf', 'r') as f:
        path_info = eval(f.read())

    sys.path.append(path_info['dynamic_path'])
    frame = __import__(frame_name)
    app = getattr(frame, app_name)

    wsgi_server = WSGIserver(port, app, path_info['static_path'])
    wsgi_server.server_run()


if __name__ == '__main__':
    main()
