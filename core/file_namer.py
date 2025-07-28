class FileNamer:
    """
    Class for managing and generating formatted file names.

    This class allows setting the base name, prefix, and version for a file,
    and provides a method to generate a full file name with a specific index.
    It is useful for maintaining a structured naming convention for different
    files in various contexts.

    :ivar file_name: Base name of the file.
    :type file_name: str
    :ivar prefix: Prefix to be added to the file name.
    :type prefix: str
    :ivar pic_vers: Version of the file, used for versioning the name.
    :type pic_vers: str
    """
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