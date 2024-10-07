<template>
<div id="login">
    <div id="contain">
        <div id="right_card">
            <el-card class="el-card">
                <h2>8位二进制加密/解密</h2>
                <form class="login" @submit.prevent="handleBinaryAction">
                    <input v-shake type="text" v-model="binaryForm.text" placeholder="输入8位二进制明文/密文">
                    <input v-shake type="password" v-model="binaryForm.key" placeholder="输入10位二进制密钥">
                </form>
                <div class="message">
                    <span v-html="binaryError"></span>
                </div>
                <div id="btn" class="button-row">
                    <div class="button-borders">
                        <button class="primary-button" @click="binaryDecrypt">解密</button>
                    </div>
                    <div class="button-borders">
                        <button class="primary-button" @click="binaryEncrypt">加密</button>
                    </div>

                </div>
                <div v-if="binaryResult">
                    <h3>结果: {{ binaryResult }}</h3>
                </div>
            </el-card>
            <el-card class="el-card">
                <h2>字符串加密/解密</h2>
                <form class="login" @submit.prevent="handleStringAction">
                    <input v-shake type="text" v-model="stringForm.text" placeholder="输入字符串明文/密文">
                    <input v-shake type="password" v-model="stringForm.key" placeholder="输入10位二进制密钥">
                </form>
                <div class="message">
                    <span v-html="stringError"></span>
                </div>
                <div id="btn" class="button-row">
                    <div class="button-borders">
                        <button class="primary-button" @click="stringDecrypt">解密</button>
                    </div>
                    <div class="button-borders">
                        <button class="primary-button" @click="stringEncrypt">加密</button>
                    </div>

                    <div class="button-borders">
                        <button class="primary-button" @click="bruteForceAnalysis">暴力破解分析</button>
                    </div>
                </div>
                <div v-if="stringResult">
                    <h3>结果: {{ stringResult }}</h3>
                </div>
            </el-card>
        </div>
        <div id="left_card">
            <div v-if="plotData" class="image-container">
                <img :src="'data:image/png;base64,' + plotData" alt="Brute Force Analysis" class="analysis-image">
            </div>
        </div>
    </div>
</div>
</template>

<script>
import { reactive, ref } from 'vue';
import axios from 'axios';

export default {
    name: "AppLogin",
    setup() {
        const binaryForm = reactive({
            text: "",
            key: ""
        });
        const stringForm = reactive({
            text: "",
            key: ""
        });
        const binaryError = ref('');
        const stringError = ref('');
        const binaryResult = ref('');
        const stringResult = ref('');
        const plotData = ref('');

        const binaryDecrypt = async () => {
            try {
                const response = await axios.post('http://localhost:5000/binary_decrypt', {
                    text: binaryForm.text,
                    key: binaryForm.key
                });
                binaryResult.value = response.data.result;
            } catch (err) {
                binaryError.value = '解密失败，请按照位数要求输入';
            }
        };

        const binaryEncrypt = async () => {
            try {
                const response = await axios.post('http://localhost:5000/binary_encrypt', {
                    text: binaryForm.text,
                    key: binaryForm.key
                });
                binaryResult.value = response.data.result;
            } catch (err) {
                binaryError.value = '加密失败，请按照位数要求输入';
            }
        };

        const binaryBruteForceDecrypt = async () => {
            try {
                const response = await axios.post('http://localhost:5000/binary_brute_force', {
                    text: binaryForm.text,
                    plaintext: binaryForm.text // 确保发送了明文
                });
                const keys = response.data.keys.join(', ');
                binaryResult.value = `明文: ${response.data.plaintext}, 密钥: [${keys}], 时间: ${response.data.time}秒`;
                alert(`可能的密钥: [${keys}]`);
            } catch (err) {
                binaryError.value = '暴力解密失败，请按照位数要求输入';
            }
        };

        const stringDecrypt = async () => {
            try {
                const response = await axios.post('http://localhost:5000/string_decrypt', {
                    text: stringForm.text,
                    key: stringForm.key
                });
                stringResult.value = response.data.result;
            } catch (err) {
                stringError.value = '解密失败，请按照位数要求输入';
            }
        };

        const stringEncrypt = async () => {
            try {
                const response = await axios.post('http://localhost:5000/string_encrypt', {
                    text: stringForm.text,
                    key: stringForm.key
                });
                stringResult.value = response.data.result;
            } catch (err) {
                stringError.value = '加密失败，请按照位数要求输入';
            }
        };

        const stringBruteForceDecrypt = async () => {
            try {
                const response = await axios.post('http://localhost:5000/string_brute_force', {
                    text: stringForm.text,
                    plaintext: stringForm.text // 确保发送了明文
                });
                const keys = response.data.keys.join(', ');
                stringResult.value = `明文: ${response.data.plaintext}, 密钥: [${keys}], 时间: ${response.data.time}秒`;
                alert(`可能的密钥: [${keys}]`);
            } catch (err) {
                stringError.value = '暴力解密失败，请按照位数要求输入';
            }
        };

        const bruteForceAnalysis = async () => {
            try {
                const response = await axios.get('http://localhost:5000/brute_force_analysis');
                plotData.value = response.data.plot;
            } catch (err) {
                stringError.value = '暴力破解分析失败，请按照位数要求输入';
            }
        };

        return {
            binaryForm,
            stringForm,
            binaryError,
            stringError,
            binaryResult,
            stringResult,
            plotData,
            binaryDecrypt,
            binaryEncrypt,
            binaryBruteForceDecrypt,
            stringDecrypt,
            stringEncrypt,
            stringBruteForceDecrypt,
            bruteForceAnalysis
        };
    }
}
</script>

<style lang="less" scoped>
#login {
    position: relative;
    width: 100vw;
    height: 100vh;
    background-image: url('../components/backpic.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-color: #a7a8bd;
}

#contain {
    height: 100%;
    display: flex;
    flex-direction: row;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

#left_card {
    width: 50%;
    text-align: center;
    display: flex;
    justify-content: center;
    align-items: center;
}

.image-container {
    width: 120%;
    max-width: 700px;
    opacity: 0.95; /* 设置透明度 */
}

.analysis-image {
    width: 800px;
    height: auto;
}

#right_card {
    width: 50%; /* 设置宽度为60% */
    display: flex;
    flex-direction: column;
    align-items: center;
    .el-card {
        width: 80%;
        margin: 20px 0;
        border-radius: 25px;
        background-color: rgba(255, 255, 255, 0.1);
    }
}

.button-row {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    gap: 10px; /* 按钮之间的间距 */
}


.login {
    input {
        width: 80%;
        height: 45px;
        margin-top: 10px;
        border: 1px solid white;
        background-color: rgba(255, 255, 255, 0.5);
        border-radius: 10px;
        font-size: inherit;
        padding-left: 20px;
        outline: none;
    }
}

.message {
    margin-top: 26px;
    font-size: 0.9rem;
    color: red;
}

.primary-button {
    font-family: 'Ropa Sans', sans-serif;
    color: white;
    cursor: pointer;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 0.05rem;
    border: 1px solid #0E1822;
    padding: 0.8rem 2.1rem;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 531.28 200'%3E%3Cdefs%3E%3Cstyle%3E .shape %7B fill: %23FF4655 %7D %3C/style%3E%3C/defs%3E%3Cg id='Layer_2' data-name='Layer 2'%3E%3Cg id='Layer_1-2' data-name='Layer 1'%3E%3Cpolygon class='shape' points='415.81 200 0 200 115.47 0 531.28 0 415.81 200' /%3E%3C/g%3E%3C/g%3E%3C/svg%3E%0A");
    background-color: #f77643;
    background-size: 200%;
    background-position: 200%;
    background-repeat: no-repeat;
    transition: 0.3s ease-in-out;
    transition-property: background-position, border, color;
    position: relative;
    z-index: 1;
}


.primary-button:hover {
    border: 1px solid #FF4655;
    color: white;
    background-position: 40%;
}

.primary-button:before {
    content: "";
    position: absolute;
    background-color: #afd0f1;
    width: 0.2rem;
    height: 0.2rem;
    top: -1px;
    left: -1px;
    transition: background-color 0.15s ease-in-out;
}

.primary-button:hover:before {
    background-color: white;
}

.primary-button:hover:after {
    background-color: white;
}

.primary-button:after {
    content: "";
    position: absolute;
    background-color: #FF4655;
    width: 0.3rem;
    height: 0.3rem;
    bottom: -1px;
    right: -1px;
    transition: background-color 0.15s ease-in-out;
}

.button-borders {
    position: relative;
    width: fit-content;
    height: fit-content;
}

.button-borders:before {
    content: "";
    position: absolute;
    width: calc(100% + 0.5em);
    height: 50%;
    left: -0.3em;
    top: -0.3em;
    border: 1px solid #a7d3ff;
    border-bottom: 0px;
}

.button-borders:after {
    content: "";
    position: absolute;
    width: calc(100% + 0.5em);
    height: 50%;
    left: -0.3em;
    bottom: -0.3em;
    border: 1px solid #8faecc;
    border-top: 0px;
}

.shape {
    fill: #a3b8ce;
}
</style>