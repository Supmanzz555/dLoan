<template>
  <div>
    <h2 class="text-h4 mb-4">Activity Log</h2>

    <v-data-table :headers="headers" :items="logs" :items-per-page="-1" :loading="loading">
      <template #item.correct="{ item }">
        <v-chip v-if="item.action === 'submit_feedback' && item.details?.correct" color="green" size="small">Agree</v-chip>
        <v-chip v-else-if="item.action === 'submit_feedback'" color="red" size="small">Override</v-chip>
      </template>
      <template #item.details="{ item }">
        {{ typeof item.details === 'object' ? JSON.stringify(item.details) : item.details }}
      </template>
      <template #item.created_at="{ item }">
        {{ new Date(item.created_at).toLocaleString() }}
      </template>
    </v-data-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authAPI } from '../api/auth'

const logs = ref([])
const loading = ref(false)

const headers = [
  { title: 'User', key: 'username' },
  { title: 'Action', key: 'action' },
  { title: 'Details', key: 'details' },
  { title: 'IP', key: 'ip_address' },
  { title: 'Time', key: 'created_at' },
]

onMounted(async () => {
  loading.value = true
  const res = await authAPI.activityLog().catch(() => [])
  logs.value = res || []
  loading.value = false
})
</script>
