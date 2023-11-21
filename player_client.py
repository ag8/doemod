import socket

def main():
    host = "192.168.68.139"
    port = 12348

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    name = input(client_socket.recv(1024).decode())
    client_socket.send(name.encode())

    while True:
        input("Press Enter to buzz...")
        client_socket.send(b"buzz")

    client_socket.close()

if __name__ == "__main__":
    main()
