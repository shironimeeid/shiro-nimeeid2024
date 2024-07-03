import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("https://5640-180-242-216-251.ap.ngrok.io ", 15933))

print(client.recv(1024.decode())
client.send ("".encode())