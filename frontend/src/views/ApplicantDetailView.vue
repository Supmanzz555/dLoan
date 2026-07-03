<template>
  <div>
    <v-btn variant="text" prepend-icon="mdi-arrow-left" class="mb-2" :to="{ name: 'Applicants' }">Back</v-btn>
    <h2 class="text-h4 mb-4">{{ applicant.name }}</h2>

    <v-row>
      <v-col cols="12" md="6">
        <v-card title="Details" class="pa-2">
          <v-list>
            <v-list-item><v-list-item-title>ID</v-list-item-title><v-list-item-subtitle>{{ applicant.applicant_id }}</v-list-item-subtitle></v-list-item>
            <v-list-item><v-list-item-title>Age</v-list-item-title><v-list-item-subtitle>{{ applicant.age }}</v-list-item-subtitle></v-list-item>
            <v-list-item><v-list-item-title>Employment</v-list-item-title><v-list-item-subtitle>{{ applicant.employment_type }}</v-list-item-subtitle></v-list-item>
            <v-list-item><v-list-item-title>Income</v-list-item-title><v-list-item-subtitle>${{ applicant.monthly_income?.toLocaleString() }}</v-list-item-subtitle></v-list-item>
            <v-list-item><v-list-item-title>Debt</v-list-item-title><v-list-item-subtitle>${{ applicant.monthly_debt?.toLocaleString() }}</v-list-item-subtitle></v-list-item>
            <v-list-item><v-list-item-title>Loan Request</v-list-item-title><v-list-item-subtitle>${{ applicant.requested_loan_amount?.toLocaleString() }}</v-list-item-subtitle></v-list-item>
          </v-list>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card title="Credit History" class="pa-2">
          <v-card-text>{{ applicant.credit_history || 'N/A' }}</v-card-text>
        </v-card>
        <v-card title="Notes" class="pa-2 mt-4">
          <v-card-text>{{ applicant.notes || 'N/A' }}</v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-card class="mt-4" title="Screen This Applicant">
      <v-card-text>
        <v-btn color="primary" @click="screenNow" :loading="screening">Run Screening</v-btn>
        <v-chip v-if="jobId" class="ml-3" color="info">Job: {{ jobId }}</v-chip>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { applicantsAPI } from '../api/applicants'
import { screeningAPI } from '../api/screening'

const route = useRoute()
const router = useRouter()
const applicant = ref({})
const screening = ref(false)
const jobId = ref('')

onMounted(async () => {
  applicant.value = await applicantsAPI.get(route.params.id)
})

async function screenNow() {
  screening.value = true
  const res = await screeningAPI.screen({ applicant_id: applicant.value.applicant_id })
  jobId.value = res.job_id
  screening.value = false
  router.push({ name: 'Screen', query: { jobId: res.job_id } })
}
</script>
