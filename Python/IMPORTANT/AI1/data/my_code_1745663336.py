class FileOpener:
    def __init__(self, filename):
        self.filename = filename
    
    def __enter__(self):
        self.file = open(self.filename, 'r')
        return self.file
    
    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.close()
        if exc_type:
            print(f"An error occurred: {exc_value}")
        return True  # suppress exception

with FileOpener('sample.txt') as f:
    content = f.read()
    print(content)