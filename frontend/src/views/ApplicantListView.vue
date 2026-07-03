<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <h2 class="text-h4">Applicants</h2>
      <v-btn color="primary" prepend-icon="mdi-plus" :to="{ name: 'ApplicantNew' }">New</v-btn>
    </div>

    <v-text-field v-model="search" label="Search by name, ID, or employment type" prepend-inner-icon="mdi-magnify" variant="outlined" density="compact" hide-details class="mb-4" @input="load" />

    <v-data-table v-if="!loading" :headers="headers" :items="applicants" :items-per-page="-1">
      <template #item.name="{ item }">
        <router-link :to="{ name: 'ApplicantDetail', params: { id: item.id } }">{{ item.name }}</router-link>
      </template>
      <template #item.monthly_income="{ item }">
        ${{ item.monthly_income?.toLocaleString() }}
      </template>
      <template #item.actions="{ item }">
        <v-icon size="small" class="mr-2" @click="$router.push({ name: 'ApplicantEdit', params: { id: item.id } })">mdi-pencil</v-icon>
        <v-icon size="small" @click="confirmDelete(item)">mdi-delete</v-icon>
      </template>
    </v-data-table>
    <v-skeleton-loader v-else type="table-row@10" />

    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card class="pa-4">
        <v-card-title class="text-h5">Delete Applicant</v-card-title>
        <v-card-text>Are you sure you want to delete <strong>{{ deleteTarget?.name }}</strong>?</v-card-text>
        <v-card-actions>
          <v-btn variant="text" @click="deleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="remove">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { applicantsAPI } from '../api/applicants'

const search = ref('')
const applicants = ref([])
const loading = ref(false)
const deleteDialog = ref(false)
const deleteTarget = ref(null)

const headers = [
  { title: 'ID', key: 'applicant_id' },
  { title: 'Name', key: 'name' },
  { title: 'Age', key: 'age' },
  { title: 'Employment', key: 'employment_type' },
  { title: 'Income', key: 'monthly_income' },
  { title: 'Actions', key: 'actions', sortable: false },
]

async function load() {
  loading.value = true
  const params = search.value ? { search: search.value } : {}
  const res = await applicantsAPI.list(params).catch(() => ({ results: [] }))
  applicants.value = res.results || res || []
  loading.value = false
}

function confirmDelete(item) {
  deleteTarget.value = item
  deleteDialog.value = true
}

async function remove() {
  if (!deleteTarget.value) return
  await applicantsAPI.delete(deleteTarget.value.id).catch(() => {})
  deleteDialog.value = false
  deleteTarget.value = null
  load()
}

onMounted(load)
</script>
