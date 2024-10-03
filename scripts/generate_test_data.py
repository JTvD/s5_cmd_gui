import os


def generate_files(num_files, file_size, directory):
    # Ensure the directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate files
    for i in range(int(num_files/2)):
        file_name = f"file_{i}.txt"
        file_path = os.path.join(directory, file_name)

        # 'wb' mode is used to write in binary format, which allows for precise control over file size
        with open(file_path, 'wb') as f:
            f.write(b'0' * file_size)


if __name__ == "__main__":
    # Directory to store the files
    directory = "C:/Users/tim/Downloads/temp1"

    # Number of files
    num_files = 100000
    # File size in bytes (500 KB)
    file_size = 500 * 1024

    generate_files(num_files, file_size, directory)
    #generate_files(num_files, file_size, "C:/temper/temp2")
