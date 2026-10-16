export type ImageState = { paths: string[]; index: number }

declare module 'claude-code' {
  interface PluginState {
    image: { state: ImageState }
  }
}
