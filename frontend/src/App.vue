<template>
  <el-container class="app-container">
    <el-header>
      <h1>EcomImagePro - 电商图片处理工具</h1>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  width: 100%;
  height: 100vh;
}

.app-container {
  height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.el-header h1 {
  font-size: 24px;
  font-weight: 500;
}

.el-main {
  padding: 20px;
  background-color: #f5f5f5;
}
</style>

