<template>
  <v-card elevation="6">
    <v-toolbar color="primary accent--text" flat>
      <v-toolbar-title>
        <b
          >{{ !!containerToEdit ? 'Edit your Container' : 'Add a Container' }}
        </b></v-toolbar-title
      >
    </v-toolbar>
    <v-divider light />
    <v-form class="ma-5" ref="form">
      <v-col cols="12" md="12">
        <v-text-field
          v-model="container.containerName"
          label="Container name"
          :rules="[v => !!v || 'Container name is required']"
          required
        ></v-text-field>
      </v-col>
      <v-col cols="12" md="12">
        <v-textarea
          v-model="container.containerDescription"
          label="Description"
        ></v-textarea>
      </v-col>
      <v-row>
        <v-checkbox
          v-model="container.containerIsInput"
          label="Input"
          false-value="false"
          true-value="true"
          class="mx-10"
        />
        <v-checkbox
          v-model="container.containerIsOutput"
          label="Output"
          false-value="false"
          true-value="true"
          class="mx-10"
        />
        <v-checkbox
          v-model="container.containerIsShared"
          label="Shared"
          false-value="false"
          true-value="true"
          class="mx-10"
        />
      </v-row>
      <v-file-input
        v-model="file"
        :label="container.filename"
        @change="updateDockerFile"
        prepend-icon="mdi-docker"
      />
      <v-row justify="center">
        <v-btn
          :disabled="this.isDisabled"
          @click="submit"
          color="confirm"
          class="ma-4"
          text
        >
          {{ !!containerToEdit ? 'Save Edits' : 'Add Container' }}
        </v-btn>
      </v-row>
    </v-form>
  </v-card>
</template>

<script>
export default {
  props: {
    containerToEdit: {
      type: Object,
      default: () => {
        return undefined
      }
    }
  },
  data() {
    return {
      file: '',
      container: {
        containerId: '',
        filename: '',
        containerName: '',
        containerDescription: '',
        containerIsInput: false,
        containerIsOutput: false,
        containerIsShared: false
      }
    }
  },
  created() {
    this.populate()
  },
  computed: {
    // disables button if no name or dockerfile for new container
    isDisabled: function() {
      return !!this.containerToEdit
        ? false
        : !(this.container.containerName && this.file)
    }
  },
  methods: {
    populate() {
      if (!!this.containerToEdit) {
        // getting the values for the existing container
        this.container = JSON.parse(JSON.stringify(this.containerToEdit))
      } else {
        // default values for adding a new container
        this.container.containerId = ''
        this.container.filename = ''
        this.container.containerName = ''
        this.container.containerDescription = ''
        this.container.containerIsInput = false
        this.container.containerIsOutput = false
        this.container.containerIsShared = false
      }
    },
    readFile(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.onload = () => resolve(reader.result)
        reader.onerror = reject
        reader.readAsArrayBuffer(file)
      })
    },
    updateDockerFile(file) {
      this.file = file
    },
    async submit() {
      const config = { headers: { 'Content-Type': 'multipart/form-data' } }
      const formData = new FormData()
      formData.append('name', this.container?.containerName)
      formData.append('is_input_container', this.container.containerIsInput)
      formData.append('is_output_container', this.container.containerIsOutput)
      formData.append('is_shared', this.container.containerIsShared)
      if (this.file) {
        const f = await this.readFile(this.file)
        formData.append('file', new Blob([f]))
        formData.append('filename', this.file.name)
      }
      if (!!this.container.containerDescription) {
        formData.append('description', this.container.containerDescription)
      }
      if (!!this.containerToEdit) {
        await this.$store.dispatch('containers/updateContainer', {
          id: this.container.containerId,
          data: formData
        })
      } else {
        await this.$store
          .dispatch('containers/addContainer', formData)
          .then(() => {
            this.$refs.form.reset()
            this.container.containerIsInput = false
            this.container.containerIsOutput = false
            this.container.containerIsShared = false
          })
      }
      this.$emit('closeDialog')
      this.$toaster.toastSuccess('Container saved!')
    }
  }
}
</script>
