"""A5/1 chuẩn (64-bit key, thanh ghi 19-22-23)."""


class StandardA51:
    LEN = (19, 22, 23)                       # độ dài X, Y, Z
    CLK = (9, 11, 11)                        # bit quay x9, y11, z11
    TAPS = ((14, 17, 18, 19), (21, 22), (8, 21, 22, 23))

    def __init__(self, key_64bits: str, frame: int = 0):
        if len(key_64bits) != 64 or not set(key_64bits) <= {"0", "1"}:
            raise ValueError("Khóa phải gồm đúng 64 ký tự '0'/'1'.")
        if not 0 <= frame < 2**22:
            raise ValueError("Frame number phải nằm trong [0, 2^22).")

        # Mảng 1-indexed: phần tử 0 là đệm
        self.R = [[0] * (n + 1) for n in self.LEN]

        for b in key_64bits:                 # 64 nhịp nạp khóa
            self._load_clock(int(b))
        for i in range(22):                  # 22 nhịp nạp frame (LSB trước)
            self._load_clock((frame >> i) & 1)
        for _ in range(100):                 # 100 nhịp khởi động, bỏ đầu ra
            self._majority_clock()

    def _shift(self, k: int, in_bit: int = 0) -> None:
        r = self.R[k]
        t = in_bit
        for p in self.TAPS[k]:
            t ^= r[p]
        r[:] = [0, t] + r[1:self.LEN[k]]     # dịch i -> i+1, t vào vị trí 1

    def _load_clock(self, bit: int) -> None:
        for k in range(3):
            self._shift(k, bit)

    def _majority_clock(self) -> None:
        bits = [self.R[k][self.CLK[k]] for k in range(3)]
        m = 1 if sum(bits) >= 2 else 0
        for k in range(3):
            if bits[k] == m:
                self._shift(k)

    def next_bit(self) -> int:
        self._majority_clock()
        return self.R[0][19] ^ self.R[1][22] ^ self.R[2][23]


def crypt_bits(bits: str, key: str, frame: int = 0) -> str:
    """Mã hóa = giải mã (XOR với keystream)."""
    c = StandardA51(key, frame)
    return "".join(str(int(b) ^ c.next_bit()) for b in bits)


def text_to_bits(text: str) -> str:
    return "".join(f"{b:08b}" for b in text.encode("utf-8"))


def bits_to_text(bits: str) -> str:
    data = bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))
    return data.decode("utf-8", errors="replace")


def encrypt_text(plaintext: str, key: str, frame: int = 0) -> str:
    return crypt_bits(text_to_bits(plaintext), key, frame)


def decrypt_text(cipher_bits: str, key: str, frame: int = 0) -> str:
    return bits_to_text(crypt_bits(cipher_bits, key, frame))


if __name__ == "__main__":
    key = "1101010100111010011000110101010011101001100011010101001110100110"
    msg = "Xin chao! Day la A5/1 chuan."

    c1 = encrypt_text(msg, key, frame=1)
    c2 = encrypt_text(msg, key, frame=2)
    assert decrypt_text(c1, key, frame=1) == msg   # khứ hồi
    assert c1 != c2                                # frame khác -> keystream khác
    print("OK")
