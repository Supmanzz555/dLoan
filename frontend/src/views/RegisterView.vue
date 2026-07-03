<template>
  <div class="register-wrapper">
    <v-card width="420" class="pa-6" style="border-radius: 16px">
      <div class="text-center mb-4">
        <v-icon color="primary" size="48">mdi-account-plus</v-icon>
        <div class="text-h5 font-weight-bold mt-2">Create Account</div>
      </div>
      <v-alert v-if="error" type="error" class="mb-3" closable>{{ error }}</v-alert>
      <v-text-field v-model="username" label="Username" variant="outlined" prepend-inner-icon="mdi-account" />
      <v-text-field v-model="email" label="Email" type="email" variant="outlined" prepend-inner-icon="mdi-email" />
      <v-text-field v-model="password" label="Password" type="password" variant="outlined" prepend-inner-icon="mdi-lock" />
      <v-btn color="primary" block class="mt-2" @click="register" :loading="loading">Register</v-btn>
      <v-btn variant="text" block class="mt-2" :to="{ name: 'Login' }">Already have an account?</v-btn>
    </v-card>
  </div>
</template>

<style scoped>
.register-wrapper {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1565C0, #FF8F00);
}
</style>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function register() {
  error.value = ''
  loading.value = true
  try {
    await auth.register({ username: username.value, email: email.value, password: password.value })
    router.push('/')
  } catch (e) {
    error.value = Object.values(e.response?.data || {}).flat().join(', ') || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
