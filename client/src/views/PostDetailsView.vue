<template>
  <div>
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1>Post Details</h1>
      <router-link to="/" class="btn btn-outline-primary">Back to List</router-link>
    </div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="post" class="card mb-4">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="card-title">Post {{ postId.slice(0, 8) }}...</h5>
          <button @click="deletePost(postId)" class="btn btn-danger btn-sm">
            <i class="bi bi-trash"></i>
          </button>
        </div>
        <div class="row">
          <div v-for="(count, eventType) in post" :key="eventType" class="col-md-3 mb-3">
            <div class="card">
              <div class="card-body text-center">
                <h6 class="card-subtitle mb-2 text-muted">{{ eventType }}</h6>
                <h3 class="card-title">{{ count }}</h3>
                <button @click="addEvent(eventType)" class="btn btn-success btn-sm">
                  Add {{ eventType }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <h5 class="card-title mb-4">Event History</h5>
        <div v-if="Object.keys(chartData).length === 0" class="text-center my-5">
          <p class="text-muted">No historical data available</p>
        </div>
        <div v-else v-for="(eventType, index) in Object.keys(chartData)" :key="eventType" class="mb-5">
          <h6 class="mb-3">{{ eventType }}</h6>
          <div :id="'chart-' + index" style="height: 300px;"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import Plotly from 'plotly.js-dist'

export default {
  name: 'PostDetailsView',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      charts: {},
      chartData: {}
    }
  },
  computed: {
    ...mapState(['posts', 'historicalData']),
    ...mapGetters(['getPostById', 'getHistoricalData', 'isLoading', 'getError']),
    postId() {
      return this.id
    },
    post() {
      return this.getPostById(this.postId)
    },
    eventTypes() {
      return this.post ? Object.keys(this.post) : []
    },
    loading() {
      return this.isLoading
    },
    error() {
      return this.getError
    },
    currentHistoricalData() {
      return this.getHistoricalData(this.postId)
    }
  },
  methods: {
    ...mapActions(['fetchPost', 'deletePost', 'addPostEvent']),
    async addEvent(eventType) {
      const event = {
        post_id: this.postId,
        event_type: eventType,
        count: 1,
        total: (this.post[eventType] || 0) + 1,
        timestamp: new Date().toISOString()
      }
      await this.addPostEvent({ postId: this.postId, event })
    },
    updateCharts() {
      console.log('Updating charts with data:', this.currentHistoricalData)
      this.chartData = { ...this.currentHistoricalData }
      
      // Process for each event type
      Object.keys(this.chartData).forEach((eventType, index) => {
        const data = this.chartData[eventType] || []
        console.log(`Chart data for ${eventType}:`, data)
        
        if (data && data.length > 0) {
          try {
            const timestamps = data.map(d => d.timestamp)
            const counts = data.map(d => d.count)
            const totals = data.map(d => d.total)

            const trace1 = {
              x: timestamps,
              y: counts,
              name: 'New Events',
              type: 'bar'
            }

            const trace2 = {
              x: timestamps,
              y: totals,
              name: 'Total Events',
              type: 'scatter',
              mode: 'lines+markers'
            }

            const layout = {
              title: `${eventType} Events Over Time`,
              xaxis: {
                title: 'Time',
                type: 'date'
              },
              yaxis: {
                title: 'Count'
              },
              barmode: 'group'
            }

            const chartElement = document.getElementById(`chart-${index}`)
            if (chartElement) {
              Plotly.purge(chartElement)
              Plotly.newPlot(chartElement, [trace1, trace2], layout)
              console.log(`Chart updated for ${eventType}`)
            } else {
              console.warn(`Chart element not found for ${eventType} at index ${index}`)
            }
          } catch (error) {
            console.error(`Error updating chart for ${eventType}:`, error)
          }
        }
      })
    }
  },
  watch: {
    postId: {
      immediate: true,
      handler(newId) {
        console.log('Post ID changed to:', newId)
        this.$store.dispatch('setCurrentPost', newId)
        this.fetchPost(newId)
      }
    },
    currentHistoricalData: {
      deep: true,
      handler(newData) {
        console.log('Historical data changed:', newData)
        this.$nextTick(() => {
          this.updateCharts()
        })
      }
    }
  },
  mounted() {
    console.log('Component mounted, post ID:', this.postId)
    this.$nextTick(() => {
      this.updateCharts()
    })
  },
  updated() {
    console.log('Component updated')
  },
  beforeUnmount() {
    // Clean up charts
    Object.keys(this.charts).forEach(id => {
      if (document.getElementById(id)) {
        Plotly.purge(id)
      }
    })
    this.$store.dispatch('disconnectWebSockets')
  }
}
</script> 