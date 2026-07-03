<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <h2 class="text-h4">Screening History</h2>
      <v-btn color="primary" variant="outlined" prepend-icon="mdi-download" @click="exportCsv">Export CSV</v-btn>
    </div>

    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-text-field v-model="search" label="Search by job ID or applicant name" prepend-inner-icon="mdi-magnify" variant="outlined" density="compact" hide-details />
      </v-col>
      <v-col cols="12" md="3">
        <v-select v-model="statusFilter" :items="statusOptions" label="Status" variant="outlined" density="compact" hide-details @update:model-value="load" />
      </v-col>
    </v-row>

    <v-data-table v-if="!loading" :headers="headers" :items="screenings" :items-per-page="-1" @click:row="viewScreening">
      <template #item.status="{ item }">
        <v-chip :color="statusChipColor(item.status)" size="small">{{ item.status }}</v-chip>
      </template>
      <template #item.created_at="{ item }">
        {{ new Date(item.created_at).toLocaleString() }}
      </template>
    </v-data-table>
    <v-skeleton-loader v-else type="table-row@10" />

    <v-card class="mt-6" title="Feedback / Override Log">
      <v-card-text>
        <v-data-table v-if="!loadingFeedback" :headers="fbHeaders" :items="feedbackLog" :items-per-page="-1">
          <template #item.correct="{ item }">
            <v-chip :color="item.correct ? 'green' : 'red'" size="small">{{ item.correct ? 'Agree' : 'Override' }}</v-chip>
          </template>
          <template #item.review_status="{ item }">
            <v-chip v-if="item.review_status" :color="item.review_status === 'concur' ? 'green' : 'orange'" size="small">{{ item.review_status }}</v-chip>
            <span v-else class="text-grey text-caption">—</span>
          </template>
          <template #item.created_at="{ item }">
            {{ new Date(item.created_at).toLocaleString() }}
          </template>
        </v-data-table>
        <v-skeleton-loader v-else type="table-row@5" />
        <div v-if="!loadingFeedback && !feedbackLog.length" class="text-grey text-center pa-4">No feedback yet</div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { screeningAPI } from '../api/screening'
import { dashboardAPI } from '../api/dashboard'

const router = useRouter()
const search = ref('')
const statusFilter = ref('')
const screenings = ref([])
const feedbackLog = ref([])
const loading = ref(false)
const loadingFeedback = ref(false)
const statusOptions = ['', 'done', 'error', 'pending_review', 'approved', 'rejected', 'sent_back']

const headers = [
  { title: 'Job ID', key: 'job_id' },
  { title: 'Applicant', key: 'applicant_name' },
  { title: 'Status', key: 'status' },
  { title: 'Initiated By', key: 'initiated_by_name' },
  { title: 'Created', key: 'created_at' },
]

const fbHeaders = [
  { title: 'Job ID', key: 'job_id' },
  { title: 'Applicant', key: 'applicant_name' },
  { title: 'Verdict', key: 'correct' },
  { title: 'Override', key: 'override_recommendation' },
  { title: 'Review', key: 'review_status' },
  { title: 'Comment', key: 'comment' },
  { title: 'By', key: 'submitted_by_name' },
  { title: 'Date', key: 'created_at' },
]

async function load() {
  loading.value = true
  const params = {}
  if (search.value) params.search = search.value
  if (statusFilter.value) params.status = statusFilter.value
  const res = await screeningAPI.list(params).catch(() => ({ results: [] }))
  screenings.value = res.results || []
  loading.value = false
}

let debounceTimer = null
watch(search, () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(load, 300)
})

function statusChipColor(s) {
  return { done: 'green', pending_review: 'orange', approved: 'blue', rejected: 'red', sent_back: 'grey', error: 'red', running: 'orange', queued: 'grey' }[s] || 'grey'
}

function viewScreening(event, { item }) {
  router.push({ name: 'Screen', query: { jobId: item.job_id } })
}

async function exportCsv() {
  try {
    const blob = await dashboardAPI.exportCsv()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'screenings.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Export failed:', e)
  }
}

async function loadFeedback() {
  loadingFeedback.value = true
  const res = await screeningAPI.feedbackList().catch(() => [])
  feedbackLog.value = res || []
  loadingFeedback.value = false
}

onMounted(() => {
  load()
  loadFeedback()
})

onUnmounted(() => {
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>
