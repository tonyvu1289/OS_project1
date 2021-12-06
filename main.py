from fat_32 import *
from sector import *

# createVolume("test1.dat",2,"passwordforvolume")
# vol_1 = None
# password = ""
# while(True):
#     try:
#         password = input()
#         vol_1 = volume("test1.dat",512,password)
#         break
#     except:
#         continue
# vol_1.addFile("./","./2_cluster.csv","VuCongDuy")
# # vol_1.updatePassword("./2_cluster.csv","VuCongDuy","duydancer")
# # vol_1.exportFile("./export/","2_cluster.csv","duydancer")
# # vol_1.addFile("./","./5_cluster.docx")
# # vol_1.deleteFile("2_cluster.csv")
# vol_1.addFile("./","./6_cluster.txt")
# # vol_1.exportFile("./export/",'./5_cluster.docx')
# vol_1.exportFile("./export/",'./6_cluster.txt')
# vol_1.exportFile("./export/",'./2_cluster.csv')
# vol_1.exportFile('./export/','./add.txt')
# vol_1.deleteFile("add.txt")
# vol_1.addFile("./","./report.docx")
# vol_1.exportFile("./export/",'./report.docx')
# vol_1.deleteFile("2_cluster.csv","duydancer")
# vol_1.dir()
# vol_1.closeVolume()
volume_name=""
password =""
volume_size_gb = 0
choice = 0
while(choice!=1):
    print("1. Doc volume hien co ")
    print("2. Tao 1 volume moi hoan toan")
    print("0.Thoat khoi chuong trinh")
    choice = int(input())
    if choice == 1:
        print("Nhap ten file :")
        volume_name = input()

        while(True):
            try:
                print("Nhap mat khau cho volume. Neu khong co mat khau thi bam enter de bo qua :")
                password = input()
                vol_1 = volume(volume_name,512,password)
                break
            except:
                continue
    elif choice == 2:
        print("Nhap ten file :")
        volume_name = input()
        print("Nhap mat khau cho volume. Neu khong co mat khau thi bam enter de bo qua :")
        password = input()
        print("Nhap kich thuoc volume (tinh theo gb):")
        volume_size_gb = int(input())
        choice = createVolume(volume_name,volume_size_gb,password)
    elif choice ==0:
        exit()
while(choice!=0):
    vol_1.dir()
    print("1. Dat/Doi mat khau 1 tap tin(neu khong co mat khau thi mat khau mac dinh la 1 chuoi ky tu rong) ")
    print("2. Chep (import) 1 tap tin tu ben ngoai vao")
    print("3. Xuat(outport) tap tin ben trong volume ra ben ngoai")
    print("4. Xoa 1 tap tin trong volume")
    print("5.Doi mat khau cho volume")
    print("0.Thoat khoi chuong trinh")
    choice = int(input())
    if choice == 1 :
        print("Nhap ten tap tin muon doi mat khau:")
        file_name = input()
        print("Nhap mat khau cu:")
        old_pass = input()
        print("Nhap mat khau moi:")
        new_pass = input()
        vol_1.updatePassword(file_name,old_pass,new_pass)
    elif choice == 2:
        print("Nhap duong dan tap tin tu o ben ngoai : ")
        outside_dir = input()
        print("Thiet lap mat khau cho file nay, vui long nhap mat khau(neu khong muon dat mat khau thi bam enter de bo qua): ")
        password = input()
        try:
            vol_1.addFile("./",outside_dir,password)
        except:
            print("Tao file khong thanh cong do duong dan khong ton tai!")
    elif choice == 3:
        print("Nhap duong dan thu muc muon xuat ra : ")
        outside_dir = input()
        print("Nhap ten file : ")
        file_name = input()
        print("Nhap mat khau cua file")
        password = input()
        vol_1.exportFile(outside_dir,file_name,password)
    elif choice == 4:
        print("Nhap ten file : ")
        file_name = input()
        print("Nhap mat khau cua file")
        password = input()
        try:
            vol_1.deleteFile(file_name,password)
        except:
            print("File khong ton tai")
    elif choice == 5:
        print("Nhap mat khau cu :")
        old_pass = input()
        print("Nhap mat khau moi : ")
        new_pass = input()
        vol_1.changeVolumePass(old_pass,new_pass)
