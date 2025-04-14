<template>
  <div>
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="mb-0">Social Network Posts</h1>
      <div class="d-flex">
        <div class="input-group">
          <input
            type="text"
            class="form-control"
            placeholder="Search by Post ID"
            v-model="searchTerm"
            @input="filterPosts"
          >
          <button class="btn btn-outline-secondary" type="button" @click="clearSearch">
            <i class="bi bi-x"></i> Clear
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    <div v-else-if="filteredPosts.length === 0" class="text-center my-5">
      <p class="text-muted">No posts found matching your search criteria</p>
    </div>
    <div v-else class="row">
      <div v-for="postId in filteredPosts" :key="postId" class="col-md-6 col-lg-4 mb-4">
        <div class="card">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <h5 class="card-title">Post {{ postId.slice(0, 8) }}...</h5>
              <button @click="deletePost(postId)" class="btn btn-danger btn-sm">
                <i class="bi bi-trash"></i>
              </button>
            </div>
            <div class="mb-3">
              <div v-for="(count, eventType) in posts[postId]" :key="eventType" class="d-flex justify-content-between">
                <span>{{ eventType }}:</span>
                <span class="badge bg-primary">{{ count }}</span>
              </div>
            </div>
            <div class="d-flex justify-content-end">
              <router-link :to="{ name: 'post-details', params: { id: postId }}" class="btn btn-primary">
                View Details
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

export default {
  name: 'HomeView',
  data() {
    return {
      searchTerm: '',
      filteredPosts: []
    }
  },
  computed: {
    ...mapState(['posts']),
    ...mapGetters(['isLoading', 'getError']),
    loading() {
      return this.isLoading
    },
    error() {
      return this.getError
    },
    postIds() {
      return Object.keys(this.posts)
    }
  },
  methods: {
    ...mapActions(['fetchAllPosts', 'deletePost']),
    filterPosts() {
      if (!this.searchTerm) {
        this.filteredPosts = this.postIds
        return
      }
      
      const searchTermLower = this.searchTerm.toLowerCase()
      this.filteredPosts = this.postIds.filter(postId => 
        postId.toLowerCase().includes(searchTermLower)
      )
    },
    clearSearch() {
      this.searchTerm = ''
      this.filterPosts()
    }
  },
  watch: {
    posts: {
      handler() {
        this.filterPosts()
      },
      deep: true,
      immediate: true
    }
  },
  created() {
    this.fetchAllPosts()
    this.$store.dispatch('connectWebSockets')
  },
  beforeUnmount() {
    this.$store.dispatch('disconnectWebSockets')
  }
}
</script>

<style scoped>
.input-group {
  width: 300px;
}
</style> 