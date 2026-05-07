from cryptography.fernet import Fernet

# -------------------------------
# ENCRYPT
# -------------------------------
def encrypt(path, key):
    cipher = Fernet(key.encode())

    with open(path, "rb") as f:
        data = f.read()

    out = path + ".enc"

    with open(out, "wb") as f:
        f.write(cipher.encrypt(data))

    return out


# -------------------------------
# DECRYPT
# -------------------------------
def decrypt(path, key):
    cipher = Fernet(key.encode())

    with open(path, "rb") as f:
        data = f.read()

    out = path.replace(".enc", "")

    with open(out, "wb") as f:
        f.write(cipher.decrypt(data))

    return out









    