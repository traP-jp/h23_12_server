def convert_image_to_binary(file_name):
    with open(file_name, 'rb') as file:
        binary_data = file.read()
    return binary_data
