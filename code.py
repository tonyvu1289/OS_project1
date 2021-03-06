from os import fdopen, read, write
import os

def createNullFile_cluster(cluster:int,f):
    size = cluster*8*512
    f.seek(size-1)
    f.write(b"\0")
def createNullFile_gb(num_gb:int,f):
    size = 1073741824* num_gb
    f.seek(size-1)
    f.write(b"\0")
def writeblock(byte_val,block_num,block_size,f):
    f.seek(block_num*block_size)
    byte_block = b''.join([byte_val,bytearray(block_size)])[:512] # write 
    f.write(byte_block)
def readblock(block_num,block_size,f):
    f.seek(block_num*block_size)
    return f.read(block_size)
def writeoffset(byte_val,offset_num,block_num,block_size,f):
    block = readblock(block_num,block_size,f)
    # print(type(block[offset_num+byte_val:]))
    new_block = b''.join([block[:offset_num],byte_val,block[offset_num+len(byte_val):]])
    writeblock(new_block,block_num,block_size,f)
def readoffset(block_num,offset_num,offset_size,block_size,f):
    block = readblock(block_num,block_size,f)
    return block[offset_num:offset_num+offset_size]
 
def createVolume(volume_name,volume_size_gb): 
    '''
    volume_size : Tính theo gb
    '''
    if(os.path.exists(volume_name)):
        print("Khong the khoi tao file moi do ten file '{}' da ton tai !".format(volume_name))
        return
    f = open(volume_name,'w+b')
    createNullFile_gb(volume_size_gb,f)

    header_list = []
    block_size = 512 # 1 sector = 512 byte
    clustersize_sector = 8 #1 cluster = 8 sector
    volume_size = int(volume_size_gb*1000000/block_size)
    bootsector_size = 1 # bootsector chiếm 1 sector
    N_r = 2 #số bảng FAT
    print(((block_size*clustersize_sector)/(4)+N_r))
    FAT_size = int((volume_size-1)/((block_size*clustersize_sector)/(4)+N_r))+1
    RDET_start = (int)((int)(bootsector_size+FAT_size*N_r)/(int)(clustersize_sector))+1
    header_list.append(block_size.to_bytes(2,'little'))
    header_list.append(clustersize_sector.to_bytes(1,'little'))
    header_list.append(bootsector_size.to_bytes(2,'little'))
    header_list.append(N_r.to_bytes(1,'little'))
    header_list.append(volume_size.to_bytes(4,'little'))
    header_list.append(FAT_size.to_bytes(4,'little'))
    header_list.append(RDET_start.to_bytes(4,'little'))
    # list : [header_list(2byte),cluster_size(1 byte)] => join => byte(3byte)
    writeblock(b''.join(header_list),0,block_size,f)
    temp = 268435455
    two_element_FAT = temp.to_bytes(4,'little') + temp.to_bytes(4,'little')
    writeblock(two_element_FAT,bootsector_size,block_size,f)
    f.close()

class volume:
    def __init__(self,volume_name,block_size=512) -> None:
        self.f = open(volume_name,"r+b")
        data_block = readblock(0,block_size,self.f)
        data = []
        sizes = [2,1,2,1,4,4,4]
        i = 0
        for size in sizes:
            data.append(int.from_bytes(data_block[i:i+size],'little'))
            i = i+size
        print(data)
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
            data = readblock(i,self.block_size,input)
            writeblock(data,self.bootsector_size+self.FATsize_sector*self.Nr+self.clustersize_sector+cluster_list[i],self.block_size,self.f)
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
    def closeVolume(self):
        self.f.close()
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
# createVolume("test1.dat",2)
vol_1 = volume("test1.dat",512)
# vol_1.addFile("./","./add.txt")
vol_1.closeVolume()
# f = open("MyFS.dat","r+b")
# block_size = 512
# createNullFile_cluster(1,f)
# int_val = 12
# byte_val = int_val.to_bytes(2,'little')

# # #writeblock(byte_val,0,block_size,f)
# writeoffset(byte_val,3,0,block_size,f)
# byte_val = readoffset(0,3,2,block_size,f)
# print(int.from_bytes(byte_val,'little'))
# # print(int.from_bytes(readoffset(0,3,2,block_size,f),'little'))
# #f = createVolume("MyFS.dat")
# f.close()