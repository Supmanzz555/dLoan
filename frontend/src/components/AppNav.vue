<template>
  <v-navigation-drawer
    v-model="drawer"
    :rail="rail"
    :permanent="!isMobile"
    :temporary="isMobile"
    @click.stop="rail = false"
  >
    <template #prepend>
      <v-list-item class="px-2 py-1">
        <v-list-item-title class="text-body-2 font-weight-bold">{{ auth.user?.username }}</v-list-item-title>
        <template #append>
          <v-chip v-if="auth.isSuperAdmin" color="orange" size="x-small">Super</v-chip>
          <v-chip v-else-if="auth.user?.role === 'reviewer'" color="purple" size="x-small">Reviewer</v-chip>
          <v-chip v-else-if="auth.isAdmin" color="primary" size="x-small">Admin</v-chip>
        </template>
      </v-list-item>
      <v-divider />
    </template>
    <v-list density="compact" nav color="primary">
      <v-list-item prepend-icon="mdi-view-dashboard" title="Dashboard" :to="{ name: 'Dashboard' }" @click="closeOnMobile" />
      <v-list-item prepend-icon="mdi-account-multiple" title="Applicants" :to="{ name: 'Applicants' }" @click="closeOnMobile" />
      <v-list-item prepend-icon="mdi-account-search" title="Screen" :to="{ name: 'Screen' }" @click="closeOnMobile" />
      <v-list-item prepend-icon="mdi-history" title="History" :to="{ name: 'History' }" @click="closeOnMobile" />
    </v-list>

    <template #append>
      <v-list density="compact" nav color="primary">
        <v-list-item prepend-icon="mdi-account-cog" title="Profile" :to="{ name: 'Profile' }" @click="closeOnMobile" />
        <v-list-item
          v-if="auth.isAdmin"
          prepend-icon="mdi-shield-account"
          title="Users"
          :to="{ name: 'UserManagement' }"
          @click="closeOnMobile"
        >
          <template #append>
            <v-chip v-if="auth.isSuperAdmin" color="orange" size="x-small">Super</v-chip>
          </template>
        </v-list-item>
        <v-list-item
          v-if="auth.isAdmin"
          prepend-icon="mdi-clipboard-list"
          title="Activity"
          :to="{ name: 'ActivityLog' }"
          @click="closeOnMobile"
        />
        <v-divider />
        <v-list-item
          :prepend-icon="isDark ? 'mdi-weather-night' : 'mdi-weather-sunny'"
          :title="isDark ? 'Dark' : 'Light'"
          @click="toggleTheme"
        />
        <v-list-item prepend-icon="mdi-logout" title="Logout" @click="logout" />
      </v-list>
    </template>
  </v-navigation-drawer>
  <v-app-bar v-if="isMobile" density="compact" color="primary">
    <v-app-bar-nav-icon @click="drawer = !drawer" />
    <v-app-bar-title>dLoan</v-app-bar-title>
    <v-spacer />
    <v-btn :icon="isDark ? 'mdi-weather-night' : 'mdi-weather-sunny'" variant="text" @click="toggleTheme" />
  </v-app-bar>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDisplay } from 'vuetify'
import { useTheme } from 'vuetify'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const theme = useTheme()
const { mobile } = useDisplay()
const isMobile = computed(() => mobile.value)

const drawer = ref(!isMobile.value)
const rail = ref(true)

function closeOnMobile() {
  if (isMobile.value) drawer.value = false
}

watch(isMobile, (val) => {
  rail.value = !val
  drawer.value = !val
})

const isDark = computed(() => theme.global.name.value === 'dark')

function toggleTheme() {
  const next = isDark.value ? 'light' : 'dark'
  theme.global.name.value = next
  localStorage.setItem('theme', next)
}

function logout() {
  auth.logout()
  router.push('/login')
}
</script>
