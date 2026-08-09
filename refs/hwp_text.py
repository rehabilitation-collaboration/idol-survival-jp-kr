"""HWP 5.x の BodyText からテキストを抽出する最小実装。

HWPTAG_PARA_TEXT (tag id 67) のレコードを拾い、UTF-16LE として復号する。
制御文字 (0x00-0x1F) は HWP の inline control record なので除去する。
"""
import sys
import zlib
import struct
import olefile

HWPTAG_PARA_TEXT = 0x43  # 67


def records(buf):
    pos = 0
    n = len(buf)
    while pos + 4 <= n:
        (header,) = struct.unpack_from("<I", buf, pos)
        pos += 4
        tag = header & 0x3FF
        size = (header >> 20) & 0xFFF
        if size == 0xFFF:
            (size,) = struct.unpack_from("<I", buf, pos)
            pos += 4
        yield tag, buf[pos:pos + size]
        pos += size


def decode_para(data):
    out = []
    i = 0
    while i + 2 <= len(data):
        (code,) = struct.unpack_from("<H", data, i)
        if code < 32:
            # inline/extended control: 확장(1,2,3,11..12...) は 16바이트 소비
            if code in (1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23):
                i += 16
            else:
                i += 2
            out.append("\n" if code in (10, 13) else "")
            continue
        out.append(chr(code))
        i += 2
    return "".join(out)


def main(path):
    ole = olefile.OleFileIO(path)
    header = ole.openstream("FileHeader").read()
    compressed = bool(header[36] & 0x01)
    names = ["/".join(s) for s in ole.listdir()]
    sections = sorted(n for n in names if n.startswith("BodyText/Section"))
    chunks = []
    for name in sections:
        raw = ole.openstream(name).read()
        if compressed:
            raw = zlib.decompress(raw, -15)
        for tag, data in records(raw):
            if tag == HWPTAG_PARA_TEXT:
                chunks.append(decode_para(data))
    text = "\n".join(chunks)
    sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))


if __name__ == "__main__":
    main(sys.argv[1])
