import socket
import re
import multiprocessing
import sys


class WSGI_Server:

    def __init__(self, port, app, static_path):
        # create tcp socket
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind port
        self.tcp_server_socket.bind(('',port))
        # set listen state
        self.tcp_server_socket.listen(128)
        # get mini web frame name and app function
        self.application = app
        # get statci path
        self.static_path = static_path

    def serve_client(self, new_client_socket):
        # receive client request
        request = new_client_socket.recv(1024).decode('utf-8')
        # print(request)
        request_lines = request.splitlines()
        # print(request_lines)
        # GET /index.html HTTP/1.1:match example
        ret = re.match(r'[^/]+(/[^ ]*)', request_lines[0])
        file_name = ''
        if ret:
            file_name = ret.group(1)
            if file_name == '/':
                file_name = '/index.html'
        # if file_name not endswith .html, web server thinks it is a static request, 
        # direct get static infor and return response to browser.
        print(file_name)
        if not file_name.endswith('.html'): 
            file_path = self.static_path + file_name
            try:
                f = open(file_path, 'rb')
            except:
                response = 'HTTP/1.1 404 NOT FOUND\r\n'
                response += '\r\n'
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
            env['file_path']= file_name
            body = self.application(env, self.set_response_header)
            header = 'HTTP/1.1 {}\r\n'.format(self.status)
            for temp in self.headers:
                header += '{}:{}\r\n'.format(temp[0], temp[1])
            header += '\r\n'
            response = header + body
            new_client_socket.send(response.encode('utf-8'))
        new_client_socket.close()

    def set_response_header(self, status, headers):
        self.status = status
        self.headers = headers

    def runforever(self):
        while True:
            # accept client message
            new_client_socket, _ = self.tcp_server_socket.accept()
            # serve client request and response
            p = multiprocessing.Process(target=self.serve_client,args=(new_client_socket,))
            p.start()
            new_client_socket.close()
        # close socket
        self.tcp_server_socket.close()


def main():
    '''main process, use method runforever'''
    if len(sys.argv) == 3:
        try:
            port = int(sys.argv[1])
            frame_app_name = sys.argv[2]
        except:
            print('The port value is wrong.')
            return
    else:
        print('please input value as following')
        print('python3 web_server.py 7788 mini_web:application')
        return 
    # mini_web:application
    ret = re.match(r'([^:]+):(.*)', frame_app_name)
    if ret:
        frame_name = ret.group(1)
        app_name = ret.group(2)
    else:
        print('please input value as following')
        print('python3 web_server.py 7788 mini_web:application')
        return 

    with open('./web_server.conf','r') as f:
        conf_info = eval(f.read())

    sys.path.append(conf_info['dynamic_path'])
    # import frame_name it will find frame_name.py
    frame = __import__(frame_name)
    app = getattr(frame, app_name)
    wgsi_server = WSGI_Server(port, app, conf_info['static_path'])
    wgsi_server.runforever()


if __name__ == '__main__':
    main()