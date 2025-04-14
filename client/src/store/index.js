import { createStore } from 'vuex'
import api from '../services/api'

export default createStore({
  state: {
    posts: {},
    historicalData: {},
    wsOverview: null,
    wsDetails: null,
    currentPostId: null,
    loading: false,
    error: null
  },
  mutations: {
    SET_POSTS(state, posts) {
      state.posts = posts
    },
    // eslint-disable-next-line no-unused-vars
    UPDATE_POST(state, { postId, eventType, count, total }) {
      if (!state.posts[postId]) {
        state.posts[postId] = {}
      }
      state.posts[postId][eventType] = total
    },
    SET_HISTORICAL_DATA(state, { postId, data }) {
      state.historicalData = {
        ...state.historicalData,
        [postId]: data
      }
      console.log('Historical data updated:', state.historicalData)
    },
    UPDATE_HISTORICAL_DATA(state, { postId, eventType, data }) {
      if (!state.historicalData[postId]) {
        state.historicalData[postId] = {}
      }
      state.historicalData[postId][eventType] = data
      console.log('Historical data updated for event type:', eventType, data)
    },
    SET_WS_OVERVIEW(state, ws) {
      state.wsOverview = ws
    },
    SET_WS_DETAILS(state, ws) {
      state.wsDetails = ws
    },
    SET_CURRENT_POST_ID(state, postId) {
      state.currentPostId = postId
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    },
    REMOVE_POST(state, postId) {
      delete state.posts[postId]
      delete state.historicalData[postId]
    }
  },
  actions: {
    async fetchAllPosts({ commit }) {
      try {
        commit('SET_LOADING', true)
        const posts = await api.getAllPosts()
        const postsMap = posts.reduce((acc, post) => {
          acc[post.post_id] = post.events
          return acc
        }, {})
        commit('SET_POSTS', postsMap)
      } catch (error) {
        commit('SET_ERROR', error.message)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async fetchPost({ commit }, postId) {
      try {
        commit('SET_LOADING', true)
        const post = await api.getPost(postId)
        commit('SET_HISTORICAL_DATA', {
          postId,
          data: post.historical_data
        })
      } catch (error) {
        commit('SET_ERROR', error.message)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async addPostEvent({ commit }, { postId, event }) {
      try {
        commit('SET_LOADING', true)
        await api.addPostEvent(postId, event)
      } catch (error) {
        commit('SET_ERROR', error.message)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async deletePost({ commit }, postId) {
      try {
        commit('SET_LOADING', true)
        await api.deletePost(postId)
        commit('REMOVE_POST', postId)
      } catch (error) {
        commit('SET_ERROR', error.message)
      } finally {
        commit('SET_LOADING', false)
      }
    },

    connectWebSockets({ commit, state }) {
      // Disconnect existing WebSockets first
      if (state.wsOverview) {
        state.wsOverview.close()
      }
      if (state.wsDetails) {
        state.wsDetails.close()
      }

      // Connect to overview WebSocket
      const wsOverview = new WebSocket('ws://localhost:8000/ws/overview')
      wsOverview.onmessage = (event) => {
        const data = JSON.parse(event.data)
        console.log('Overview WS received:', data)
        if (data.type === 'initial') {
          commit('SET_POSTS', data.data.posts.reduce((acc, post) => {
            acc[post.post_id] = post.event_types
            return acc
          }, {}))
        } else if (data.type === 'update') {
          commit('UPDATE_POST', {
            postId: data.data.post_id,
            eventType: data.data.event_type,
            count: data.data.count,
            total: data.data.total
          })
        } else if (data.type === 'delete') {
          commit('REMOVE_POST', data.data.post_id)
        }
      }
      wsOverview.onerror = (error) => {
        console.error('Overview WebSocket error:', error)
        commit('SET_ERROR', 'WebSocket connection error')
      }
      commit('SET_WS_OVERVIEW', wsOverview)

      // Connect to details WebSocket if we have a current post
      if (state.currentPostId) {
        const wsDetails = new WebSocket(`ws://localhost:8000/ws/details/${state.currentPostId}`)
        wsDetails.onmessage = (event) => {
          const data = JSON.parse(event.data)
          console.log('Details WS received:', data)
          if (data.type === 'initial') {
            commit('SET_HISTORICAL_DATA', {
              postId: data.data.post_id,
              data: data.data.historical_data
            })
          } else if (data.type === 'update') {
            commit('UPDATE_POST', {
              postId: data.data.post_id,
              eventType: data.data.event_type,
              count: data.data.count,
              total: data.data.total
            })
            commit('UPDATE_HISTORICAL_DATA', {
              postId: data.data.post_id,
              eventType: data.data.event_type,
              data: data.data.historical_data
            })
          }
        }
        wsDetails.onerror = (error) => {
          console.error('Details WebSocket error:', error)
          commit('SET_ERROR', 'WebSocket connection error')
        }
        commit('SET_WS_DETAILS', wsDetails)
      }
    },

    disconnectWebSockets({ state }) {
      if (state.wsOverview) {
        state.wsOverview.close()
      }
      if (state.wsDetails) {
        state.wsDetails.close()
      }
    },

    setCurrentPost({ commit, dispatch }, postId) {
      commit('SET_CURRENT_POST_ID', postId)
      dispatch('connectWebSockets')
    }
  },
  getters: {
    getPostById: (state) => (id) => state.posts[id],
    getHistoricalDataByType: (state) => (postId, eventType) => 
      state.historicalData[postId]?.[eventType] || [],
    getHistoricalData: (state) => (postId) => state.historicalData[postId] || {},
    isLoading: (state) => state.loading,
    getError: (state) => state.error
  }
}) 