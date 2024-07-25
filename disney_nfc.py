def write_nfc(tag_data, data, sector, block):
    tag_data[(block*16+sector*4*16):(block*8+sector*4*16)+16]=data
    return tag_data

def read_nfc(data, sector, block):
    return data[(block*16+sector*4*16):(block*16+sector*4*16)+16]