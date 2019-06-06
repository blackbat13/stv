class FileTools:
    @staticmethod
    def save_to_file(file_name: str, content: str) -> None:
        f = open(f"{file_name}.ispl", "w")
        f.write(content)
        f.close()
