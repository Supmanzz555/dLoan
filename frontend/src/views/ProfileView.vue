<template>
  <div>
    <div class="d-flex align-center mb-4">
      <h2 class="text-h4">Profile</h2>
      <v-chip v-if="auth.isSuperAdmin" color="orange" class="ml-3" size="small">Super Admin</v-chip>
      <v-chip v-else-if="auth.user?.role === 'reviewer'" color="purple" class="ml-3" size="small">Reviewer</v-chip>
      <v-chip v-else-if="auth.isAdmin" color="primary" class="ml-3" size="small">Admin</v-chip>
    </div>

    <v-row>
      <v-col cols="12" md="6">
        <v-card title="Settings" class="pa-4">
          <v-alert v-if="saveMsg" :type="saveMsg.type" closable class="mb-3">{{ saveMsg.text }}</v-alert>
          <v-text-field v-model="form.first_name" label="First Name" variant="outlined" />
          <v-text-field v-model="form.last_name" label="Last Name" variant="outlined" />
          <v-text-field v-model="form.email" label="Email" variant="outlined" />
          <v-select v-model="form.preferred_language" :items="['en','th']" label="Language" variant="outlined" />
          <v-btn color="primary" @click="saveProfile" :loading="saving">Save</v-btn>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card title="Change Password" class="pa-4">
          <v-alert v-if="pwMsg" :type="pwMsg.type" closable class="mb-3">{{ pwMsg.text }}</v-alert>
          <v-text-field v-model="pw.old_password" label="Current Password" type="password" variant="outlined" />
          <v-text-field v-model="pw.new_password" label="New Password" type="password" variant="outlined" />
          <v-btn color="primary" @click="changePw" :loading="changingPw">Change</v-btn>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authAPI } from '../api/auth'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const form = ref({ first_name: '', last_name: '', email: '', preferred_language: 'en' })
const pw = ref({ old_password: '', new_password: '' })
const saving = ref(false)
const changingPw = ref(false)
const saveMsg = ref(null)
const pwMsg = ref(null)

onMounted(() => {
  const u = auth.user
  if (u) {
    form.value = {
      first_name: u.first_name || '',
      last_name: u.last_name || '',
      email: u.email || '',
      preferred_language: u.preferred_language || 'en',
    }
  }
})

async function saveProfile() {
  saving.value = true
  saveMsg.value = null
  try {
    const res = await authAPI.updateProfile(form.value)
    auth.user = res
    localStorage.setItem('user', JSON.stringify(res))
    saveMsg.value = { type: 'success', text: 'Profile updated' }
  } catch (e) {
    saveMsg.value = { type: 'error', text: 'Update failed' }
  } finally {
    saving.value = false
  }
}

async function changePw() {
  changingPw.value = true
  pwMsg.value = null
  try {
    await authAPI.changePassword(pw.value)
    pwMsg.value = { type: 'success', text: 'Password changed' }
    pw.value = { old_password: '', new_password: '' }
  } catch (e) {
    pwMsg.value = { type: 'error', text: e.response?.data?.detail || 'Failed' }
  } finally {
    changingPw.value = false
  }
}
</script>
