import socket
import re

def serve_client(new_client_socket, request):
    request_lines = request.splitlines()
    # GET /index.html HTTP/1.1
    ret = re.match(r'[^/]+(/[^ ]*)', request_lines[0])
    if ret:
        file_name = ret.group(1)
        print(file_name)
    # get response body
    file_path = './html' + file_name
    try:
        f = open(file_path, 'rb')
    except:
        response = 'HTTP/1.1 404 NOT FOUND\r\n'
        response += '\r\n'
        response += '------file not found-----'
        new_client_socket.send(response.encode('utf-8'))
    else:
        file_content = f.read()
        f.close()
        # response the client request
        # get response body
        response_body = file_content
        print(len(response_body))
        # get response header
        response_header = 'HTTP/1.1 200 OK\r\n'
        response_header += 'Content-Length:%d\r\n' % len(response_body)
        response_header += '\r\n'
        response = response_header.encode('utf-8') + response_body 
        new_client_socket.send(response)
        # new_client_socket.close()


def main():
    # create tcp socket
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set port socket reuse
    tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind port
    tcp_server_socket.bind(('',7788))
    # set listen state
    tcp_server_socket.listen(128)
    # set tcp socket block state false
    tcp_server_socket.setblocking(False)
    # create client socket list
    client_sockets = []
    while True:
        # accept client message
        try:
            new_client_socket, _ = tcp_server_socket.accept()
        except:
            pass
        else:
            print('A new client comes')
            # set new client socket block state false
            new_client_socket.setblocking(False)
            client_sockets.append(new_client_socket)
            # print(client_sockets)
        for client_socket in client_sockets:
            try:
                recv_data = client_socket.recv(1024).decode('utf-8')
            except:
                pass
            else:
                if recv_data:
                    serve_client(client_socket, recv_data)
                else:
                    client_socket.close()
                    client_sockets.remove(client_socket)
    # close socket
    tcp_server_socket.close()


if __name__ == '__main__':
    main()
