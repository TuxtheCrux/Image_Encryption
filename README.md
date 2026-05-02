# 🔐 Image Encryptor

A command-line tool to encrypt and decrypt image files using password-based pixel manipulation.

## How it works

Each pixel's RGB values are shifted by a pseudo-random value derived from your password. The random sequence is seeded with a key generated via **Scrypt**, a memory-hard key derivation function. Without the correct password, the pixel shifts cannot be reproduced and the image cannot be recovered.

Encrypted files are stored as PNG with a custom binary header:

```
[ ENCIMG (6B) ][ Salt (32B) ][ PNG image data ]
```

## Installation

```bash
pip install pillow cryptography
```

## Usage

```bash
# Encrypt an image
python encryptor.py encrypt path/to/image.jpg

# Decrypt an image
python encryptor.py decrypt path/to/image.png
```

You will be prompted to enter (and confirm) a password interactively. The original file is deleted after a successful operation.

## Security notes

| Property | Detail |
|---|---|
| KDF | Scrypt (`n=2^14, r=8, p=1`) |
| Salt | 32 random bytes per file |
| PRNG | Python `random` (not cryptographically secure) |
| Integrity | No — a wrong password produces a corrupted image silently |

> ⚠️ This project is for educational purposes. The use of Python's `random` module makes it unsuitable for protecting sensitive data. Consider AES-based encryption for real-world use.

## Requirements

- Python 3.8+
- [Pillow](https://python-pillow.org/)
- [cryptography](https://cryptography.io/)
