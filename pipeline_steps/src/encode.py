import base64

'''
This script serves as the base64 encoder for the fabric api payloads
'''

class encode:

    def __init__(self):

        print("Successfully initialized base64 encoder")

    
    def encode_str(self, txt_file):  # logic to encode a string to base64

        with open(file=txt_file, mode='r', encoding='utf-8') as file:  # read as utf8
            content = file.read() 
        
        content_bytes = content.encode('utf-8')  # encode as utf8
        base64_bytes = base64.b64encode(content_bytes)  # encode to base64

        return base64_bytes

    
    def encode_bin(self, bin_file):  # logic to encode a binary file to base64

        with open(bin_file, 'rb') as file:  # read as binary
            content = file.read()
        
        base64_bytes = base64.b64encode(content)  # encode to base64

        return base64_bytes