import io
import random
from PIL import Image, UnidentifiedImageError
import pathlib
import argparse
import os
from getpass import getpass
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
#done
def main():
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt a image"
    )
    sub_parsers = parser.add_subparsers()
    encrypt_parser = sub_parsers.add_parser(
        "encrypt", help="Encrypt a image"
    )
    encrypt_parser.add_argument(
        "path", type=pathlib.Path, help="Path to image to encrypt"
    )
    encrypt_parser.set_defaults(func=encrypt)
    decrypt_parser = sub_parsers.add_parser(
        "decrypt", help="Decrypt a image"
    )
    decrypt_parser.add_argument(
        "path", type=pathlib.Path, help="Path to image to decrypt"
    )
    decrypt_parser.set_defaults(func=decrypt)
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    while True:
        if args.path.exists():
            if args.func == encrypt:
                try:
                    img = Image.open(args.path)
                    img.verify()
                except UnidentifiedImageError:
                    print("Not an image")
                    return
            break
        else:
            print(f"Path '{args.path}' does not exist. Please provide a valid path.")
            args.path = pathlib.Path(input("Enter path: "))

    if args.func == encrypt:
        while True:
            password = getpass("Enter password: ")
            validate_password = getpass("Confirm password: ")
            if password == validate_password:
                break
            else:
                print("Passwords did not match. Please try again")
    elif args.func == decrypt:
        password = getpass("Enter password: ")
    args.func(args.path, password)

def encrypt(path, password):
    with open(path, "rb") as file:
        magic = file.read(6)
        if magic == b"ENCIMG":
            print("Is an encrypted file!")
            return
    img = Image.open(path)
    salt = os.urandom(32)
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(password.encode())
    img_size = img.size
    num_pixel = img_size[0] * img_size[1]
    random.seed(key)
    for pixel in range(num_pixel):
        shift = random.randint(0,255)
        r,g,b = img.getpixel((pixel % img_size[0], pixel // img_size[0]))
        img.putpixel((pixel % img_size[0],pixel//img_size[0]),
                     ((r + shift) % 256, (g + shift) % 256, (b + shift) % 256))
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    with open (path.with_suffix(".png"), "wb") as file:
        file.write(b"ENCIMG")
        file.write(salt)
        file.write(img_bytes)
    path.unlink()

def decrypt(path, password):
    output_path = path.with_stem(path.stem + "_decrypt")
    if output_path.exists():
        print(f"File '{output_path}' already exists. Skipping decryption")
        return
    with open(path, "rb") as file:
        magic = file.read(6)
        if magic != b"ENCIMG":
            print("Not an encrypted file!")
            return
        salt = file.read(32)
        img_byts = file.read()
    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1)
    key = kdf.derive(password.encode())
    random.seed(key)
    buffer = io.BytesIO(img_byts)
    img = Image.open(buffer)
    img_size = img.size
    num_pixel = img.size[0] * img_size[1]
    for pixel in range(num_pixel):
        shift = random.randint(0,255)
        r,g,b = img.getpixel((pixel % img_size[0], pixel // img_size[0]))
        img.putpixel((pixel % img_size[0],pixel//img_size[0]),
                     ((r - shift +256) % 256, (g - shift + 256)%256,
                     (b - shift + 256 ) % 256))

    img.save(output_path, format="PNG")
    path.unlink()
    final_path = output_path.with_stem(output_path.stem.removesuffix("_decrypt"))
    output_path.rename(final_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted.")