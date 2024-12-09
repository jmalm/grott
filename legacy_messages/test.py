import messages


command_buffer = b'\x00\x01\x00\x06\x000\x01\x10\x00"(G"9Aw\'\\wattGrowattGrowattGroZaFt_rdwztxGUo}/J'


def test_serialize():
    m = messages.deserialize(command_buffer)
    assert m.serialize() == command_buffer
