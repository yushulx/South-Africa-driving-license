# https://github.com/ugommirikwe/sa-license-decoder/blob/master/SPEC.md

import base64
import rsa
from pathlib import Path
from dbr import *

__version__ = '0.1.1'

v1 = [0x01, 0xe1, 0x02, 0x45]
v2 = [0x01, 0x9b, 0x09, 0x45]

pk_v1_128 = '''
-----BEGIN RSA PUBLIC KEY-----
MIGXAoGBAP7S4cJ+M2MxbncxenpSxUmBOVGGvkl0dgxyUY1j4FRKSNCIszLFsMNwx2XWXZg8H53gpCsxDMwHrncL0rYdak3M6sdXaJvcv2CEePrzEvYIfMSWw3Ys9cRlHK7No0mfrn7bfrQOPhjrMEFw6R7VsVaqzm9DLW7KbMNYUd6MZ49nAhEAu3l//ex/nkLJ1vebE3BZ2w==
-----END RSA PUBLIC KEY-----
'''

pk_v1_74 = '''
-----BEGIN RSA PUBLIC KEY-----
MGACSwD/POxrX0Djw2YUUbn8+u866wbcIynA5vTczJJ5cmcWzhW74F7tLFcRvPj1tsj3J221xDv6owQNwBqxS5xNFvccDOXqlT8MdUxrFwIRANsFuoItmswz+rfY9Cf5zmU=
-----END RSA PUBLIC KEY-----
'''

pk_v2_128 = '''
-----BEGIN RSA PUBLIC KEY-----
MIGWAoGBAMqfGO9sPz+kxaRh/qVKsZQGul7NdG1gonSS3KPXTjtcHTFfexA4MkGAmwKeu9XeTRFgMMxX99WmyaFvNzuxSlCFI/foCkx0TZCFZjpKFHLXryxWrkG1Bl9++gKTvTJ4rWk1RvnxYhm3n/Rxo2NoJM/822Oo7YBZ5rmk8NuJU4HLAhAYcJLaZFTOsYU+aRX4RmoF
-----END RSA PUBLIC KEY-----
'''

pk_v2_74 = '''
-----BEGIN RSA PUBLIC KEY-----
MF8CSwC0BKDfEdHKz/GhoEjU1XP5U6YsWD10klknVhpteh4rFAQlJq9wtVBUc5DqbsdI0w/bga20kODDahmGtASy9fae9dobZj5ZUJEw5wIQMJz+2XGf4qXiDJu0R2U4Kw==
-----END RSA PUBLIC KEY-----
'''


def decode_pdf417(image_file, license_key=''):
    """Decode PDF417 code from image

    Args:
        image_file (str): Image file path
        
    Returns: 
        bytes: raw data
    """
    key = "DLS2eyJoYW5kc2hha2VDb2RlIjoiMjAwMDAxLTE2NDk4Mjk3OTI2MzUiLCJvcmdhbml6YXRpb25JRCI6IjIwMDAwMSIsInNlc3Npb25QYXNzd29yZCI6IndTcGR6Vm05WDJrcEQ5YUoifQ=="
    if (license_key != ''):
        key = license_key
    BarcodeReader.init_license(key)
    reader = BarcodeReader()
    results = reader.decode_file(image_file)
    if results != None and len(results) > 0:
        return results[0].barcode_bytes
    else:
        return None
    
def decrypt_data(data):
    """Decrypt data

    Args:
        data (bytes): Raw data
        
    Returns: 
        bytes: decrypted data
    """
    
    header = data[0: 6]
    pk128 = pk_v1_128
    pk74 = pk_v1_74
    
    if header[0] == v1[0] and header[1] == v1[1] and header[2] == v1[2] and header[3] == v1[3]:
        pk128 = pk_v1_128
        pk74 = pk_v1_74
    elif header[0] == v2[0] and header[1] == v2[1] and header[2] == v2[2] and header[3] == v2[3]:
        pk128 = pk_v2_128
        pk74 = pk_v2_74
    
    all = bytearray()
    
    pubKey = rsa.PublicKey.load_pkcs1(pk128)
    start = 6
    for i in range(5):
        block = data[start: start + 128]
        input = int.from_bytes(block, byteorder='big', signed=False)
        output = pow(input, pubKey.e, mod=pubKey.n)
        
        decrypted_bytes = output.to_bytes(128, byteorder='big', signed=False)
        all += decrypted_bytes
        
        start = start + 128
    
    pubKey = rsa.PublicKey.load_pkcs1(pk74)
    block = data[start: start + 74]
    input = int.from_bytes(block, byteorder='big', signed=False)
    output = pow(input, pubKey.e, mod=pubKey.n)
    
    decrypted_bytes = output.to_bytes(74, byteorder='big', signed=False)
    all += decrypted_bytes
    
    return all

def readNibbleDateString(nibbleQueue):
    m = nibbleQueue.pop(0)
    if m == 10:
        return ''
    
    c = nibbleQueue.pop(0)
    d = nibbleQueue.pop(0)
    y = nibbleQueue.pop(0)

    m1 = nibbleQueue.pop(0)
    m2 = nibbleQueue.pop(0)

    d1 = nibbleQueue.pop(0)
    d2 = nibbleQueue.pop(0)
    
    return f'{m}{c}{d}{y}/{m1}{m2}/{d1}{d2}'
    
def readNibbleDateList(nibbleQueue, length):
    dateList = []
    
    for i in range(length):
        dateString = readNibbleDateString(nibbleQueue)
        if dateString != '':
            dateList.append(dateString)
            
    return dateList

def readStrings(data, index, length):
    strings = []
    
    i = 0
    while i < length:
        value = ''
        while True:
            currentByte = data[index]
            index += 1
            
            if currentByte == 0xe0:
                break
            elif currentByte == 0xe1:
                if value != '':
                    i += 1
                break
            
            value += chr(currentByte)
            
        i += 1
        
        if value != '':
            strings.append(value)
            
    return strings, index

def readString(data, index):
    value = ''
    delimiter = 0xe0

    while True:
        currentByte = data[index]
        index += 1
        
        if currentByte == 0xe0 or currentByte == 0xe1:
            delimiter = currentByte
            break

        value += chr(currentByte)
        
    return value, index, delimiter
 
def parse_data(data):
    """Parse data

    Args:
        data (bytes): decrypted data
        
    Returns: 
        Driving license object
    """
    
    index = 0
    for i in range(0, len(data)):
        if data[i] == 0x82:
            index = i
            break
   
    # Section 1: Strings
    vehicleCodes, index = readStrings(data, index + 2, 4)
    # print(f'Vehicle codes: {vehicleCodes}')
    
    surname, index, delimiter = readString(data, index)
    # print(f'Surname: {surname}')
    
    initials, index, delimiter = readString(data, index)
    # print(f'Initials: {initials}')
    
    PrDPCode = ''
    if delimiter == 0xe0:
        PrDPCode, index, delimiter = readString(data, index)
        # print(f'PrDP Code: {PrDPCode}')
    
    idCountryOfIssue, index, delimiter = readString(data, index)
    # print(f'ID Country of Issue: {idCountryOfIssue}')
    
    licenseCountryOfIssue, index, delimiter = readString(data, index)
    # print(f'License Country of Issue: {licenseCountryOfIssue}')
    
    vehicleRestrictions, index = readStrings(data, index, 4)
    # print(f'Vehicle Restriction: {vehicleRestrictions}')
    
    licenseNumber, index, delimiter = readString(data, index)
    # print(f'License Number: {licenseNumber}')
    
    idNumber = ''
    for i in range(13):
        idNumber += chr(data[index])
        index += 1
    # print(f'ID Number: {idNumber}')
    
    # Section 2: Binary Data
    idNumberType = f'{data[index]:02d}'
    index += 1
    # print(f'ID number type: {idNumberType}') # 02 means South African ID
    
    nibbleQueue = []
    while True:
        currentByte = data[index]
        index += 1
        if currentByte == 0x57:
            break

        nibbles = [currentByte >> 4, currentByte & 0x0f]
        
        nibbleQueue += nibbles
        
    licenseCodeIssueDates = readNibbleDateList(nibbleQueue, 4)
    # print(f'License code issue date: {licenseCodeIssueDates}') # 4x License code issue date. Each date either 8 nibbleQueue, or a single a nibble.
    
    driverRestrictionCodes = f'{nibbleQueue.pop(0)}{nibbleQueue.pop(0)}'
    # print(f'Driver restriction codes: {driverRestrictionCodes}') # A combination of (0-2), (0-2). 0 = none, 1 = glasses, 2 = artificial limb
    
    PrDPermitExpiryDate = readNibbleDateString(nibbleQueue)
    # print(f'PrDP permit expiry date: {PrDPermitExpiryDate}')
    
    licenseIssueNumber = f'{nibbleQueue.pop(0)}{nibbleQueue.pop(0)}'
    # print(f'License issue number: {licenseIssueNumber}')
    
    birthdate = readNibbleDateString(nibbleQueue)
    # print(f'Birthdate: {birthdate}')
    
    licenseIssueDate = readNibbleDateString(nibbleQueue)
    # print(f'License Valid From: {licenseIssueDate}')
    
    licenseExpiryDate = readNibbleDateString(nibbleQueue)
    # print(f'License Valid To: {licenseExpiryDate}')
    
    # 01 = male, 02 = female
    gender = f'{nibbleQueue.pop(0)}{nibbleQueue.pop(0)}'
    if  gender == '01':
        gender = 'male'
        # print('Gender: male')
    else:
        gender = 'female'
        # print('Gender: female')
    
    # Section 3: Image Data
    # image info
    index += 3
    width = data[index]
    index += 2
    # print(f'Image width: {width}')
    
    height = data[index]
    index += 1
    # print(f'Image height: {height}')
    
    return DrivingLicense(vehicleCodes, surname, initials, PrDPCode, idCountryOfIssue, licenseCountryOfIssue, vehicleRestrictions, licenseNumber, idNumber, idNumberType, licenseCodeIssueDates, driverRestrictionCodes, PrDPermitExpiryDate, licenseIssueNumber, birthdate, licenseIssueDate, licenseExpiryDate, gender, width, height)
    
class DrivingLicense:    
    def __init__(self, vehicleCodes, surname, initials, PrDPCode, idCountryOfIssue, licenseCountryOfIssue, vehicleRestrictions, licenseNumber, idNumber, idNumberType, licenseCodeIssueDates, driverRestrictionCodes, PrDPermitExpiryDate, licenseIssueNumber, birthdate, licenseIssueDate, licenseExpiryDate, gender, width, height):
        self.vehicleCodes = vehicleCodes
        self.surname = surname
        self.initials = initials
        self.PrDPCode = PrDPCode
        self.idCountryOfIssue = idCountryOfIssue
        self.licenseCountryOfIssue = licenseCountryOfIssue
        self.vehicleRestrictions = vehicleRestrictions
        self.licenseNumber = licenseNumber
        self.idNumber = idNumber
        self.idNumberType = idNumberType
        self.licenseCodeIssueDates = licenseCodeIssueDates
        self.driverRestrictionCodes = driverRestrictionCodes
        self.PrDPermitExpiryDate = PrDPermitExpiryDate
        self.licenseIssueNumber = licenseIssueNumber
        self.birthdate = birthdate
        self.licenseIssueDate = licenseIssueDate
        self.licenseExpiryDate = licenseExpiryDate
        self.gender = gender
        self.image_width = width
        self.image_height = height
        
    def __str__(self) -> str:
        return f'Vehicle codes: {self.vehicleCodes} \nSurname: {self.surname} \nInitials: {self.initials} \nPrDP Code: {self.PrDPCode} \nID Country of Issue: {self.idCountryOfIssue} \nLicense Country of Issue: {self.licenseCountryOfIssue} \nVehicle Restriction: {self.vehicleRestrictions} \nLicense Number: {self.licenseNumber} \nID Number: {self.idNumber} \nID number type: {self.idNumberType} \nLicense code issue date: {self.licenseCodeIssueDates} \nDriver restriction codes: {self.driverRestrictionCodes} \nPrDP permit expiry date: {self.PrDPermitExpiryDate} \nLicense issue number: {self.licenseIssueNumber} \nBirthdate: {self.birthdate} \nLicense Valid From: {self.licenseIssueDate} \nLicense Valid To: {self.licenseExpiryDate} \nGender: {self.gender}\nImage width: {self.image_width}\nImage height: {self.image_height}'
    
        
def parse_base64(base64_string, encrypted=False):
    """Parse base64 string

    Args:
        base64_string (str): base64 string
        encrypted (bool): is the base64 string encrypted
        
    Returns: 
        Driving license object
    """
    data = base64.b64decode(base64_string)
    if len(data) != 720 and encrypted == True:
        return None
    
    if encrypted:
        data = decrypt_data(data)
    return parse_data(data)

def parse_bytes(bytes, encrypted=False):
    """Parse bytes

    Args:
        bytes (bytes): bytes
        encrypted (bool): is the bytes encrypted
        
    Returns: 
        Driving license object
    """
    data = bytes
    if len(data) != 720 and encrypted == True:
        return None
    
    if encrypted:
        # print(len(bytes))
        data = decrypt_data(bytes)
    return parse_data(data)

def parse_file(filename, encrypted=True, license=''):
    """Parse file

    Args:
        filename (str): filename
        encrypted (bool): is PDF417 content encrypted
        
    Returns: 
        Driving license object
    """
    
    data = decode_pdf417(filename, license)
    if data == None or len(data) != 720:
        return None
    
    return parse_bytes(data, encrypted)
