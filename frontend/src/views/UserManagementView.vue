<template>
  <div>
    <div class="d-flex justify-space-between align-center mb-4">
      <h2 class="text-h4">User Management</h2>
      <v-btn color="primary" prepend-icon="mdi-plus" @click="showCreate = true">New User</v-btn>
    </div>

    <v-alert v-if="msg" :type="msg.type" closable class="mb-3">{{ msg.text }}</v-alert>

    <v-data-table :headers="headers" :items="users" :items-per-page="-1" :loading="loading">
      <template #item.role="{ item }">
        <v-chip v-if="item.is_super_admin" color="orange" size="small" class="mr-1">Super Admin</v-chip>
        <v-chip v-else-if="item.role === 'admin'" color="primary" size="small">Admin</v-chip>
        <v-chip v-else-if="item.role === 'reviewer'" color="purple" size="small">Reviewer</v-chip>
        <v-chip v-else size="small">Officer</v-chip>
      </template>
      <template #item.is_active="{ item }">
        <v-chip :color="item.is_active ? 'green' : 'red'" size="small">{{ item.is_active ? 'Active' : 'Disabled' }}</v-chip>
      </template>
      <template #item.actions="{ item }">
        <v-icon
          v-if="canEdit(item)"
          size="small" class="mr-2"
          @click="editUser(item)"
        >mdi-pencil</v-icon>
        <v-icon
          v-if="canToggle(item)"
          size="small"
          @click="toggleActive(item)"
        >{{ item.is_active ? 'mdi-account-off' : 'mdi-account-check' }}</v-icon>
        <span v-if="!canEdit(item) && !canToggle(item)" class="text-grey text-caption">Protected</span>
      </template>
    </v-data-table>

    <v-dialog v-model="showCreate" max-width="500">
      <v-card class="pa-4" title="Create User">
        <v-text-field v-model="newUser.username" label="Username" variant="outlined" />
        <v-text-field v-model="newUser.email" label="Email" variant="outlined" />
        <v-text-field v-model="newUser.password" label="Password" type="password" variant="outlined" />
        <v-select v-model="newUser.role" :items="['officer','reviewer','admin']" label="Role" variant="outlined" />
        <v-checkbox v-if="auth.isSuperAdmin" v-model="newUser.is_super_admin" label="Super Admin" hide-details />
        <v-card-actions>
          <v-btn variant="text" @click="showCreate = false">Cancel</v-btn>
          <v-btn color="primary" @click="createUser">Create</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showEdit" max-width="500">
      <v-card class="pa-4" title="Edit User">
        <v-text-field v-if="auth.isSuperAdmin" v-model="editForm.email" label="Email" variant="outlined" />
        <v-select v-model="editForm.role" :items="['officer','reviewer','admin']" label="Role" variant="outlined" />
        <v-text-field v-if="auth.isSuperAdmin" v-model="editForm.password" label="New Password (leave blank to keep)" type="password" variant="outlined" />
        <v-checkbox v-if="auth.isSuperAdmin" v-model="editForm.is_super_admin" label="Super Admin" hide-details />
        <v-card-actions>
          <v-btn variant="text" @click="showEdit = false">Cancel</v-btn>
          <v-btn color="primary" @click="updateUser">Save</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authAPI } from '../api/auth'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const users = ref([])
const loading = ref(false)
const msg = ref(null)
const showCreate = ref(false)
const showEdit = ref(false)
const editUserId = ref(null)

const newUser = ref({ username: '', email: '', password: '', role: 'officer', is_super_admin: false })
const editForm = ref({ email: '', role: '', is_super_admin: false, password: '' })

const headers = [
  { title: 'Username', key: 'username' },
  { title: 'Email', key: 'email' },
  { title: 'Role', key: 'role' },
  { title: 'Status', key: 'is_active' },
  { title: 'Joined', key: 'date_joined' },
  { title: 'Actions', key: 'actions', sortable: false },
]

function canEdit(item) {
  if (item.is_super_admin && !auth.isSuperAdmin) return false
  return true
}

function canToggle(item) {
  if (item.is_super_admin && !auth.isSuperAdmin) return false
  if (item.id === auth.user?.id) return false
  return true
}

async function load() {
  loading.value = true
  const res = await authAPI.listUsers().catch(() => [])
  users.value = res || []
  loading.value = false
}

async function createUser() {
  try {
    await authAPI.createUser(newUser.value)
    showCreate.value = false
    newUser.value = { username: '', email: '', password: '', role: 'officer', is_super_admin: false }
    msg.value = { type: 'success', text: 'User created' }
    load()
  } catch (e) {
    msg.value = { type: 'error', text: JSON.stringify(e.response?.data || {}) }
  }
}

function editUser(user) {
  editUserId.value = user.id
  editForm.value = { email: user.email, role: user.role, is_super_admin: user.is_super_admin, password: '' }
  showEdit.value = true
}

async function updateUser() {
  try {
    const payload = { ...editForm.value }
    if (!payload.password) delete payload.password
    await authAPI.updateUser(editUserId.value, payload)
    showEdit.value = false
    msg.value = { type: 'success', text: 'User updated' }
    load()
  } catch (e) {
    msg.value = { type: 'error', text: 'Update failed' }
  }
}

async function toggleActive(user) {
  if (user.is_active) {
    await authAPI.disableUser(user.id)
    msg.value = { type: 'info', text: `${user.username} disabled` }
  } else {
    await authAPI.updateUser(user.id, { is_active: true })
    msg.value = { type: 'info', text: `${user.username} enabled` }
  }
  load()
}

onMounted(load)
</script>
