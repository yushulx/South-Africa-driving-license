# Python Decoder for Driving License in South Africa
The Python project is used to decode, decrypt and parse South African driving licenses. The PDF417 decoding part relies on [Dynamsoft Barcode Reader](https://www.dynamsoft.com/barcode-reader/overview/), which requires a [license key](https://www.dynamsoft.com/customer/license/trialLicense/?product=dcv&package=cross-platform). 

![South Africa Driving License Parser](https://camo.githubusercontent.com/fecababb27c452d4cfc669e5f0755c41ffdb7244e24d41f0096be09e65ef92bc/68747470733a2f2f7777772e64796e616d736f66742e636f6d2f636f6465706f6f6c2f696d672f323032322f31322f736f7574682d6166726963612d64726976696e672d6c6963656e73652e706e67)


## Command-line Usage
```bash 
$ sadltool [-t TYPES] [-e ENCRYPTED] [-l LICENSE] source

positional arguments:
  source                A source file containing information of driving license.

options:
  -h, --help            show this help message and exit
  -t TYPES, --types TYPES
                        Specify the source type. 1: PDF417 image 2: Base64 string 3: Raw bytes
  -e ENCRYPTED, --encrypted ENCRYPTED
                        Is the source encrypted? 0: No 1: Yes
  -l LICENSE, --license LICENSE
                        The license key is required for decoding PDF417
```

## Try Project Examples:

```bash
python test.py images/dlbase64.txt -t 2 -e 0
python test.py images/dl.raw -t 3 -e 0  
python test.py images/dl.png -l <Dynamsoft Barcode Reader License Key>
```

## Sample Code

```python
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
```

## How to Build the Package
- Source distribution:
    
    ```bash
    python setup.py sdist
    ```

- Wheel:
    
    ```bash
    pip wheel . --verbose
    # Or
    python setup.py bdist_wheel
    ```

## References
- [https://github.com/ugommirikwe/sa-license-decoder/blob/master/SPEC.md](https://github.com/ugommirikwe/sa-license-decoder/blob/master/SPEC.md)
- [https://stackoverflow.com/questions/17549231/decode-south-african-za-drivers-license](https://stackoverflow.com/questions/17549231/decode-south-african-za-drivers-license)
- [https://github.com/DanieLeeuwner/Reply.Net.SADL/blob/master/Reply.Net.SADL/Reply.Net.SADL/DriversLicenceService.cs](https://github.com/DanieLeeuwner/Reply.Net.SADL/blob/master/Reply.Net.SADL/Reply.Net.SADL/DriversLicenceService.cs)

