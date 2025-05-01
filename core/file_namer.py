class FileNamer:
    def __init__(self):
        self.file_name = ""
        self.prefix = ""
        self.pic_vers = ""

    def set_name(self, file_name, prefix, pic_vers):
        self.file_name = file_name
        self.prefix = prefix
        self.pic_vers = pic_vers

    def generate_file_name(self, index):
        return f"{self.file_name}_v{self.pic_vers}.{index}_{self.prefix}.jpg"