<template>
  <v-app>
    <v-slide-x-reverse-transition mode="out-in">
      <router-view />
    </v-slide-x-reverse-transition>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" :timeout="4000">
      {{ snackbar.message }}
      <template #actions>
        <v-btn variant="text" @click="snackbar.show = false">Close</v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { reactive, provide } from 'vue'

const snackbar = reactive({ show: false, message: '', color: 'error' })
provide('snackbar', snackbar)
</script>

<style>
.v-data-table .v-table-row:nth-child(even) {
  background-color: rgb(var(--v-theme-background));
}
.v-data-table .v-table-row:hover {
  background-color: rgb(var(--v-theme-primary), 0.04);
}
.v-data-table .v-table-row--active {
  background-color: rgb(var(--v-theme-primary), 0.08);
}
</style>
