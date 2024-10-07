<template>
  <router-view />
</template>

<script setup>
</script>

<style scoped>
/* 设置全局背景图片 */
body {
  margin: 0;
  padding: 0;
  background-image: url('./components/background.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
</style>
