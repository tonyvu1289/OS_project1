from fat_32 import *
from sector import *

createVolume("test1.dat",2)
vol_1 = volume("test1.dat",512)
vol_1.addFile("./","./add.txt")
vol_1.exportFile('./export/','./add.txt')
vol_1.closeVolume()
