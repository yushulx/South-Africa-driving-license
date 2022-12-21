import argparse
from sadl import *
import sys
import os

def sadltool():
    
    parser = argparse.ArgumentParser(description='Decode, decrypt and parse South Africa driving license.')
    parser.add_argument('source', help='A source file containing information of driving license.')
    parser.add_argument('-t', '--types', default=1, type=int, help='Specify the source type. 1: PDF417 image 2: Base64 string 3: Raw bytes')
    parser.add_argument('-e', '--encrypted', default=1, type=int, help='Is the source encrypted? 0: No 1: Yes')
    parser.add_argument('-l', '--license', default='', type=str, help='The license key is required for decoding PDF417')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    try:
        args = parser.parse_args()
        source = args.source
        types = args.types
        if args.encrypted == 1:
            encrypted = True
        else:
            encrypted = False
        license = args.license
        
        if not os.path.exists(source):
            print('Source not found')
            exit(-1)
            
        if types == 1:
            dl = parse_file(source, encrypted, license)
            print(dl)
        elif types == 2:
            with open(source, 'r') as f:
                source = f.read()
                dl = parse_base64(source, encrypted)
                print(dl)
        elif types == 3:
            data = Path(source).read_bytes()
            dl = parse_bytes(data, encrypted)
            print(dl)
            
    except Exception as err:
        print(err)
        sys.exit(1)
        
sadltool()