import sys

import rich_click as click

from grottdata import decrypt
from messages import from_datalogger, to_datalogger, Message
from util import get_decrypted, get_record_type


@click.command()
@click.argument("message_file", nargs=-1, type=str, required=True)
@click.option("--verbose", is_flag=True)
@click.option("--include-datalogger", is_flag=True, help="Include datalogger messages. They are not included by default because they are encoded differently.")
@click.option("--fail-on-error", is_flag=True, help="Fail on error.")
def main_click(message_file: str, verbose: bool, include_datalogger: bool, fail_on_error: bool):
    for p in message_file:
        do(p, verbose, include_datalogger, fail_on_error)


def clean_classes(message_classes: list[type[Message]], include_datalogger: bool) -> \
        tuple[list[type[Message]], list[type[Message]]]:
    if include_datalogger:
        return message_classes, []
    return ([cls for cls in message_classes if "Datalogger" not in cls.__name__],
            [cls for cls in message_classes if "Datalogger" in cls.__name__])



def do(message_file: str, verbose: bool = False, include_datalogger: bool = False, fail_on_error: bool = True):
    print(f"\n=== {message_file} ===")
    if "192.168.0" in message_file:
        message_classes, ignored_classes = clean_classes(from_datalogger, include_datalogger)
        print(f"Using message classes from datalogger: {message_classes}") if verbose else None
    else:
        message_classes, ignored_classes = clean_classes(to_datalogger, include_datalogger)
        print(f"Using message classes from server: {message_classes}") if verbose else None
    ignored_record_types = [cls.record_type for cls in ignored_classes]
    with open(message_file, "rb") as f:
        raw = f.read()
    data = get_decrypted(raw)
    try:
        message = deserialize(data, message_classes)
        if message.record_type in ignored_record_types:
            return
    except Exception as e:
        print(f"Could not deserialize message in {message_file} using {message_classes}: {e}")
        print(f"Raw: {raw}") if verbose else None
        message = Message(data=data)
        print(f"Message: {message}")
        print(f"Data: {data}")
        if fail_on_error:
            raise e
        return
    print(f"Message: {message}")
    decrypted = decrypt(raw, return_bytes=True)[:-2] if message.protocol != 2 else raw
    print(f"Decrypted:    {decrypted}")
    print(f"message.data: {message.serialize()}") if verbose else None
    print(message.serialize().hex()) if verbose else None


def deserialize(data: bytes, message_classes: list[type(Message)] = None) -> Message:
    """Returns a message and the remaining bytes in the buffer."""
    if message_classes is None:
        message_classes = to_datalogger + from_datalogger
    record_type = get_record_type(data)
    for cls in message_classes:
        if record_type == cls.record_type:
            return cls(data=data)
    return Message(data=data)


def main():
    for message_file in sys.argv[1:]:
        do(message_file)


if __name__ == '__main__':
    main_click()
