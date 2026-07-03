<template>
  <div>
    <h2 class="text-h4 mb-4">{{ isEdit ? 'Edit' : 'New' }} Applicant</h2>
    <v-card class="pa-4">
      <v-alert v-if="error" type="error" class="mb-3" closable>{{ error }}</v-alert>

      <v-text-field v-model="form.name" label="Name" variant="outlined" />
      <v-row>
        <v-col cols="4"><v-text-field v-model.number="form.age" label="Age" type="number" variant="outlined" /></v-col>
        <v-col cols="4"><v-text-field v-model.number="form.monthly_income" label="Monthly Income" type="number" prefix="$" variant="outlined" /></v-col>
        <v-col cols="4"><v-text-field v-model.number="form.monthly_debt" label="Monthly Debt" type="number" prefix="$" variant="outlined" /></v-col>
      </v-row>
      <v-select v-model="form.employment_type" :items="['salaried','self-employed','business owner','unemployed','retired']" label="Employment Type" variant="outlined" />
      <v-text-field v-model.number="form.requested_loan_amount" label="Loan Amount" type="number" prefix="$" variant="outlined" />
      <v-textarea v-model="form.credit_history" label="Credit History" variant="outlined" rows="2" />
      <v-textarea v-model="form.notes" label="Notes" variant="outlined" rows="2" />

      <v-btn color="primary" @click="save" :loading="saving">Save</v-btn>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { applicantsAPI } from '../api/applicants'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const error = ref('')

const form = ref({
  applicant_id: '', name: '', age: 30, employment_type: 'salaried',
  monthly_income: 0, monthly_debt: 0, requested_loan_amount: 0,
  credit_history: '', notes: '', uploaded_documents: [],
})

onMounted(async () => {
  if (isEdit.value) {
    const data = await applicantsAPI.get(route.params.id)
    form.value = { ...form.value, ...data }
  }
})

async function save() {
  saving.value = true
  error.value = ''
  try {
    if (isEdit.value) {
      await applicantsAPI.update(route.params.id, form.value)
    } else {
      await applicantsAPI.create(form.value)
    }
    router.push({ name: 'Applicants' })
  } catch (e) {
    error.value = Object.values(e.response?.data || {}).flat().join(', ')
  } finally {
    saving.value = false
  }
}
</script>
