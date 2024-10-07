# -*- coding: utf-8 -*-
# 输入明文遍历所有密钥，找到相同的密文并输出。
import time
# 定义全局变量（置换表和 S 盒）
P10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
P8 = [6, 3, 7, 4, 8, 5, 10, 9]
IP = [2, 6, 3, 1, 4, 8, 5, 7]
IP_inv = [4, 1, 3, 5, 7, 2, 8, 6]
EP = [4, 1, 2, 3, 2, 3, 4, 1]
P4 = [2, 4, 3, 1]

SBox1 = [
    [1, 0, 3, 2],  # 行 0
    [3, 2, 1, 0],  # 行 1
    [0, 2, 1, 3],  # 行 2
    [3, 1, 0, 2]   # 行 3
]

SBox2 = [
    [0, 1, 2, 3],  # 行 0
    [2, 3, 1, 0],  # 行 1
    [3, 0, 1, 2],  # 行 2
    [2, 1, 0, 3]   # 行 3
]

def permute(bits, table):
    """
    根据置换表对位序列进行置换

    参数：
        bits (list): 输入位序列
        table (list): 置换表

    返回：
        list: 置换后的位序列
    """
    return [bits[i - 1] for i in table]

def left_shift(bits, n):
    """
    对位序列进行循环左移

    参数：
        bits (list): 输入位序列
        n (int): 左移位数

    返回：
        list: 左移后的位序列
    """
    return bits[n:] + bits[:n]

def key_generation(key):
    """
    从 10 位密钥生成两个子密钥 K1 和 K2

    参数：
        key (list): 10 位密钥

    返回：
        tuple: K1 和 K2
    """
    # 1. P10 置换
    key_p10 = permute(key, P10)
    # 2. 分为左半部和右半部
    left = key_p10[:5]
    right = key_p10[5:]
    # 3. 左移 1 位生成 K1
    left_ls1 = left_shift(left, 1)
    right_ls1 = left_shift(right, 1)
    # 4. 合并并通过 P8 置换得到 K1
    key_ls1 = left_ls1 + right_ls1
    K1 = permute(key_ls1, P8)
    # 5. 左移 2 位生成 K2
    left_ls2 = left_shift(left_ls1, 2)
    right_ls2 = left_shift(right_ls1, 2)
    # 6. 合并并通过 P8 置换得到 K2
    key_ls2 = left_ls2 + right_ls2
    K2 = permute(key_ls2, P8)
    return K1, K2

def sbox_lookup(bits, sbox):
    """
    S 盒查找

    参数：
        bits (list): 4 位输入
        sbox (list): S 盒

    返回：
        list: 2 位输出
    """
    row = int(f"{bits[0]}{bits[3]}", 2)
    col = int(f"{bits[1]}{bits[2]}", 2)
    value = sbox[row][col]
    return [int(b) for b in f"{value:02b}"]

def fk(bits, key):
    """
    轮函数 Fk

    参数：
        bits (list): 8 位输入
        key (list): 8 位子密钥

    返回：
        list: 8 位输出
    """
    # 1. 分为左半部和右半部
    left = bits[:4]
    right = bits[4:]
    # 2. 对右半部进行扩展置换 EP
    right_ep = permute(right, EP)
    # 3. 与子密钥进行异或
    xor_result = [r ^ k for r, k in zip(right_ep, key)]
    # 4. 分为两部分，分别进入 S 盒
    sbox_input_left = xor_result[:4]
    sbox_input_right = xor_result[4:]
    sbox_output_left = sbox_lookup(sbox_input_left, SBox1)
    sbox_output_right = sbox_lookup(sbox_input_right, SBox2)
    # 5. 合并 S 盒输出并通过 P4 置换
    sbox_output = sbox_output_left + sbox_output_right
    sbox_output_p4 = permute(sbox_output, P4)
    # 6. 与左半部异或
    left_result = [l ^ s for l, s in zip(left, sbox_output_p4)]
    # 7. 合并结果
    return left_result + right

def encrypt(plaintext, K1, K2):
    """
    加密函数

    参数：
        plaintext (list): 8 位明文
        K1 (list): 子密钥 K1
        K2 (list): 子密钥 K2

    返回：
        list: 8 位密文
    """
    # 1. 初始置换 IP
    bits = permute(plaintext, IP)
    # 2. 轮函数 fk1
    bits = fk(bits, K1)
    # 3. 交换 SW
    bits = bits[4:] + bits[:4]
    # 4. 轮函数 fk2
    bits = fk(bits, K2)
    # 5. 逆初始置换 IP^{-1}
    ciphertext = permute(bits, IP_inv)
    return ciphertext

def decrypt(ciphertext, K1, K2):
    """
    解密函数

    参数：
        ciphertext (list): 8 位密文
        K1 (list): 子密钥 K1
        K2 (list): 子密钥 K2

    返回：
        list: 8 位明文
    """
    # 1. 初始置换 IP
    bits = permute(ciphertext, IP)
    # 2. 轮函数 fk2
    bits = fk(bits, K2)
    # 3. 交换 SW
    bits = bits[4:] + bits[:4]
    # 4. 轮函数 fk1
    bits = fk(bits, K1)
    # 5. 逆初始置换 IP^{-1}
    plaintext = permute(bits, IP_inv)
    return plaintext

def str_to_bit_list(s):
    """
    将字符串转换为位列表

    参数：
        s (str): 二进制字符串

    返回：
        list: 位列表
    """
    return [int(bit) for bit in s]

def bit_list_to_str(bit_list):
    """
    将位列表转换为字符串

    参数：
        bit_list (list): 位列表

    返回：
        str: 二进制字符串
    """
    return ''.join(str(bit) for bit in bit_list)

def analyze_identical_ciphertexts_for_plaintexts(plaintexts):
    """
    对用户输入的多个明文，使用所有可能的密钥进行加密，并找出那些使得所有明文加密后得到相同密文的密钥。

    参数：
        plaintexts (list of list): 多个明文的位列表

    输出：
        打印出所有使得所有明文加密后得到相同密文的密钥和对应的密文。
        如果没有找到符合条件的密钥，打印一个说明消息。
    """
    # 存储每个密钥加密每个明文后生成的密文
    key_to_ciphertext_map = {}

    # 遍历所有可能的密钥
    for i in range(1024):
        key_candidate = [int(b) for b in f"{i:010b}"]
        K1, K2 = key_generation(key_candidate)
        # 检查当前密钥加密每个明文是否产生相同的密文
        common_ciphertext = None
        is_common = True
        for plaintext in plaintexts:
            ciphertext = encrypt(plaintext, K1, K2)
            ciphertext_str = bit_list_to_str(ciphertext)
            if common_ciphertext is None:
                common_ciphertext = ciphertext_str
            elif common_ciphertext != ciphertext_str:
                is_common = False
                break
        
        if is_common:
            # 如果该密钥对所有明文产生了相同的密文，则记录
            key_to_ciphertext_map[common_ciphertext] = key_to_ciphertext_map.get(common_ciphertext, []) + [bit_list_to_str(key_candidate)]

    # 打印找到的密钥和对应的相同密文
    if key_to_ciphertext_map:
        for ciphertext, keys in key_to_ciphertext_map.items():
            print(f"密文 {ciphertext}\n有密钥 {'、'.join(keys)}\n")
    else:
        # 如果没有找到任何使得所有明文加密后密文相同的密钥
        print("没有找到任何密钥使得所有输入的明文加密后得到相同的密文。")


def main():
    """
    主函数，提供命令行交互
    """
    while True:
        print("\n请选择操作：")
        print("1. 分析一组明文相同密文的密钥")
        print("2. 退出")

        choice = input("请输入选项(1/2): ")

        if choice == '1':
            n = int(input("请输入明文的数量: "))
            plaintexts = []
            for i in range(n):
                plaintext_input = input(f"请输入第 {i+1} 个8位明文: ")
                plaintext = str_to_bit_list(plaintext_input)
                plaintexts.append(plaintext)
            analyze_identical_ciphertexts_for_plaintexts(plaintexts)

        elif choice == '2':
            print("退出程序")
            break

        else:
            print("无效的选项，请重试")

if __name__ == "__main__":
    main()
