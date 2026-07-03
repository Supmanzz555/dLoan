<template>
  <v-expansion-panels variant="accordion" class="mt-2">
    <v-expansion-panel title="Agent Flow" subtitle="LLM reasoning steps (intake → explanation)">
      <v-expansion-panel-text>
        <v-expansion-panels variant="accordion">
          <v-expansion-panel v-for="state in agentStates" :key="state.name" :title="state.name">
            <v-progress-linear v-if="state.loading" indeterminate />
            <v-expansion-panel-text>
              <pre class="text-body-2">{{ JSON.stringify(state.data, null, 2) }}</pre>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-expansion-panel-text>
    </v-expansion-panel>
  </v-expansion-panels>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ states: Object })
const agentStates = computed(() => {
  if (!props.states) return []
  const order = ['intake', 'document', 'eligibility', 'risk', 'recommendation', 'explanation']
  return order.map((name) => ({
    name,
    data: props.states[name] || { note: 'Not run' },
    loading: false,
  }))
})
</script>
