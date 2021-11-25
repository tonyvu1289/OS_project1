from os import fdopen
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
def createVolume(volume_name):
    f = open(volume_name,'w+b')
    createNullFile_cluster(2,f)
    header_list = []
    block_size = 512
    clusersize_sector = 8
    header_list.append(block_size.to_bytes(2,'little'))
    header_list.append(clusersize_sector.to_bytes(1,'little'))
    writeblock(b''.join(header_list),0,block_size,f)
    return f
# f = open("MyFS.dat","r+b")
# block_size = 512
# createNullFile_cluster(2,f)
# int_val = 512
# byte_val = int_val.to_bytes(2,'little')
# #writeblock(byte_val,0,block_size,f)
# #writeoffset(byte_val,3,0,block_size,f)
# print(int.from_bytes(readoffset(0,3,2,block_size,f),'little'))
f = createVolume("MyFS.dat")
f.close()