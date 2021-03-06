<template>
  <v-card elevation="6">
    <v-toolbar color="primary accent--text" flat>
      <v-toolbar-title><b>Settings</b></v-toolbar-title>
    </v-toolbar>
    <v-form v-model="isFormValid">
      <v-text-field
        class="mx-2"
        v-model="aeTitle"
        :rules="[validateAETitle]"
        counter
        :prefix="`Your AE Title is: ${$store.state.config.USER_AE_PREFIX}`"
        prepend-icon="mdi-access-point"
      />
    </v-form>
    <v-divider class="my-3" light />
    <v-select
      multiple
      class="mx-2"
      hint="Choose which Application Entities can send to you"
      persistent-hint
      :items="destinations"
      item-text="full_name"
      return-object
      label="Allowed Application Entities"
      v-model="permittedAEs"
      chips
      clearable
      prepend-icon="mdi-access-point-check"
      @change="didChangeAE = true"
    >
    </v-select>
    <v-row justify="center" align="center">
      Add an Application Entity
      <v-icon-btn add @click="destinationDialog = true" />
    </v-row>
    <v-divider class="my-3" light />
    <v-card-actions class="justify-center">
      <v-btn
        @click="submit"
        text
        color="confirm"
        :disabled="!(didEdit && isFormValid)"
        >Save Changes</v-btn
      >
    </v-card-actions>
    <v-dialog v-model="destinationDialog" max-width="900px" min-height="600px">
      <OutputDestinationForm @closeDialog="destinationDialog = false" />
    </v-dialog>
  </v-card>
</template>

<script>
import { mapState } from 'vuex'
import { generic_get, generic_post } from '~/api'
import { OutputDestinationForm } from '~/components/flowchart'
import { validateAETitle } from '~/utilities/validationRules'

export default {
  components: {
    OutputDestinationForm
  },
  data() {
    return {
      destinationDialog: false,
      isFormValid: false,
      didChangeAE: false,
      permittedAEs: [],
      aeTitle: '',
      currentAETitle: ''
    }
  },
  computed: {
    ...mapState('destination', ['destinations']),
    ...mapState('auth', ['user']),
    didEdit() {
      return this.currentAETitle !== this.aeTitle || this.didChangeAE
    }
  },
  methods: {
    validateAETitle,
    async getUserInfo() {
      const URL = '/user/me'
      const { ae_title } = await generic_get(this, URL)
      this.aeTitle = ae_title
      this.currentAETitle = ae_title
    },
    async getUserPermittedAEs() {
      const URL = '/user/permitted-ae'
      const userPermittedDestinations = await generic_get(this, URL)
      userPermittedDestinations.forEach(permitted => {
        this.permittedAEs.push(permitted.destination)
      })
    },
    async saveUserAETitle() {
      const URL = `/user/${this.user.id}`
      const payload = { ae_title: this.aeTitle }
      this.ae_title = await generic_put(this, URL, payload)
    },
    async savePermittedAETitles() {
      const URL = '/user/permitted-ae'
      const payload = {
        destinations: this.permittedAEs
      }
      await generic_post(this, URL, payload)
    },
    submit() {
      try {
        if (this.user.ae_title !== this.ae_title) {
          this.saveUserAETitle()
        }

        this.savePermittedAETitles()
        this.$toaster.toastSuccess('Changes saved!')
      } catch (e) {
        this.$toaster.toastError('Could not save changes')
      }
    }
  },
  created() {
    this.$store.dispatch('destination/fetchDestinations')
    this.getUserInfo()
    this.getUserPermittedAEs()
  }
}
</script>
