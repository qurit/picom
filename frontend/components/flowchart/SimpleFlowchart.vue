<template>
  <div>
    <div
      class="flowchart-container"
      @mousemove="handleMove"
      @mouseup="handleUp"
      @mousedown="handleDown"
    >
      <svg width="100%" height="100%">
        <FlowchartLink
          v-bind.sync="link"
          v-for="(link, index) in lines"
          :key="`link${index}`"
          @deleteLink="linkDelete(link.id)"
        ></FlowchartLink>
      </svg>
      <slot />
      <FlowchartNode
        v-bind.sync="node"
        :scene.sync="scene"
        v-for="(node, index) in scene.nodes"
        :key="`node${index}`"
        :options="nodeOptions"
        :colors="colors.container"
        :canEdit="canEdit"
        @setApplicationEntity="setApplicationEntities"
        @linkingStart="linkingStart(node.id)"
        @linkingStop="linkingStop(node.id)"
        @nodeSelected="nodeSelected(node.id, $event)"
        @deleteNode="deleteNode(node.id)"
      >
      </FlowchartNode>
    </div>
  </div>
</template>

<script>
import FlowchartLink from './FlowchartLink.vue'
import FlowchartNode from './FlowchartNode.vue'
import { getMousePosition } from './position'
import { generic_post } from '~/api'

export default {
  name: 'VueFlowchart',
  components: { FlowchartLink, FlowchartNode },
  props: {
    scene: {
      type: Object,
      default: () => ({
        centerX: 1024,
        scale: 1,
        centerY: 140,
        nodes: [],
        links: []
      })
    },
    height: {
      type: Number,
      default: 400
    },
    id: {
      type: Number
    },
    colors: {
      type: Object,
      default: () => ({
        container: undefined
      })
    },
    canEdit: {
      type: Boolean
    }
  },
  data: () => ({
    savedNodes: [],
    savedLinks: [],
    action: {
      linking: false,
      dragging: false,
      scrolling: false,
      selected: 0
    },
    mouse: {
      x: 0,
      y: 0,
      lastX: 0,
      lastY: 0
    },
    draggingLink: null,
    rootDivOffset: {
      top: 0,
      left: 0
    },
    pipelineNodeApplicationEntities: []
  }),
  computed: {
    nodeOptions: ctx => ({
      centerY: ctx.scene.centerY,
      centerX: ctx.scene.centerX,
      scale: ctx.scene.scale,
      offsetTop: ctx.rootDivOffset.top,
      offsetLeft: ctx.rootDivOffset.left,
      selected: ctx.action.selected
    }),
    lines() {
      const lines = this.scene.links.map(link => {
        const fromNode = this.findNodeWithID(link.from)
        const toNode = this.findNodeWithID(link.to)
        let x, y, cy, cx, ex, ey
        x = this.scene.centerX + fromNode?.x
        y = this.scene.centerY + fromNode?.y
        ;[cx, cy] = this.getPortPosition('bottom', x, y)
        x = this.scene.centerX + toNode?.x
        y = this.scene.centerY + toNode?.y
        ;[ex, ey] = this.getPortPosition('top', x, y)
        return {
          start: [cx, cy],
          end: [ex, ey],
          id: link.id
        }
      })
      if (this.draggingLink) {
        let x, y, cy, cx
        const fromNode = this.findNodeWithID(this.draggingLink.from)
        x = this.scene.centerX + fromNode.x
        y = this.scene.centerY + fromNode.y
        ;[cx, cy] = this.getPortPosition('bottom', x, y)
        // push temp dragging link, mouse cursor postion = link end postion
        lines.push({
          start: [cx, cy],
          end: [this.draggingLink.mx, this.draggingLink.my]
        })
      }
      return lines
    }
  },
  mounted() {
    this.rootDivOffset.top = this.$el ? this.$el.offsetTop : 0
    this.rootDivOffset.left = this.$el ? this.$el.offsetLeft : 0
  },
  methods: {
    setApplicationEntities(applicationEntity) {
      const index = this.pipelineNodeApplicationEntities.findIndex(
        pipelineApplicationEntity =>
          pipelineApplicationEntity.pipelineNodeId ===
          applicationEntity.pipelineNodeId
      )
      if (index >= 0) {
        this.pipelineNodeApplicationEntities.splice(index, 1)
      }
      this.pipelineNodeApplicationEntities.push(applicationEntity)
    },
    findNodeWithID(id) {
      return this.scene.nodes.find(item => id === item.id)
    },
    getPortPosition(type, x, y) {
      if (type === 'top') {
        return [x + 100, y]
      } else if (type === 'bottom') {
        return [x + 100, y + 170] // TODO: Make dynamic
      }
    },
    linkingStart(index) {
      this.action.linking = true
      this.draggingLink = {
        from: index,
        mx: 0,
        my: 0
      }
    },
    linkingStop(index) {
      // add new Link
      if (this.draggingLink && this.draggingLink.from !== index) {
        // check link existence
        const existed = this.scene.links.find(link => {
          return link.from === this.draggingLink.from && link.to === index
        })
        if (!existed) {
          let maxID = Math.max(
            0,
            ...this.scene.links.map(link => {
              return link.id
            })
          )
          const newLink = {
            id: maxID + 1,
            from: this.draggingLink.from,
            to: index
          }
          this.scene.links.push(newLink)
          this.$emit('linkAdded', newLink)
        }
      }
      this.draggingLink = null
    },
    linkDelete(id) {
      const deletedLink = this.scene.links.find(item => {
        return item.id === id
      })
      if (deletedLink) {
        this.scene.links = this.scene.links.filter(item => {
          return item.id !== id
        })
        this.$emit('linkBreak', deletedLink)
      }
    },
    nodeSelected(id, e) {
      this.action.dragging = id
      this.action.selected = id
      this.$emit('nodeClick', id)
      this.mouse.lastX =
        e.pageX || e.clientX + document.documentElement.scrollLeft
      this.mouse.lastY =
        e.pageY || e.clientY + document.documentElement.scrollTop
    },
    handleMove(e) {
      if (this.action.linking) {
        ;[this.mouse.x, this.mouse.y] = getMousePosition(this.$el, e)
        this.draggingLink.mx = this.mouse.x
        this.draggingLink.my = this.mouse.y
      }

      if (this.action.dragging) {
        this.mouse.x =
          e.pageX || e.clientX + document.documentElement.scrollLeft
        this.mouse.y = e.pageY || e.clientY + document.documentElement.scrollTop

        let diffX = this.mouse.x - this.mouse.lastX
        let diffY = this.mouse.y - this.mouse.lastY
        this.mouse.lastX = this.mouse.x
        this.mouse.lastY = this.mouse.y
        this.moveSelectedNode(diffX, diffY)
      }

      if (this.action.scrolling) {
        ;[this.mouse.x, this.mouse.y] = getMousePosition(this.$el, e)

        let diffX = this.mouse.x - this.mouse.lastX
        let diffY = this.mouse.y - this.mouse.lastY
        this.mouse.lastX = this.mouse.x
        this.mouse.lastY = this.mouse.y
        this.scene.centerX += diffX
        this.scene.centerY += diffY
      }
    },
    handleUp(e) {
      const target = e.target
      if (this.$el.contains(target)) {
        if (
          typeof target.className !== 'string' ||
          target.className.indexOf('node-input') < 0
        ) {
          this.draggingLink = null
        }
      }
      this.action.linking = false
      this.action.dragging = null
      this.action.scrolling = false
    },
    handleDown(e) {
      const target = e.target
      if (
        (target === this.$el || target.matches('svg, svg *')) &&
        e.which === 1
      ) {
        this.action.scrolling = true
        ;[this.mouse.lastX, this.mouse.lastY] = getMousePosition(this.$el, e)
        this.action.selected = null // deselectAll
      }

      this.$emit('canvasClick', e)
    },
    moveSelectedNode(dx, dy) {
      let index = this.scene.nodes.findIndex(
        item => item.id === this.action.dragging
      )
      let left = this.scene.nodes[index].x + dx / this.scene.scale
      let top = this.scene.nodes[index].y + dy / this.scene.scale

      this.$set(
        this.scene.nodes,
        index,
        Object.assign(this.scene.nodes[index], {
          x: left,
          y: top
        })
      )
    },
    deleteNode(id) {
      this.scene.nodes = this.scene.nodes.filter(node => node.id !== id)
      this.scene.links = this.scene.links.filter(
        link => link.from !== id && link.to !== id
      )
    },
    async savePipeline() {
      this.savedNodes = this.scene.nodes
      this.savedLinks = this.scene.links
      var nodeArray = []
      var linkArray = []
      this.savedNodes.forEach(node => {
        const newPipelineNode = {
          node_id: node.id,
          container_id: node.container_id,
          x: node.x,
          y: node.y,
          container_is_input: node.container_is_input,
          container_is_output: node.container_is_output
        }
        // if there is a node with an application entity, then save the application entity as well
        this.pipelineNodeApplicationEntities.forEach(
          pipelineNodeApplicationEntity => {
            if (pipelineNodeApplicationEntity.pipelineNodeId === node.id) {
              newPipelineNode['application_entity_id'] =
                pipelineNodeApplicationEntity.applicationEntityId
            }
          }
        )
        nodeArray.push(newPipelineNode)
      })
      this.savedLinks.forEach(link => {
        const newPipelineLink = {
          to: link.to,
          from: link.from
        }
        linkArray.push(newPipelineLink)
      })

      const PAYLOAD = { nodes: nodeArray, links: linkArray }
      const URL = `/pipeline/${this.id}`
      try {
        await generic_post(this, URL, PAYLOAD)
        this.$toaster.toastSuccess('Pipeline saved!')
      } catch (e) {
        let msg =
          'Something went wrong, please make sure your pipeline is properly formed'

        try {
          msg = e.response.data.detail[0].msg
        } finally {
          this.$toaster.toastError(msg)
        }
      }
    },
    checkSaved() {
      return (
        this.savedNodes === this.scene.nodes &&
        this.savedLinks === this.scene.links
      )
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
.flowchart-container {
  margin: 0;
  width: 100%;
  height: calc(100vh - 24px);
  background: #ddd;
  position: relative;
  overflow: hidden;

  svg {
    cursor: grab;
  }
}
</style>
