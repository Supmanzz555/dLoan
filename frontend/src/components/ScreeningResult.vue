<template>
  <div>
    <v-alert v-if="result" :color="result.recommendation === 'Proceed' ? 'green' : 'red'" variant="tonal" class="mb-4" density="compact">
      <div class="d-flex align-center">
        <v-icon :color="result.recommendation === 'Proceed' ? 'green' : 'red'" size="36" class="mr-3">{{ recIcon }}</v-icon>
        <div>
          <div class="text-h5">{{ result.recommendation }}</div>
          <div>Confidence: {{ result.confidence }}</div>
        </div>
      </div>
    </v-alert>

    <v-alert v-if="disclaimer" type="warning" variant="tonal" class="mb-4" density="compact">
      {{ disclaimer }}
    </v-alert>

    <v-list v-if="result">
      <v-list-item><v-list-item-title>Eligibility</v-list-item-title><v-list-item-subtitle>{{ result.eligibility_status }}</v-list-item-subtitle></v-list-item>
      <v-list-item><v-list-item-title>DTI Ratio</v-list-item-title><v-list-item-subtitle>{{ result.debt_to_income_ratio }}</v-list-item-subtitle></v-list-item>
      <v-list-item v-if="result.risk_flags?.length"><v-list-item-title>Risk Flags</v-list-item-title>
        <v-list-item-subtitle>
          <v-chip v-for="f in result.risk_flags" :key="f" color="error" size="small" class="mr-1">{{ f }}</v-chip>
        </v-list-item-subtitle>
      </v-list-item>
      <v-list-item v-if="result.next_action"><v-list-item-title>Next Action</v-list-item-title><v-list-item-subtitle>{{ result.next_action }}</v-list-item-subtitle></v-list-item>
    </v-list>

    <v-card v-if="result?.explanation" variant="outlined" class="mt-4">
      <v-card-title class="d-flex align-center">
        <span>Explanation</span>
        <v-spacer />
        <v-btn
          variant="text" size="small"
          :prepend-icon="showRawExp ? 'mdi-format-text' : 'mdi-code-json'"
          @click="showRawExp = !showRawExp"
        >
          {{ showRawExp ? 'Formatted' : 'Raw JSON' }}
        </v-btn>
      </v-card-title>
      <v-divider />
      <v-card-text>
        <pre v-if="showRawExp" class="text-body-2" style="white-space: pre-wrap; font-family: monospace;">{{ result.explanation }}</pre>
        <div v-else>
          <p v-for="(para, i) in cleanParagraphs" :key="i" class="mb-2 text-body-1">{{ para }}</p>
        </div>
      </v-card-text>
    </v-card>

    <v-btn
      v-if="result"
      variant="text" size="small" color="grey"
      prepend-icon="mdi-code-json"
      class="mt-2"
      @click="showFullRaw = !showFullRaw"
    >
      {{ showFullRaw ? 'Hide raw response' : 'View raw response' }}
    </v-btn>

    <v-card v-if="showFullRaw && result" variant="outlined" class="mt-2">
      <pre class="pa-4 text-caption" style="white-space: pre-wrap; font-family: monospace; max-height: 400px; overflow-y: auto;">{{ JSON.stringify(result, null, 2) }}</pre>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ result: Object })
const showRawExp = ref(false)
const showFullRaw = ref(false)

const recIcon = computed(() => {
  if (props.result?.recommendation === 'Proceed') return 'mdi-check-circle'
  if (props.result?.recommendation === 'Decline') return 'mdi-close-circle'
  return 'mdi-alert-circle'
})

const disclaimer = computed(() => {
  if (!props.result?.explanation) return ''
  const match = props.result.explanation.match(/Requires human review:.*?(\.|$)/)
  return match ? match[0] : ''
})

const cleanParagraphs = computed(() => {
  if (!props.result?.explanation) return []
  const text = props.result.explanation.replace(/\n*Requires human review:.*$/, '').trim()
  return text.split('\n').filter(Boolean)
})
</script>
