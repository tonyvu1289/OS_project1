from sector import *

class volume:
    def clusterstart_sector(self,cluster_num):
        return self.bootsector_size+self.FATsize_sector*self.Nr+self.clustersize_sector+cluster_num*self.block_size
    def __init__(self,volume_name,block_size=512) -> None:
        self.f = open(volume_name,"r+b")
        data_block = readblock(0,block_size,self.f)
        data = []
        sizes = [2,1,2,1,4,4,4]
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
    def addFile(self,dest,source):
        input = open(source,"r+b")

        new_entry = RDET_entry(bytearray(32))
        new_entry.filename= source.split('/')[-1]
        for entry in self.RDET_table:
            if entry.filename == new_entry.filename:
                print("Ten file '{}' da duoc dat! Vui long dat ten khac".format(entry.filename))
                return
        new_entry.filesize = os.path.getsize(source)
        new_entry.state= 0x20
        cluster_needed = (int)(new_entry.filesize/(self.clustersize_sector* self.block_size))+1
        cluster_list = []
        for i in range(len(self.FAT_table)):
            if(self.FAT_table[i]==0):
                cluster_list.append(i)
            if(len(cluster_list)==cluster_needed):
                break
        for i in range(len(cluster_list)-1):
            self.FAT_table[cluster_list[i]] = cluster_list[i+1]
        eof = 268435455

        self.FAT_table[cluster_list[-1]]= eof
        for i in range(cluster_needed):
            start = self.clusterstart_sector(cluster_list[i])
            for j in range(self.clustersize_sector):
                data = readblock(i*self.clustersize_sector+j,self.block_size,input)
                writeblock(data,start + j,self.block_size,self.f)
                
        new_entry.clusterstart = cluster_list[0]
        for i in range(len(self.RDET_table)):
            if(self.RDET_table[i].isNull()):
                self.RDET_table[i] = new_entry
                break
        # chưa xử lý tên trùng.
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
    def exportFile(self,out_dir,source):
        file_name = source.split('/')[-1]
        file_entry = -1
        for entry in self.RDET_table:
            if(file_name == entry.filename):
                file_entry = entry
                break
        if file_entry == -1:
            print("Khong ton tai file can export !")
            return
        cluster_list = []
        cur_cluster = file_entry.clusterstart
        while(cur_cluster != 268435455): #cur_cluster khac 0FFFFFFF
            cluster_list.append(cur_cluster)
            cur_cluster = self.FAT_table[cur_cluster]
        out = open(out_dir+file_name,'w+b')
        for j in range(len(cluster_list)):
            start = self.clusterstart_sector(cluster_list[j])
            for i in range(self.clustersize_sector):
                data = readblock(start+i,self.block_size,self.f)
                writeblock(data,j*8+i,self.block_size,out)
        out.close()
    def closeVolume(self):
        self.f.close()
    def clusterstart_sector(self,cluster_num):
        return (int)(self.bootsector_size+self.FATsize_sector*self.Nr+self.clustersize_sector+(cluster_num-2)*self.clustersize_sector)
class RDET_entry:
    def __init__(self,data_block) -> None:
        assert len(data_block)==32,"data_block of RDET not equal 32 bit ! Fuck you"
        data = []
        self.sizes = [23,1,4,4]
        i = 0
        for size in self.sizes:
            if(size == 23):
                data.append(data_block[i:i+size].decode('utf-8').split('\0')[0])
            else:
                data.append(int.from_bytes(data_block[i:i+size],'little'))
            i = i+size
        self.filename = data[0]
        self.state = data[1]
        self.clusterstart = data[2]
        self.filesize = data[3]
    def toBlock(self):
        byte_list = []
        by = bytes(self.filename,"utf-8")
        by += b'\0' * (23 - len(by))
        byte_list.append(by)
        byte_list.append(self.state.to_bytes(1,'little'))
        byte_list.append(self.clusterstart.to_bytes(4,'little'))
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
