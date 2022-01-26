import base64


def decoding(text):
    text_parts = text.split('?')
    base64_bytes = text_parts[3].encode(text_parts[1])
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode(text_parts[1])
