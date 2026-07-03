<template>
  <v-card class="mt-4 pa-4" variant="outlined">
    <v-card-title class="text-h6">Review Screening</v-card-title>
    <v-card-text>
      <v-alert v-if="reviewed" type="success" class="mb-3">
        Screening {{ reviewResult }}
        <template #close>
          <v-btn v-if="reviewResult === 'sent_back'" variant="text" size="small" @click="$emit('refresh')">Re-screen</v-btn>
        </template>
      </v-alert>
      <v-alert v-if="error" type="error" closable class="mb-3">{{ error }}</v-alert>

      <div v-if="feedback" class="mb-4">
        <div class="text-body-2 text-grey mb-1">Officer Feedback</div>
        <v-chip :color="feedback.correct ? 'green' : 'red'" size="small">
          {{ feedback.correct ? 'Agreed with AI' : 'Override' }}
        </v-chip>
        <v-chip v-if="feedback.override_recommendation" size="small" class="ml-1">
          {{ feedback.override_recommendation }}
        </v-chip>
        <p v-if="feedback.comment" class="mt-2 text-body-2">{{ feedback.comment }}</p>
        <div class="text-caption text-grey mt-1">by {{ feedback.submitted_by_name }} — {{ new Date(feedback.created_at).toLocaleString() }}</div>
      </div>

      <template v-if="!reviewed">
        <v-textarea v-model="comment" label="Review comment" variant="outlined" rows="2" class="mb-3" />

        <div class="d-flex ga-2">
          <v-btn color="green" @click="submit('concur')" :loading="loading">Concur</v-btn>
          <v-btn color="orange" @click="submit('send_back')" :loading="loading">Send Back</v-btn>
        </div>
      </template>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { screeningAPI } from '../api/screening'

const props = defineProps({
  screeningId: { type: Number, required: true },
  feedback: { type: Object, default: null },
})
const emit = defineEmits(['done', 'refresh'])

const comment = ref('')
const loading = ref(false)
const reviewed = ref(false)
const reviewResult = ref('')
const error = ref('')

async function submit(action) {
  loading.value = true
  error.value = ''
  try {
    const res = await screeningAPI.review(props.screeningId, {
      action,
      comment: comment.value,
    })
    reviewResult.value = res.status
    reviewed.value = true
    emit('done', { action, status: res.status })
  } catch (e) {
    error.value = e.response?.data?.detail || 'Review failed'
  } finally {
    loading.value = false
  }
}
</script>
