<template>
  <div>
    <h2 v-if="!pastScreening" class="text-h4 mb-4">Screen an Applicant</h2>

    <v-card class="pa-4 mb-4">
      <v-alert v-if="error" type="error" class="mb-3" closable>{{ error }}</v-alert>

      <v-autocomplete v-model="selectedId" :items="applicants" item-title="name" item-value="applicant_id" label="Select Applicant" variant="outlined" return-object clearable :loading="loadingApps" />

      <v-select v-model="responseLang" :items="['en','th']" label="Response Language" variant="outlined" class="mb-3" />

      <v-btn color="primary" @click="startScreen" :loading="screening" :disabled="!selectedId">Start Screening</v-btn>
    </v-card>

    <v-skeleton-loader v-if="loadingApps" type="list-item@5" />

    <div v-if="screeningActive">
      <v-chip v-if="pastScreening" :color="statusColor" size="small" class="mb-3">
        Status: {{ status }}
      </v-chip>

    <v-card v-if="!pastScreening" class="pa-4 mb-4">
        <v-card-title>Progress</v-card-title>
        <v-card-text>
          <v-chip v-for="step in progress" :key="step" color="green" class="mr-1 mb-1">{{ step }}</v-chip>
          <v-progress-linear v-if="status === 'running'" indeterminate color="primary" class="mt-2" />
          <v-alert v-if="status === 'error'" type="error" class="mt-2">{{ error }}</v-alert>
        </v-card-text>
      </v-card>

      <ScreeningResult v-if="result" :result="result" />

      <FeedbackForm
        v-if="status === 'done' && !hasFeedback && screeningDbId && isOwnScreening"
        :screening-id="screeningDbId"
        @submitted="onFeedbackSubmitted"
      />
      <v-alert
        v-else-if="status === 'done' && !hasFeedback && screeningDbId && !isOwnScreening"
        type="info" variant="tonal" class="mt-4"
      >
        Awaiting feedback from the screening officer
      </v-alert>

      <!-- Awaiting review: show feedback + review form -->
      <template v-if="feedbackData && status === 'pending_review'">
        <v-card class="mt-4 pa-4" variant="outlined">
          <v-card-title class="text-h6">Officer Feedback</v-card-title>
          <v-card-text>
            <v-chip :color="feedbackData.correct ? 'green' : 'red'" size="small">
              {{ feedbackData.correct ? 'Agreed with AI' : 'Override' }}
            </v-chip>
            <v-chip v-if="feedbackData.override_recommendation" size="small" class="ml-1">
              {{ feedbackData.override_recommendation }}
            </v-chip>
            <p v-if="feedbackData.comment" class="mt-2 text-body-2">{{ feedbackData.comment }}</p>
            <div class="text-caption text-grey mt-1">by {{ feedbackData.submitted_by_name }} — {{ new Date(feedbackData.created_at).toLocaleString() }}</div>
          </v-card-text>
        </v-card>
        <ReviewForm
          v-if="auth.isReviewer"
          :screening-id="screeningDbId"
          :feedback="feedbackData"
          @done="onReviewDone"
        />
        <div v-else class="mt-3 text-caption text-grey">Pending review by a senior officer</div>
      </template>

      <!-- Finalized: show feedback + review result -->
      <template v-if="feedbackData && ['approved','rejected','sent_back'].includes(status)">
        <v-card class="mt-4 pa-4" variant="outlined">
          <v-card-title class="d-flex align-center">
            <span>Officer Feedback</span>
            <v-chip :color="statusColor" size="small" class="ml-2">{{ status }}</v-chip>
          </v-card-title>
          <v-card-text>
            <v-chip :color="feedbackData.correct ? 'green' : 'red'" size="small">
              {{ feedbackData.correct ? 'Agreed with AI' : 'Override' }}
            </v-chip>
            <v-chip v-if="feedbackData.override_recommendation" size="small" class="ml-1">
              {{ feedbackData.override_recommendation }}
            </v-chip>
            <p v-if="feedbackData.comment" class="mt-2 text-body-2">{{ feedbackData.comment }}</p>
            <div class="text-caption text-grey mt-1">Officer: {{ feedbackData.submitted_by_name }} — {{ new Date(feedbackData.created_at).toLocaleString() }}</div>
            <v-divider class="my-3" />
            <div class="text-body-2 text-grey">Reviewer: {{ feedbackData.reviewed_by_name || '?' }}</div>
            <p v-if="feedbackData.review_comment" class="text-body-2">{{ feedbackData.review_comment }}</p>
            <div class="text-caption text-grey mt-1">{{ feedbackData.reviewed_at ? new Date(feedbackData.reviewed_at).toLocaleString() : '' }}</div>
          </v-card-text>
        </v-card>
      </template>

      <AgentChain v-if="agentStates" :states="agentStates" />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { applicantsAPI } from '../api/applicants'
import { screeningAPI } from '../api/screening'
import { useAuthStore } from '../stores/auth'
import ScreeningResult from '../components/ScreeningResult.vue'
import AgentChain from '../components/AgentChain.vue'
import FeedbackForm from '../components/FeedbackForm.vue'
import ReviewForm from '../components/ReviewForm.vue'

const route = useRoute()
const auth = useAuthStore()
const applicants = ref([])
const selectedId = ref(null)
const responseLang = ref('en')
const screening = ref(false)
const loadingApps = ref(false)
const screeningActive = ref(false)
const pastScreening = ref(false)
const jobId = ref('')
const status = ref('')
const progress = ref([])
const result = ref(null)
const agentStates = ref(null)
const screeningDbId = ref(null)
const feedbackData = ref(null)
const hasFeedback = ref(false)
const isOwnScreening = ref(false)
const error = ref('')
let pollTimer = null

const statusColor = computed(() => {
  const colors = {
    done: 'green', pending_review: 'orange', approved: 'blue',
    rejected: 'red', sent_back: 'grey', error: 'red', running: 'orange', queued: 'grey',
  }
  return colors[status.value] || 'grey'
})

onMounted(async () => {
  loadingApps.value = true
  const res = await applicantsAPI.list().catch(() => ({ results: [] }))
  applicants.value = res.results || res || []
  loadingApps.value = false

  if (route.query.jobId) {
    jobId.value = route.query.jobId
    screeningActive.value = true
    pastScreening.value = true
    await fetchScreeningByJobId()
    if (['pending_review', 'approved', 'rejected', 'sent_back'].includes(status.value)) {
      await fetchFeedback()
    }
    if (!['queued', 'running'].includes(status.value)) return
    startPolling()
  }
})

onUnmounted(() => {
  if (pollTimer) clearTimeout(pollTimer)
})

async function fetchScreeningByJobId() {
  const listRes = await screeningAPI.list({ search: jobId.value }).catch(() => ({ results: [] }))
  const match = listRes.results?.find((s) => s.job_id === jobId.value)
  if (match) {
    screeningDbId.value = match.id
    status.value = match.status
    progress.value = match.progress || []
    hasFeedback.value = match.has_feedback || false
    isOwnScreening.value = match.initiated_by === auth.user?.id
    if (match.result_data) result.value = match.result_data
    if (match.agent_states) agentStates.value = match.agent_states
  }
}

async function fetchFeedback() {
  if (!screeningDbId.value) return
  const all = await screeningAPI.feedbackList().catch(() => [])
  const match = all.find((f) => f.screening === screeningDbId.value)
  if (match) feedbackData.value = match
}

function onFeedbackSubmitted() {
  status.value = 'pending_review'
  fetchFeedback()
}

function onReviewDone() {
  fetchFeedback()
  fetchScreeningByJobId()
}

async function startScreen() {
  if (!selectedId.value) return
  if (pollTimer) clearTimeout(pollTimer)
  error.value = ''
  screening.value = true
  try {
    const res = await screeningAPI.screen({
      applicant_id: selectedId.value.applicant_id,
      response_lang: responseLang.value,
    })
    jobId.value = res.job_id
    pastScreening.value = false
    screeningActive.value = true
    feedbackData.value = null
    result.value = null
    agentStates.value = null
    status.value = 'queued'
    progress.value = []
    startPolling()
  } catch (e) {
    error.value = e.response?.data?.detail || e.message || 'Screening failed'
  } finally {
    screening.value = false
  }
}

async function startPolling() {
  if (pollTimer) clearTimeout(pollTimer)
  const poll = async () => {
    try {
      const data = await screeningAPI.status(jobId.value)
      status.value = data.status
      progress.value = data.progress || []
      if (data.result) result.value = data.result
      if (data.agent_states) agentStates.value = data.agent_states
      if (data.error) error.value = data.error

      if (['done', 'error', 'pending_review', 'approved', 'rejected', 'sent_back'].includes(data.status)) {
        if (['done'].includes(data.status) && data.result?.screening_id) {
          screeningDbId.value = data.result.screening_id
        } else {
          const listRes = await screeningAPI.list({ search: jobId.value }).catch(() => ({ results: [] }))
          const match = listRes.results?.find((s) => s.job_id === jobId.value)
          if (match) {
            screeningDbId.value = match.id
            hasFeedback.value = match.has_feedback || false
            isOwnScreening.value = match.initiated_by === auth.user?.id
          }
        }
        return
      }
      pollTimer = setTimeout(poll, 2000)
    } catch (e) {
      pollTimer = setTimeout(poll, 5000)
    }
  }
  poll()
}
</script>
