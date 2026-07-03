<template>
  <v-layout>
    <AppNav />
    <v-main>
      <v-container fluid class="pa-4 pa-md-6">
        <router-view />
      </v-container>
    </v-main>
  </v-layout>
</template>

<script setup>
import { useDisplay } from 'vuetify'
import AppNav from '../components/AppNav.vue'
</script>
