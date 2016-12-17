import mmap


class CommPCIeLinux:
    def __init__(self, bar, bar_size, debug=False):
        self.bar = bar
        self.bar_size = bar_size
        self.debug = debug

    def open(self):
        if hasattr(self, "sysfs"):
            return
        self.sysfs = open(self.bar, "r+b")
        self.sysfs.flush()
        self.mmap = mmap.mmap(self.sysfs.fileno(), self.bar_size)

    def close(self):
        if not hasattr(self, "sysfs"):
            return
        self.mmap.close()
        del self.mmap
        self.sysfs.close()
        del self.sysfs

    def read(self, addr, length=None):
        data = []
        length_int = 1 if length is None else length
        for i in range(length_int):
            self.mmap.seek(addr + 4*i)
            value = int.from_bytes(self.mmap.read(4), "big")
            if self.debug:
                print("RD {:08X} @ {:08X}".format(data, addr + 4*i))
            if length is None:
                return value
            data.append(value)
        return data

    def write(self, addr, data):
        data = data if isinstance(data, list) else [data]
        length = len(data)
        for i, value in enumerate(data):
            self.mmap[addr + 4*i:addr + 4*(i + 1)] = value.to_bytes(4, byteorder="big")
            if self.debug:
                print("WR {:08X} @ {:08X}".format(value, 4*(addr + i)))
