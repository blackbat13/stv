class FileTools:
    @staticmethod
    def save_to_file(file_name: str, content: str, extension:str="ispl") -> str:
        file_name = FileTools.add_extension(file_name, extension)
        f = open(f"{file_name}", "w")
        f.write(content)
        f.close()
        return file_name

    @staticmethod
    def add_extension(file_name:str, extension:str) -> str:
        if file_name.endswith("." + extension):
            return file_name
        else:
            return file_name + "." + extension
