import { generic_get, generic_delete, full_data_post } from '~/api'

export const state = () => ({
  pipelines: []
})

export const getters = {
  userPipelines: (state, getters, rootState) => {
    return state.pipelines.filter(
      pipeline => pipeline.user_id === rootState.auth.user.id
    )
  },
  sharedPipelines: (state, getters, rootState) => {
    return state.pipelines.filter(
      pipeline =>
        pipeline.user_id !== rootState.auth.user.id &&
        pipeline.is_shared === true
    )
  }
}

export const mutations = {
  setPipelines: (state, pipelines) => (state.pipelines = pipelines),
  addPipeline: (state, pipeline) => state.pipelines.push(pipeline),
  deletePipeline: (state, id) => {
    const index = state.pipelines.findIndex(pipeline => pipeline.id === id)
    state.pipelines.splice(index, 1)
  }
}
export const actions = {
  async fetchPipelines({ commit }) {
    try {
      const URL = '/pipeline'
      const res = await generic_get(this, URL)
      commit('setPipelines', res)
      return res
    } catch (err) {
      console.log(err)
    }
  },
  async deletePipeline({ commit }, id) {
    try {
      const URL = `/pipeline/${id}`
      await generic_delete(this, URL)
      commit('deletePipeline', id)
    } catch (err) {
      console.log(err)
    }
  },
  async addPipeline({ commit }, data) {
    try {
      // can't use generic_post here because need all of response, not just the response.data
      const URL = '/pipeline'
      const res = await full_data_post(this, URL, data)
      commit('addPipeline', data)
      return res
    } catch (err) {
      console.log(err)
    }
  }
}
