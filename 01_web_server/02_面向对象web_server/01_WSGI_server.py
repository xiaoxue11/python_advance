import socket
import re
import threading


EOL1 = b'\n\n'
EOL2 = b'\n\r\n'

class WSGI_Server():
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
        
        file_path = './html' + file_name
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
            # get response header
            response = 'HTTP/1.1 200 OK\r\n'
            response += '\r\n'
            new_client_socket.send(response.encode('utf-8'))
            new_client_socket.send(file_contend)
        new_client_socket.close()


    def server_run(self):
        # create tcp socket
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind port
        tcp_server_socket.bind(('',7788))
        # set listen state
        tcp_server_socket.listen(128)
        # accept client message
        while True:
            new_client_socket, _ = tcp_server_socket.accept()
            # print(client_addr)
            # serve client request and response
            # serve_client(new_client_socket)
            p = threading.Thread(target=self.serve_client,args=(new_client_socket,))
            p.start()
           # new_client_socket.close()
        # close socket
        tcp_server_socket.close()

def main():
    wsgi = WSGI_Server()
    wsgi.server_run()


if __name__ == '__main__':
    main()
