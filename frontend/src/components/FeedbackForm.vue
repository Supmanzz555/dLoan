<template>
  <v-card class="mt-4 pa-4" title="Officer Feedback">
    <v-alert v-if="submitted" type="success" class="mb-3">
      Feedback saved
      <template #close>
        <v-btn variant="text" size="small" @click="resetForm">Submit another</v-btn>
      </template>
    </v-alert>
    <v-alert v-if="error" type="error" closable @click:close="error = ''">{{ error }}</v-alert>

    <template v-if="!submitted">
      <v-radio-group v-model="correct" inline>
        <v-radio label="Correct" :value="true" />
        <v-radio label="Incorrect" :value="false" />
      </v-radio-group>

      <v-select v-if="correct === false" v-model="override" :items="['Proceed','Refer','Decline']" label="Override Recommendation" variant="outlined" class="mb-3" />

      <v-textarea
        v-model="comment"
        :label="correct ? 'Comment (optional)' : 'Comment * (required for override)'"
        :rules="commentRules"
        variant="outlined" rows="2"
      />

      <v-btn color="primary" @click="submit" :loading="saving">Submit Feedback</v-btn>
    </template>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { screeningAPI } from '../api/screening'

const props = defineProps({ screeningId: { type: Number, required: true } })
const emit = defineEmits(['submitted'])

const correct = ref(true)
const override = ref(null)
const comment = ref('')
const saving = ref(false)
const submitted = ref(false)
const error = ref('')

const commentRules = computed(() => {
  if (correct.value) return []
  return [(v) => (v && v.trim().length > 0) || 'Reason required when overriding AI']
})

function resetForm() {
  correct.value = true
  override.value = null
  comment.value = ''
  submitted.value = false
  error.value = ''
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await screeningAPI.feedback({
      screening_id: props.screeningId,
      correct: correct.value,
      override_recommendation: override.value,
      comment: comment.value,
    })
    submitted.value = true
    emit('submitted')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to save feedback'
  } finally {
    saving.value = false
  }
}
</script>
