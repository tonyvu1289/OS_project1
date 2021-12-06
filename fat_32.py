from sector import *
import math
#EOF cluster is 268435455 (cause i like it)
#JK microsoft like it, not me =))
class volume:
    def changeVolumePass(self,oldpass,newpass):
        if(self.volume_pass != int.from_bytes(hashString_4byte(oldpass),'little')):
            print("mat khau cu khong dung!")
            return
        writeoffset(hashString_4byte(newpass),18,0,self.block_size,self.f)

    def clusterstart_sector(self,cluster_num):
        return self.bootsector_size+self.FATsize_sector*self.Nr+self.clustersize_sector+cluster_num*self.block_size
    def __init__(self,volume_name,block_size=512,password="") -> None:
        self.f = open(volume_name,"r+b")
        data_block = readblock(0,block_size,self.f)
        data = []
        sizes = [2,1,2,1,4,4,4,4]
        i = 0
        for size in sizes:
            data.append(int.from_bytes(data_block[i:i+size],'little'))
            i = i+size
        #print(data)
        self.block_size = data[0]
        self.clustersize_sector = data[1]
        self.bootsector_size = data[2]
        self.Nr = data[3] 
        self.volume_size = data[4]
        self.FATsize_sector = data[5]
        self.RDET_start = data[6]
        self.volume_pass = data[7]
        if(hashString_4byte(password) != data[7].to_bytes(4,'little')):
            print("Mat khau truy cap volume khong dung, vui long nhap lai!")
            assert False
        self.FAT_table = []
        self.RDET_table = []
        FAT_byte = bytes()
        #read FAT_table
        for i in range(self.FATsize_sector):
            FAT_byte +=(readblock(self.bootsector_size+i,self.block_size,self.f))
        for i in range((int)((self.FATsize_sector*self.block_size)/4)):
            self.FAT_table.append(int.from_bytes(FAT_byte[i*4:i*4+4],'little'))
        #read RDET_table
        for i in range(self.clustersize_sector):
            data_block = readblock(self.bootsector_size+self.FATsize_sector*self.Nr+i,self.block_size,self.f)
            for j in range(int(self.block_size/32)):
                self.RDET_table.append(RDET_entry(data_block[j*32:j*32+32]))
        # for RDET_ent in self.RDET_table:
        #     print(RDET_ent.isNull())
    def addFile(self,dest,source,password=""):
        input = open(source,"r+b")
        hash_value = int.from_bytes(hashString_4byte(password),'little')
        new_entry = RDET_entry(bytearray(32))
        new_entry.filename= source.split('/')[-1]
        #xử lý tên trùng
        for entry in self.RDET_table:
            if entry.filename == new_entry.filename:
                print("Ten file '{}' da duoc dat! Vui long dat ten khac".format(entry.filename))
                return
        #tạo entry, khởi tạo giá trị các thứ cho entry
        new_entry.filesize = os.path.getsize(source)
        new_entry.state= 0x20
        cluster_needed = (int)(math.ceil((new_entry.filesize/(self.clustersize_sector* self.block_size))))
        cluster_list = [] 
        #cluster list chứa các cluster trống khi chưa hash, không hash trên đây
        #tìm cluster_list là list các cluster trống sẽ dùng
        for i in range(len(self.FAT_table)):
            if(self.FAT_table[i]==0):
                cluster_list.append(i)
            if(len(cluster_list)==cluster_needed):
                break
        #ghi các cluster vào bảng FAT
        for i in range(len(cluster_list)-1):
            self.FAT_table[cluster_list[i]] = cluster_list[i+1]+hash_value
        eof = 268435455
        self.FAT_table[cluster_list[-1]]= eof + hash_value
        #ghi dữ liệu file vào phần data
        for i in range(cluster_needed):
            start = self.clusterstart_sector(cluster_list[i])
            for j in range(self.clustersize_sector):
                data = readblock(i*self.clustersize_sector+j,self.block_size,input)
                writeblock(data,start + j,self.block_size,self.f)
        #cập nhật cluster bắt đầu vào rdet
        new_entry.clusterstart = cluster_list[0]
        new_entry.clusternext = cluster_list[1]
        #cập nhật RDET_table
        for i in range(len(self.RDET_table)):
            if(self.RDET_table[i].isNull()):
                self.RDET_table[i] = new_entry
                break
        self.updateRDET()
        self.updateFAT()
    def updateRDET(self):
        byte_write = bytes()
        i = 0
        for entry in self.RDET_table:
            byte_write += entry.toBlock()
            if(len(byte_write)==self.block_size):
                writeblock(byte_write,self.bootsector_size+self.FATsize_sector*self.Nr+i,self.block_size,self.f)
                i = i+1
                byte_write= bytes()
        # for i in range(self.clustersize_sector):
        #     byte_write = bytes()
        #     for j in range(self.block_size)
            #writeblock(,self.bootsector_size+self.FATsize_sector*self.Nr+i,self.block_size,self.f)
    def updateFAT(self):
        block = bytes()
        k = 0
        for i in range(len(self.FAT_table)):
            block += self.FAT_table[i].to_bytes(4,'little')
            if(len(block)==self.block_size):
                writeblock(block,self.bootsector_size+k,self.block_size,self.f)
                k = k+1
                block = bytes()
    def exportFile(self,out_dir,source,password=""):
        file_name = source.split('/')[-1]
        file_entry = -1
        for entry in self.RDET_table:
            if(entry.filename == file_name):
                file_entry = entry
                break
        hash_value = int.from_bytes(hashString_4byte(password),'little')
        if file_entry == -1:
            print("Khong ton tai file can export !")
            return
        cluster_list = []
        cluster_list.append(file_entry.clusterstart)
        cluster_list.append(self.FAT_table[cluster_list[-1]]-hash_value)
        if(cluster_list[1] != file_entry.clusternext):
            if(password==""):
                print("File nay yeu cau mat khau! Vui long thuc hien lai thao tac cung voi mat khau!")
                return
            print("Sai mat khau !")
            return         
        while(cluster_list[-1] != 268435455): #cur_cluster khac 0FFFFFFF
            cluster_list.append(self.FAT_table[cluster_list[-1]]-hash_value)

        cluster_list = cluster_list[:-1]
        
        out = open(out_dir+file_name,'w+b')
        for j in range(len(cluster_list)):
            start = self.clusterstart_sector(cluster_list[j])
            for i in range(self.clustersize_sector):
                if (out.tell()+ self.block_size) > file_entry.filesize:
                    data = readoffset(start+i,0,file_entry.filesize-out.tell(),self.block_size,self.f)                
                    out.write(data)
                    break
                else:
                    data = readblock(start+i,self.block_size,self.f)                
                    writeblock(data,j*8+i,self.block_size,out)

        out.close()
    def closeVolume(self):
        self.f.close()
    def findEntry(self,listFolder,detTable):
        if(len(listFolder)==1):
            for entry in detTable:
                if entry.filename == listFolder[0]:
                    return entry
        if(listFolder[0]=='.'):
            new_detTable = self.RDET_table
        else:
            new_detTable = []
            for entry in detTable:
                if entry.filename == listFolder[0]:
                    new_detTable_start = self.clusterstart_sector(entry.clusterstart)
                    break
        for i in range(self.clustersize_sector):
            data_block = readblock(new_detTable_start+i,self.block_size,self.f)
            for j in range(int(self.block_size/32)):
                new_detTable.append(RDET_entry(data_block[j*32:j*32+32]))
        return self.findEntry(listFolder[1:],new_detTable)         
    def dir(self):
        for rdet in self.RDET_table:
            if not(rdet.isNull()):
                print("___{}".format(rdet.filename))           
    def clusterstart_sector(self,cluster_num):
        return (int)(self.bootsector_size+self.FATsize_sector*self.Nr+self.clustersize_sector+(cluster_num-2)*self.clustersize_sector)
    def updatePassword(self,file_name,password,newpass):
        #check pass và trả về cluster-list (cluster real)
        file_entry = -1
        for entry in self.RDET_table:
            if entry.filename == file_name:
                file_entry = entry
        hash_value = int.from_bytes(hashString_4byte(password),'little')
        if file_entry == -1:
            print("Khong co file nao ten {} de cap nhat password !".format(file_name))
            return
        cluster_list = []
        cluster_list.append(file_entry.clusterstart)
        cluster_list.append(self.FAT_table[cluster_list[-1]]-hash_value)
        if(cluster_list[1] != file_entry.clusternext):
            if(password==""):
                print("File nay yeu cau mat khau! Vui long thuc hien lai thao tac cung voi mat khau!")
                return
            print("Sai mat khau !")
            return         
        while(cluster_list[-1] != 268435455): #cur_cluster khac 0FFFFFFF
            cluster_list.append(self.FAT_table[cluster_list[-1]]-hash_value)
        cluster_list = cluster_list[:-1]
        hash_value = int.from_bytes(hashString_4byte(newpass),'little')
        for i in range(len(cluster_list)-1):
            self.FAT_table[cluster_list[i]] = cluster_list[i+1]+hash_value
        eof = 268435455
        self.FAT_table[cluster_list[-1]]= eof + hash_value
        self.updateFAT()
    def deleteFile(self,file_name,password=""):
        file_entry = -1
        for entry in self.RDET_table:
            if entry.filename == file_name:
                file_entry = entry
        hash_value = int.from_bytes(hashString_4byte(password),'little')
        if file_entry == -1:
            print("Khong co file nao ten {} de xoa !".format(file_name))
            return
        cluster_list = []
        cluster_list.append(file_entry.clusterstart)
        cluster_list.append(self.FAT_table[cluster_list[-1]]-hash_value)
        if(cluster_list[1] != file_entry.clusternext):
            if(password==""):
                print("File nay yeu cau mat khau! Vui long thuc hien lai thao tac cung voi mat khau!")
                return
            print("Sai mat khau !")
            return         
        while(cluster_list[-1] != 268435455): #cur_cluster khac 0FFFFFFF
            cluster_list.append(self.FAT_table[cluster_list[-1]]-hash_value)
        cluster_list = cluster_list[:-1]
        for cluster in cluster_list:
            self.FAT_table[cluster] = 0
        file_entry.toNull()
        self.updateRDET()
        self.updateFAT()
    def detTableOfFolder(self,folder_entry):
        detTable=[]
        for i in range(self.clustersize_sector):
            data_block = readblock(self.clusterstart_sector(folder_entry.clusterstart)+i,self.block_size,self.f)
            for j in range(int(self.block_size/32)):
                detTable.append(RDET_entry(data_block[j*32:j*32+32]))
        return detTable
    def updateDetTableOfFolder(self,folder_entry,new_det):
        if len(new_det)!=128:
            print("update function problem: new_det_table not equal 1 cluster")
            return
        start = self.clusterstart_sector(folder_entry.clusterstart)
        for i in range(self.clustersize_sector):
            data_block = b''.join(new_det[i*16:i*16+16])
            writeblock(data_block,start,self.block_size,self.f)
    # def addFolder(self,dir,folder_name):
    #     dir = dir.split('/')
    #     #parent_entry = self.findEntry(dir)
    #     new_entry = RDET_entry(bytearray(32))
    #     new_entry.filename= folder_name
    #     #xử lý tên trùng
    #     # for entry in self.RDET_table:
    #     #     if entry.filename == new_entry.filename:
    #     #         print("Ten file '{}' da duoc dat! Vui long dat ten khac".format(entry.filename))
    #     #         return
    #     #tạo entry, khởi tạo giá trị các thứ cho entry
    #     new_entry.filesize = self.clustersize_sector*self.block_size
    #     new_entry.state= 0x10
    #     cluster_needed = (int)(math.ceil((new_entry.filesize/(self.clustersize_sector* self.block_size))))
    #     cluster_list = [] 
    #     #update entry thư mục mới tạo vào SDET của thư mục cha
    #     self.updateDetTableOfFolder(parent_entry,self.detTableOfFolder(parent_entry).append(new_entry))
    #     #cluster list chứa các cluster trống khi chưa hash, không hash trên đây
    #     #tìm cluster_list là list các cluster trống sẽ dùng
    #     for i in range(len(self.FAT_table)):
    #         if(self.FAT_table[i]==0):
    #             cluster_list.append(i)
    #         if(len(cluster_list)==cluster_needed):
    #             break
    #     #ghi các cluster vào bảng FAT
    #     for i in range(len(cluster_list)-1):
    #         self.FAT_table[cluster_list[i]] = cluster_list[i+1]
    #     eof = 268435455
    #     self.FAT_table[cluster_list[-1]]= eof
    #     #ghi dữ liệu folder (SDET mới) vào phần data
    #     new_entry_detTable = []
    #     rdet_start = fat_32.RDET_entry(bytearray(32))
    #     rdet_cur = fat_32.RDET_entry(bytearray(32))
    #     rdet_cur.filename = "."
    #     rdet_cur.state = 0x10
    #     rdet_cur.clusterstart = cluster_list[0]
    #     rdet_cur.clusternext = 0 #khong co
    #     rdet_cur.filesize = self.block_size
    #     rdet_start.filename = ".."
    #     rdet_start.state = 0x10
    #     rdet_start.clusterstart = parent_entry.clusterstart #khong co
    #     rdet_cur.clusternext = 0 #khong co
    #     rdet_cur.filesize = self.block_size
    #     new_entry_detTable.append(rdet_cur)
    #     new_entry_detTable.append(rdet_start)
    #     self.updateDetTableOfFolder(new_entry,new_entry_detTable)
    #     #cập nhật cluster bắt đầu vào rdet
        
    #     #new_entry.clusternext = cluster_list[1]
    #     # self.updateRDET()
    #     self.updateFAT()
       
class RDET_entry:
    def __init__(self,data_block) -> None:
        assert len(data_block)==32,"data_block of RDET not equal 32 bit ! Fuck you"
        data = []
        self.sizes = [19,1,4,4,4]
        i = 0
        for size in self.sizes:
            if(size == 19):
                data.append(data_block[i:i+size].decode('utf-8').split('\0')[0])
            else:
                data.append(int.from_bytes(data_block[i:i+size],'little'))
            i = i+size
        self.filename = data[0]
        self.state = data[1]
        self.clusterstart = data[2]
        self.clusternext = data[3]
        self.filesize = data[4]
    def toNull(self):
        self.filename = ''
    def toBlock(self):
        byte_list = []
        by = bytes(self.filename,"utf-8")
        by += b'\0' * (19 - len(by))
        byte_list.append(by)
        byte_list.append(self.state.to_bytes(1,'little'))
        byte_list.append(self.clusterstart.to_bytes(4,'little'))
        byte_list.append(self.clusternext.to_bytes(4,'little'))
        byte_list.append(self.filesize.to_bytes(4,'little'))
        return b''.join(byte_list) 
    def isFolder(self):
        return self.state == 0x10
    def isFile(self):
        return self.state == 0x20                
    def isNull(self):
        return self.filename == ''
    def printscreen(self):
        print("{}\t{}\t{}\t{}".format(self.filename,self.state,self.clusterstart,self.filesize))
