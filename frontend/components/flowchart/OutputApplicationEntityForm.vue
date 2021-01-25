<template>
  <v-card class="overflow-x-hidden" width="600">
    <v-card-title>
      Add an Application Entity source for your pipelines</v-card-title
    >
    <v-row>
      <v-col cols="6">
        <v-text-field
          v-model="host"
          label="Host Address"
          :rules="[v => !!v || 'A Host Address is required']"
          required
        />
      </v-col>
      <v-col cols="6">
        <v-text-field
          v-model.number="port"
          label="Port"
          :rules="[rules.validateNumber]"
          required
        />
      </v-col>
      <v-col cols="12">
        <v-text-field
          v-model="ae_title"
          label="AE Title"
          :rules="[v => !!v || 'A AE Title is required']"
          required
        />
      </v-col>
    </v-row>
    <v-card-actions>
      <v-spacer />
      <v-btn
        :disabled="!this.isFormValid"
        @click="submit"
        color="confirm"
        class="ma-4"
        text
      >
        Add Application Entity
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  name: 'OutputApplicationEntityForm',
  data: () => ({
    isFormValid: false,
    rules: {
      validateNumber(value) {
        return Number.isInteger(value) || 'Port must be a number'
      }
    },
    host: '',
    port: '',
    ae_title: null
  }),
  methods: {
    async submit() {
      this.$store.dispatch('applicationEntity/addApplicationEntity', {
        host: this.host,
        port: this.port
      })
      this.$refs.form.reset()
      this.$emit('closeDialog')
    }
  },
  computed: {
    isDisabled: ctx => !ctx.host || !ctx.port || !ctx.ae_title
  }
}
</script>
