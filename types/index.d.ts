export type ShotsState = { paths: string[]; index: number }

declare module 'claude-code' {
  interface PluginState {
    shots: { state: ShotsState }
  }
}
