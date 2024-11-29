import chardet

def detect_file_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    confidence = result['confidence']
    print(f"Detected encoding: {encoding} with confidence {confidence}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python detect_encoding.py <file_path>")
        sys.exit(1)
    file_path = sys.argv[1]
    detect_file_encoding(file_path)
