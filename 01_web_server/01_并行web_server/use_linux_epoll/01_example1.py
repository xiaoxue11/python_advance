import socket

EOL1 = b'\n\n'
EOL2 = b'\n\r\n'
response  = b'HTTP/1.0 200 OK\r\nDate: Mon, 1 Jan 1996 01:01:01 GMT\r\n'
response += b'Content-Type: text/plain\r\nContent-Length: 13\r\n\r\n'
response += b'Hello, world!'

tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server_socket.bind(('',7890))
tcp_server_socket.listen(128)

new_client_socket, client_addr = tcp_server_socket.accept()
request = b''
while EOL1 not in request and EOL2 not in request:
    request += new_client_socket.recv(1024)
print(request.decode('utf-8'))
new_client_socket.send(response)
new_client_socket.close()
tcp_server_socket.close()