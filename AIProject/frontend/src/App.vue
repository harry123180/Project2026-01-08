<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
      <router-link class="navbar-brand" to="/">AI Todo List</router-link>
      <div class="navbar-nav">
        <router-link class="nav-link" to="/">編輯任務</router-link>
        <router-link class="nav-link" to="/schedule">行程看板</router-link>
      </div>
    </div>
  </nav>

  <div class="container">
    <router-view></router-view>
  </div>
</template>

<style>
body {
  background-color: #f8f9fa;
}
</style>
