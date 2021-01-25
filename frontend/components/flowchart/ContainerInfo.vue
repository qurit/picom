<template>
  <v-card height="50vh" color="#373740">
    <v-row class="ma-2">
      <v-col cols="12"> Container Name: {{ this.container.name }} </v-col>
      <v-col cols="12"> Description: {{ this.container.description }}</v-col>
      <v-col cols="12">
        Application Entity: {{ node.applicationEntity || 'N/A' }}</v-col
      >
    </v-row>
  </v-card>
</template>

<script>
export default {
  props: {
    node: {
      type: Object
    }
  },
  data() {
    return {
      container: this.node.container
    }
  }
}
</script>
