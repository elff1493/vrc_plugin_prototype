import psutil
import os

tmp = psutil.net_connections()
pids = [x.pid for x in tmp]
process = filter(lambda p: p.pid in pids, psutil.process_iter())
data = [(i.pid, i.name(), i.exe()) for i in process]
outp = []
last = 0
while data:
    if data[0][0] - last:
        outp.append("port " + str(last) + " to " + str(data[0][0]) + " free")
    outp.append(data.pop(0))
    last = outp[-1][0]

for i in outp:
    try:
        print(i)
    except:
        pass