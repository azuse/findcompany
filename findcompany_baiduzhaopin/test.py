import os 

def writePID():
    pidfile = open("mainPID.txt", "w")
    pidfile.write(str(os.getpid()))
    pidfile.flush()
    pidfile.close()

print("233")
writePID()