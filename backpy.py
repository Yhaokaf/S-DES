from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import threading
import random
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)

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
    [3, 1, 0, 2]
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

def decrypt(ciphertext, K1, K2):
    bits = permute(ciphertext, IP)
    bits = fk(bits, K2)
    bits = bits[4:] + bits[:4]
    bits = fk(bits, K1)
    plaintext = permute(bits, IP_inv)
    return plaintext

def str_to_bit_list(s):
    return [int(bit) for bit in s]

def bit_list_to_str(bit_list):
    return ''.join(str(bit) for bit in bit_list)

def ascii_to_bit_list(text):
    bit_list = []
    for char in text:
        bits = f"{ord(char):08b}"
        bit_list.extend(int(bit) for bit in bits)
    return bit_list

def bit_list_to_ascii(bit_list):
    chars = []
    for i in range(0, len(bit_list), 8):
        byte = bit_list[i:i + 8]
        char = chr(int(''.join(str(bit) for bit in byte), 2))
        chars.append(char)
    return ''.join(chars)

def encrypt_text(plaintext, key):
    key_bits = str_to_bit_list(key)
    K1, K2 = key_generation(key_bits)
    plaintext_bits = ascii_to_bit_list(plaintext)
    ciphertext_bits = []
    for i in range(0, len(plaintext_bits), 8):
        block = plaintext_bits[i:i + 8]
        encrypted_block = encrypt(block, K1, K2)
        ciphertext_bits.extend(encrypted_block)
    return bit_list_to_ascii(ciphertext_bits)

def decrypt_text(ciphertext, key):
    key_bits = str_to_bit_list(key)
    K1, K2 = key_generation(key_bits)
    ciphertext_bits = ascii_to_bit_list(ciphertext)
    plaintext_bits = []
    for i in range(0, len(ciphertext_bits), 8):
        block = ciphertext_bits[i:i + 8]
        decrypted_block = decrypt(block, K1, K2)
        plaintext_bits.extend(decrypted_block)
    return bit_list_to_ascii(plaintext_bits)

def brute_force_key(plaintext, ciphertext):
    def try_key_range(start, end, result):
        for i in range(start, end):
            key_candidate = f"{i:010b}"
            if encrypt_text(plaintext, key_candidate) == ciphertext:
                result.append(key_candidate)
                break

    start_time = time.time()
    num_threads = 4
    step = 1024 // num_threads
    threads = []
    result = []

    for i in range(num_threads):
        start = i * step
        end = (i + 1) * step
        thread = threading.Thread(target=try_key_range, args=(start, end, result))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()
    if result:
        return result[0], end_time - start_time
    else:
        return None, end_time - start_time

def average_brute_force_time(num_trials=5):
    avg_times = []
    pairs = []
    for _ in range(num_trials):
        plaintext = ''.join(random.choice('ABCD') for _ in range(2))
        key = f"{random.randint(0, 1023):010b}"
        ciphertext = encrypt_text(plaintext, key)

        total_time = brute_force_key(plaintext, ciphertext)[1]
        avg_times.append(total_time)
        pairs.append((plaintext, key))
    return avg_times, pairs

def plot_average_times(avg_times, pairs):
    x = np.arange(len(avg_times))
    labels = [f"P: {pair[0]}, K: {pair[1]}" for pair in pairs]
    plt.figure(figsize=(12, 8))
    plt.bar(x, avg_times, color='skyblue')
    plt.xlabel('Plaintext-Key Pair')
    plt.ylabel('Brute Force Time (seconds)')
    plt.title('Brute Force Time for Random Plaintext-Key Pairs')
    plt.xticks(x, labels, rotation=45, ha='right')
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# @app.route('/binary_encrypt', methods=['POST'])
# def api_binary_encrypt():
#     data = request.json
#     plaintext = str_to_bit_list(data.get('text'))
#     key = str_to_bit_list(data.get('key'))
#     K1, K2 = key_generation(key)
#     encrypted_bits = encrypt(plaintext, K1, K2)
#     return jsonify({'result': bit_list_to_str(encrypted_bits)})
#
# @app.route('/binary_decrypt', methods=['POST'])
# def api_binary_decrypt():
#     data = request.json
#     ciphertext = str_to_bit_list(data.get('text'))
#     key = str_to_bit_list(data.get('key'))
#     K1, K2 = key_generation(key)
#     decrypted_bits = decrypt(ciphertext, K1, K2)
#     return jsonify({'result': bit_list_to_str(decrypted_bits)})

def is_binary_string(s, length):
    # 检查是否为长度为 length 的二进制字符串
    return len(s) == length and all(c in '01' for c in s)

@app.route('/binary_encrypt', methods=['POST'])
def api_binary_encrypt():
    data = request.json
    plaintext = data.get('text')
    key = data.get('key')

    # 检查明文和密钥格式
    if not is_binary_string(plaintext, 8):
        return jsonify({'error': 'Plaintext must be an 8-bit binary string'}), 400
    if not is_binary_string(key, 10):
        return jsonify({'error': 'Key must be a 10-bit binary string'}), 400

    # 加密处理
    plaintext_bits = str_to_bit_list(plaintext)
    key_bits = str_to_bit_list(key)
    K1, K2 = key_generation(key_bits)
    encrypted_bits = encrypt(plaintext_bits, K1, K2)

    return jsonify({'result': bit_list_to_str(encrypted_bits)})

@app.route('/binary_decrypt', methods=['POST'])
def api_binary_decrypt():
    data = request.json
    ciphertext = data.get('text')
    key = data.get('key')

    # 检查密文和密钥格式
    if not is_binary_string(ciphertext, 8):
        return jsonify({'error': 'Ciphertext must be an 8-bit binary string'}), 400
    if not is_binary_string(key, 10):
        return jsonify({'error': 'Key must be a 10-bit binary string'}), 400

    # 解密处理
    ciphertext_bits = str_to_bit_list(ciphertext)
    key_bits = str_to_bit_list(key)
    K1, K2 = key_generation(key_bits)
    decrypted_bits = decrypt(ciphertext_bits, K1, K2)

    return jsonify({'result': bit_list_to_str(decrypted_bits)})



@app.route('/string_encrypt', methods=['POST'])
def api_string_encrypt():
    data = request.json
    plaintext = data.get('text')
    key = data.get('key')
    encrypted_text = encrypt_text(plaintext, key)
    print(encrypted_text)
    return jsonify({'result': encrypted_text})

@app.route('/string_decrypt', methods=['POST'])
def api_string_decrypt():
    data = request.json
    ciphertext = data.get('text')
    key = data.get('key')
    decrypted_text = decrypt_text(ciphertext, key)
    print(decrypted_text)
    return jsonify({'result': decrypted_text})


@app.route('/brute_force_analysis', methods=['GET'])
def api_brute_force_analysis():
    avg_times, pairs = average_brute_force_time(num_trials=5)
    plot_data = plot_average_times(avg_times, pairs)
    print(plot_data)
    return jsonify({'plot': plot_data})

if __name__ == '__main__':
    app.run(debug=True)