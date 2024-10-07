# 定义全局变量（置换表和 S 盒）
P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
P8 = [6, 3, 7, 4, 8, 5, 10, 9]
IP = [2, 6, 3, 1, 4, 8, 5, 7]
IP_inv = [4, 1, 3, 5, 7, 2, 8, 6]
EP = [4, 1, 2, 3, 2, 3, 4, 1]
P4 = [2, 4, 3, 1]

SBox1 = [
    [1, 0, 3, 2],
    [3, 2, 1, 0],
    [0, 2, 1, 3],
    [3, 1, 3, 2]
]

SBox2 = [
    [0, 1, 2, 3],
    [2, 3, 1, 0],
    [3, 0, 1, 2],
    [2, 1, 0, 3]
]

def permute(bits, table):
    return [bits[i - 1] for i in table]

def left_shift(bits, n):
    return bits[n:] + bits[:n]

def key_generation(key):
    key_p10 = permute(key, P10)
    left = key_p10[:5]
    right = key_p10[5:]
    left_ls1 = left_shift(left, 1)
    right_ls1 = left_shift(right, 1)
    key_ls1 = left_ls1 + right_ls1
    K1 = permute(key_ls1, P8)
    left_ls2 = left_shift(left_ls1, 2)
    right_ls2 = left_shift(right_ls1, 2)
    key_ls2 = left_ls2 + right_ls2
    K2 = permute(key_ls2, P8)
    return K1, K2

def sbox_lookup(bits, sbox):
    row = int(f"{bits[0]}{bits[3]}", 2)
    col = int(f"{bits[1]}{bits[2]}", 2)
    value = sbox[row][col]
    return [int(b) for b in f"{value:02b}"]

def fk(bits, key):
    left = bits[:4]
    right = bits[4:]
    right_ep = permute(right, EP)
    xor_result = [r ^ k for r, k in zip(right_ep, key)]
    sbox_input_left = xor_result[:4]
    sbox_input_right = xor_result[4:]
    sbox_output_left = sbox_lookup(sbox_input_left, SBox1)
    sbox_output_right = sbox_lookup(sbox_input_right, SBox2)
    sbox_output = sbox_output_left + sbox_output_right
    sbox_output_p4 = permute(sbox_output, P4)
    left_result = [l ^ s for l, s in zip(left, sbox_output_p4)]
    return left_result + right

def encrypt(plaintext, K1, K2):
    bits = permute(plaintext, IP)
    bits = fk(bits, K1)
    bits = bits[4:] + bits[:4]
    bits = fk(bits, K2)
    ciphertext = permute(bits, IP_inv)
    return ciphertext

def is_valid_binary_string(s):
    return len(s) == 8 and all(c in '01' for c in s)

def brute_force_attack(plaintext, ciphertext):
    matching_keys = []
    for i in range(1024):
        key_candidate = [int(b) for b in f"{i:010b}"]
        K1, K2 = key_generation(key_candidate)
        enc = encrypt(plaintext, K1, K2)
        if enc == ciphertext:
            matching_keys.append(''.join(str(b) for b in key_candidate))
    return matching_keys if matching_keys else "未找到密钥"

def main():
    while True:
        plaintext_input = input("请输入8位已知明文: ")
        ciphertext_input = input("请输入8位已知密文: ")
        
        if is_valid_binary_string(plaintext_input) and is_valid_binary_string(ciphertext_input):
            plaintext = [int(bit) for bit in plaintext_input]
            ciphertext = [int(bit) for bit in ciphertext_input]
            key_found = brute_force_attack(plaintext, ciphertext)
            print(f"找到的密钥: {key_found}")
            break
        else:
            print("输入错误，请检查后重新输入")

if __name__ == "__main__":
    main()
