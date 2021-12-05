def hashString_4byte(str):
    res = 0
    for char in str:
        res+= ord(char) % 4294967296 #maxvalue
    return res.to_bytes(4,'little')
print(int.from_bytes(hashString_4byte(""),'little'))