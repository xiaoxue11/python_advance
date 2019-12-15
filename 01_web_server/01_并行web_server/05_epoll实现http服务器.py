import socket, select
import re


def receive_msg(epoll, fileno, connections, requests, responses):
    # get request end mark
    EOL1 = b'\n\n'
    EOL2 = b'\n\r\n'
    requests[fileno] += connections[fileno].recv(1024)
    if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
        request_lines = requests[fileno].decode('utf-8').splitlines()
        ret = re.match(r'[^/]+(/[^ ]*)', request_lines[0])
        file_names = ''
        if ret:
            file_names = ret.group(1)
        epoll.modify(fileno, select.EPOLLOUT)
        print('-'*40 + '\n' + requests[fileno].decode()[:-2])
        return file_names
    

def send_msg(epoll, fileno, connections, requests, responses, file_names):
    # get response body
    try:
        file_path = './html' + file_names
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
        # get response header
        response_header = b'HTTP/1.1 200 OK\r\n'
        response_header += b'Content-Length:%d\r\n' % len(response_body)
        response_header += b'\r\n'
        response = response_header+ response_body 
        responses[fileno] = response
        byteswritten = connections[fileno].send(responses[fileno])
        responses[fileno] = responses[fileno][byteswritten:]
        if len(responses[fileno]) == 0:
            epoll.modify(fileno, 0)
            connections[fileno].shutdown(socket.SHUT_RDWR)


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
    # create epoll object
    epoll = select.epoll()
    # register the listen socket
    epoll.register(tcp_server_socket.fileno(), select.EPOLLIN)
    # define a dict to store client sockets fileno
    connections = {}
    requests = {}
    responses = {}
    while True:
        # accept client message
        events = epoll.poll()
        for fileno, event in events:
            if fileno == tcp_server_socket.fileno():
                new_client_socket, client_addr = tcp_server_socket.accept()
                new_client_socket.setblocking(False)
                epoll.register(new_client_socket.fileno(), select.EPOLLIN)
                connections[new_client_socket.fileno()] = new_client_socket
                responses[new_client_socket.fileno()] = b''
                requests[new_client_socket.fileno()] = b''
            elif event & select.EPOLLIN:
                # receive data from client
                file_names = receive_msg(epoll, fileno, connections, requests, responses)
            elif event & select.EPOLLOUT:
                # send data to client
                send_msg(epoll, fileno, connections, requests, responses, file_names)
            elif event & select.EPOLLHUP:
                # remove client socket fileno from epoll, close client socket and del key-values
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
    # close socket
    tcp_server_socket.close()


if __name__ == '__main__':
    main()
