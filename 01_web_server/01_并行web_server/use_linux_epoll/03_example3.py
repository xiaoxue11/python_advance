import socket, select

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response  = b'HTTP/1.1 200 OK\r\nDate: Mon, 1 Oct 2019 14:42:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world! This is an interesting thing.'

tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server_socket.bind(('',7890))
tcp_server_socket.listen(128)
tcp_server_socket.setblocking(False)
# use epoll.Return an edge polling object, which can be used as Edge or 
# Level Triggered interface for I/O events.
# Create an epoll object
epoll = select.epoll()
# put tcp socket in epoll,Register a fd descriptor with the epoll object.
# select.EPOLLIN: available for read
epoll.register(tcp_server_socket.fileno(), select.EPOLLIN)
try:
    connections = {}
    requests = {}
    responses = {}
    while True:
        # Wait for events， until os detect data and inform process by events
        events = epoll.poll() 
        # Events are returned as a sequence of (fileno, event code) tuples. 
        # fileno is a synonym for file descriptor and is always an integer.
        for fileno, event in events:
            # if the fileno is listen socket
            # If a read event occurred on the socket server, 
            # then a new socket connection may have been created.
            if fileno == tcp_server_socket.fileno():
                # get new client socket and client address, default is block state
                connection, address = tcp_server_socket.accept()
                # set connection not block
                connection.setblocking(False)
                # register client socket fd descriptor
                epoll.register(connection.fileno(), select.EPOLLIN)
                # set key-value, key is fd descriptor and the value is the client socket
                connections[connection.fileno()] = connection
                # get current client socket requests
                requests[connection.fileno()]=b''
                # get currtent client socket responses
                responses[connection.fileno()] = response
            # if the fileno is client socket and available to read
            # If a read event occurred then read new data sent from the client.
            elif event & select.EPOLLIN:
                # get current fd descriptor and client request
                requests[fileno] += connections[fileno].recv(1024)
                # get request all
                if EOL1 in requests[fileno] or EOL2 in requests[fileno]:
                    # Once the complete request has been received, 
                    # then unregister interest in read events and register interest 
                    # in write (EPOLLOUT) events. Write events will occur when it is possible 
                    # to send response data back to the client.
                    epoll.modify(fileno, select.EPOLLOUT)
                    print('-'*40 + '\n' + requests[fileno].decode()[:-2])
            #  If a write event occurred on a client socket, 
            # it's able to accept new data to send to the client.
            elif event & select.EPOLLOUT:
                # return the length of send data
                byteswritten = connections[fileno].send(responses[fileno])
                # get value after the length value
                responses[fileno] = responses[fileno][byteswritten:]
                if len(responses[fileno]) == 0:
                    # Once the complete response has been sent, 
                    # disable interest in further read or write events.
                    epoll.modify(fileno, 0)
                    connections[fileno].shutdown(socket.SHUT_RDWR)
            # The HUP (hang-up) event indicates that the client socket has been disconnected 
            elif event & select.EPOLLHUP:
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
finally:
    epoll.unregister(tcp_server_socket.fileno())
    epoll.close()
    tcp_server_socket.close()             