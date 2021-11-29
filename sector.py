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
