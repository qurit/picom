import { generic_get, generic_post } from '~/api'

export const state = () => ({
  applicationEntities: []
})

export const mutations = {
  setApplicationEntities: (state, applicationEntities) =>
    (state.applicationEntities = applicationEntities),
  addApplicationEntity: (state, applicationEntity) =>
    state.applicationEntities.push(applicationEntity)
}

export const actions = {
  async fetchApplicationEntities({ commit }) {
    try {
      const URL = '/ae'
      const res = await generic_get(this, URL)
      commit('setApplicationEntities', res)
      return res
    } catch (err) {
      console.log(err)
    }
  },
  async addApplicationEntity({ commit }, data) {
    try {
      const URL = '/ae'
      const res = await generic_post(this, URL, {
        host: data.host,
        port: data.port
      })
      commit('addApplicationEntity', res)
    } catch (err) {
      console.log(err)
    }
  }
}
