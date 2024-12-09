from grottdata import decrypt, encrypt
import libscrc_fake as libscrc


def get_word(decrypted: bytes, word_position: int):
    byte_position = word_position * 2
    return int.from_bytes(decrypted[byte_position:byte_position + 2], byteorder="big")


def get_protocol(raw: bytes) -> int:
    """Get the protocol version."""
    return get_word(raw, 1)


def get_record_type(raw: bytes) -> int:
    """Get the record type."""
    return raw[7]


def get_decrypted(raw: bytes) -> bytes:
    """Get decrypted message (if encrypted)."""
    if get_protocol(raw) == 2:  # Protocol 2 is not encrypted
        return raw
    return decrypt(raw, return_bytes=True)[:-2]  # Decrypt, and strip crc


def get_encrypted(data: bytes) -> bytes:
    """Encrypt the message if the protocol demands it."""
    if get_protocol(data) == 2:  # Protocol 2 is not encrypted
        return data
    encrypted = encrypt(data, return_bytes=True)
    crc16 = libscrc.modbus(encrypted)
    return encrypted + crc16.to_bytes(2, "big")