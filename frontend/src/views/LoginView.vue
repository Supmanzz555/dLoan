<template>
  <div class="login-wrapper">
    <v-card width="420" class="pa-6" style="border-radius: 16px">
      <div class="text-center mb-4">
        <v-icon color="primary" size="48">mdi-credit-search</v-icon>
        <div class="text-h5 font-weight-bold mt-2">Welcome</div>
        <div class="text-caption text-grey">AI-Powered Credit Screening System</div>
      </div>
      <v-alert v-if="error" type="error" class="mb-3" closable>{{ error }}</v-alert>
      <v-text-field v-model="username" label="Username" variant="outlined" prepend-inner-icon="mdi-account" />
      <v-text-field v-model="password" label="Password" type="password" variant="outlined" prepend-inner-icon="mdi-lock" @keyup.enter="login" />
      <v-checkbox v-model="remember" label="Stay logged in" hide-details class="mt-n2" />
      <v-btn color="primary" block class="mt-4" @click="login" :loading="loading">Login</v-btn>
      <v-btn variant="text" block class="mt-2" :to="{ name: 'Register' }">Create account</v-btn>
    </v-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const remember = ref(true)
const error = ref('')
const loading = ref(false)

async function login() {
  error.value = ''
  loading.value = true
  try {
    await auth.login({ username: username.value, password: password.value, remember: remember.value })
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1565C0, #FF8F00);
}
</style>
