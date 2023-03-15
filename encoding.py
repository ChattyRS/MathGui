def message_to_ascii_hexadecimal(plaintext: str) -> str:
    '''
    Encodes a plaintext message string to hexadecimal ASCII.
    '''
    if not plaintext.isascii():
        raise ValueError('Message was not valid ASCII')
    return ' '.join([hex(ord(char)).replace('0x', '') for char in plaintext])

def message_to_ascii_decimal(plaintext: str) -> int:
    '''
    Encodes a plaintext message string to hexadecimal ASCII, and then converts it to decimal.
    '''
    if not plaintext.isascii():
        raise ValueError('Message was not valid ASCII')
    return ' '.join([str(ord(char)) for char in plaintext])