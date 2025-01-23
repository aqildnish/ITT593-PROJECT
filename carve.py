import os

def carve_jpeg(disk_image_path, output_dir):
    """
    Carves JPEG images from a disk image.

    Args:
        disk_image_path (str): The path to the disk image file.
        output_dir (str): The directory to save the recovered files.
    """

    # JPEG signature (magic number)
    jpeg_signature = b'\xff\xd8\xff\xe0'  

    with open(disk_image_path, 'rb') as disk_image:
        data = disk_image.read()
        offset = 0

        while True:
            # Find the next occurrence of the JPEG signature
            index = data.find(jpeg_signature, offset)
            if index == -1:  # No more JPEGs found
                break

            # Extract the potential JPEG data (you might need to refine this)
            file_data = data[index:index+1024]  # Extract a chunk of data

            # Save the extracted data to a file
            filename = os.path.join(output_dir, f"recovered_jpeg_{offset}.jpg")
            with open(filename, 'wb') as f:
                f.write(file_data)

            offset = index + 1  # Move to the next position in the data