
from pythonosc.udp_client import SimpleUDPClient

ip = "127.0.0.1"
port = 6001

client = SimpleUDPClient(ip, port)  # Create client
count = 1
while 1:
    count += 1
    input("enter to send")
    client.send_message("/", count)   # Send float message
