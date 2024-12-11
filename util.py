from __future__ import annotations

from grottdata import decrypt, encrypt


def get_record_type(raw: bytes) -> int:
    """Get the record type."""
    return raw[7]


def get_word(data: bytes, word_position: int) -> int:
    """Get word (two bytes) at specified position, as int."""
    byte_position = word_position * 2
    return int.from_bytes(data[byte_position:byte_position + 2], byteorder="big")


def get_protocol(raw: bytes) -> int:
    """Get the protocol version."""
    return get_word(raw, 1)


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
    crc16 = calc_crc(encrypted)
    return encrypted + crc16.to_bytes(2, "big")


def calc_crc(data):
    #calculate CR16, Modbus.
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for i in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc
