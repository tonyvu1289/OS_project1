from fat_32 import *
from sector import *

createVolume("test1.dat",2)
vol_1 = volume("test1.dat",512)
vol_1.addFile("./","./2_cluster.csv","VuCongDuy")
# vol_1.updatePassword("./2_cluster.csv","VuCongDuy","duydancer")
# vol_1.exportFile("./export/","2_cluster.csv","duydancer")
# vol_1.addFile("./","./5_cluster.docx")
# vol_1.deleteFile("2_cluster.csv")
vol_1.addFile("./","./6_cluster.txt")
# vol_1.exportFile("./export/",'./5_cluster.docx')
# vol_1.exportFile("./export/",'./6_cluster.txt')
# vol_1.exportFile("./export/",'./2_cluster.csv')
# vol_1.exportFile('./export/','./add.txt')
# vol_1.deleteFile("add.txt")
# vol_1.addFile("./","./report.docx")
# vol_1.exportFile("./export/",'./report.docx')
# vol_1.deleteFile("2_cluster.csv","duydancer")

vol_1.dir()
vol_1.closeVolume()
