import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  // Posts
  async getAllPosts() {
    const response = await api.get('/posts')
    return response.data
  },

  async getPost(postId) {
    const response = await api.get(`/posts/${postId}`)
    return response.data
  },

  async addPostEvent(postId, event) {
    const response = await api.post(`/posts/${postId}/events`, event)
    return response.data
  },

  async deletePost(postId) {
    const response = await api.delete(`/posts/${postId}`)
    return response.data
  }
} 