<template>
  <div>
    <h2 class="text-h4 mb-4">Dashboard</h2>

    <template v-if="loading">
      <v-row>
        <v-col v-for="i in 4" :key="i" cols="6" md="3">
          <v-skeleton-loader type="card" />
        </v-col>
      </v-row>
      <v-row class="mt-4">
        <v-col cols="12" md="6"><v-skeleton-loader type="card" /></v-col>
        <v-col cols="12" md="6"><v-skeleton-loader type="card" /></v-col>
      </v-row>
      <v-skeleton-loader type="card" class="mt-4" />
    </template>

    <template v-else>
      <v-row>
        <v-col cols="6" md="3">
          <v-card class="border-t-primary">
            <v-card-text class="d-flex align-center pa-4">
              <v-avatar color="primary" variant="tonal" size="48" class="mr-3">
                <v-icon color="primary">mdi-credit-search</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ data.total }}</div>
                <div class="text-caption text-grey">Total Screenings</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card class="border-t-green">
            <v-card-text class="d-flex align-center pa-4">
              <v-avatar color="green" variant="tonal" size="48" class="mr-3">
                <v-icon color="green">mdi-thumb-up</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ data.agreement_pct }}%</div>
                <div class="text-caption text-grey">AI Agreement</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card class="border-t-orange">
            <v-card-text class="d-flex align-center pa-4">
              <v-avatar color="orange" variant="tonal" size="48" class="mr-3">
                <v-icon color="orange">mdi-account-edit</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ data.overrides_count }}</div>
                <div class="text-caption text-grey">Overrides</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="6" md="3">
          <v-card class="border-t-grey">
            <v-card-text class="d-flex align-center pa-4">
              <v-avatar color="grey" variant="tonal" size="48" class="mr-3">
                <v-icon color="grey">mdi-comment-text</v-icon>
              </v-avatar>
              <div>
                <div class="text-h5 font-weight-bold">{{ data.total_feedback }}</div>
                <div class="text-caption text-grey">Feedback</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="mt-4">
        <v-col cols="12" md="6">
          <v-card title="By Outcome">
            <v-card-text>
              <v-list v-if="Object.keys(data.by_outcome).length">
                <v-list-item v-for="(count, outcome) in data.by_outcome" :key="outcome">
                  <template #prepend>
                    <v-icon :color="outcome === 'Proceed' ? 'green' : 'red'">mdi-circle</v-icon>
                  </template>
                  <v-list-item-title>{{ outcome }}</v-list-item-title>
                  <template #append>
                    <v-chip>{{ count }}</v-chip>
                  </template>
                </v-list-item>
              </v-list>
              <div v-else class="text-grey text-center pa-4">No data</div>
            </v-card-text>
          </v-card>
        </v-col>

        <v-col cols="12" md="6">
          <v-card title="Top Risk Flags">
            <v-card-text>
              <div v-if="data.top_risk_flags.length" class="d-flex flex-column ga-3">
                <div v-for="[flag, count] in data.top_risk_flags" :key="flag">
                  <div class="d-flex justify-space-between text-body-2 mb-1">
                    <span>{{ flag }}</span>
                    <span class="font-weight-medium">{{ count }}</span>
                  </div>
                  <v-progress-linear
                    :model-value="(count / maxFlag) * 100"
                    color="error"
                    height="8"
                    rounded
                  />
                </div>
              </div>
              <div v-else class="text-grey text-center pa-4">No risk flags</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-card class="mt-4">
        <v-tabs v-model="recentTab" color="primary" @update:model-value="loadRecent">
          <v-tab value="all">All</v-tab>
          <v-tab value="feedback">With Feedback</v-tab>
          <v-tab value="agreed">AI Agreed</v-tab>
          <v-tab value="overrides">Overrides</v-tab>
        </v-tabs>
        <v-divider />
        <v-card-text>
          <v-list v-if="data.recent.length">
            <v-list-item v-for="s in data.recent" :key="s.job_id" @click="viewScreening(s)" style="cursor: pointer">
              <v-list-item-title>#{{ s.job_id }}</v-list-item-title>
              <v-list-item-subtitle>
                {{ s.result_data?.recommendation }} — by {{ s.initiated_by__username || '?' }}
                <v-chip v-if="s.has_feedback" :color="s.feedback_correct ? 'green' : 'red'" size="x-small" class="ml-1">
                  {{ s.feedback_correct ? 'Agreed' : 'Override' }}
                </v-chip>
                — {{ new Date(s.created_at).toLocaleString() }}
              </v-list-item-subtitle>
            </v-list-item>
          </v-list>
          <div v-else class="text-grey text-center pa-4">No screenings match this filter</div>
        </v-card-text>
      </v-card>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardAPI } from '../api/dashboard'

const data = ref({
  total: 0, by_outcome: {}, by_status: {}, agreement_pct: 0,
  overrides_count: 0, top_risk_flags: [], recent: [], total_feedback: 0,
})
const loading = ref(false)
const recentTab = ref('all')
const router = useRouter()

const maxFlag = computed(() => {
  if (!data.value.top_risk_flags.length) return 1
  return Math.max(...data.value.top_risk_flags.map(([, c]) => c))
})

async function loadRecent() {
  data.value.recent = []
  const res = await dashboardAPI.summary({ recent: recentTab.value })
  data.value.recent = res.recent || []
}

function viewScreening(s) {
  router.push({ name: 'Screen', query: { jobId: s.job_id } })
}

onMounted(async () => {
  loading.value = true
  try {
    data.value = await dashboardAPI.summary({ recent: 'all' })
  } catch (e) {
    console.error('Dashboard load failed:', e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.border-t-primary { border-top: 3px solid rgb(var(--v-theme-primary)); }
.border-t-green { border-top: 3px solid #43A047; }
.border-t-orange { border-top: 3px solid #FF8F00; }
.border-t-grey { border-top: 3px solid #9E9E9E; }
</style>
