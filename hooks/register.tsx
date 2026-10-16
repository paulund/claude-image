import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

const PNG = /\/[^\s"'`\\<>()]*\.png\b/g
const state = atom({ plugin: 'image', key: 'state' } as const, { paths: [] as string[], index: -1 })

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'image',
      description: 'View screenshots from this session in a zoomable split (/image N, /image list)',
      argumentHint: '[n|list]',
    })
    return next(e)
  })

  // Collect absolute .png paths from any tool call's input and output.
  on('tool.call', async ($, e, next) => {
    const ran = await next(e)
    const found = JSON.stringify([e, ran.deny === undefined ? ran.result : ''])
      .replace(/\\\//g, '/')
      .match(PNG)
    if (found) {
      const fresh = []
      for (const p of new Set(found)) {
        const ok = await $.fs.stat(p).then(s => s.kind === 'file', () => false)
        if (ok) fresh.push(p)
      }
      if (fresh.length) {
        await update($, state, s => {
          const merged = [...s.paths.filter(p => !fresh.includes(p)), ...fresh].slice(-50)
          return { paths: merged, index: merged.length - 1 }
        })
        $.ui.toast(`screenshot: ${fresh[fresh.length - 1]}  (/image to view)`)
      }
    }
    return ran
  }).catch(($, e, next) => next(e))

  on('command.run', { command: 'image' }, async ($, e) => {
    const s = await read($, state)
    const arg = (e.args ?? '').trim()
    if (arg === 'list') {
      return { text: s.paths.length ? s.paths.map((p, i) => `${i + 1}. ${p}`).join('\n') : 'No screenshots seen yet.' }
    }
    if (!s.paths.length) return { text: 'No screenshots seen yet.' }
    const n = arg ? Number(arg) : s.paths.length
    if (!Number.isInteger(n) || n < 1 || n > s.paths.length) return { text: `Pick 1-${s.paths.length}.` }

    // Open a herdr split beside this pane and run the viewer there.
    const split = await $.process.run(['herdr', 'pane', 'split', '--current', '--direction', 'right'])
    if (split.exitCode !== 0) {
      return { text: `Could not split a herdr pane (are you running inside herdr?). Run: python3 ${$.plugin.root}/bin/viewpng.py ${s.paths.join(' ')}` }
    }
    const paneId = JSON.parse(split.stdout)?.result?.pane?.pane_id
    if (!paneId) return { text: 'herdr split gave no pane id.' }
    await $.process.run(['herdr', 'pane', 'run', paneId, 'python3', `${$.plugin.root}/bin/viewpng.py`, `--start=${n - 1}`, ...s.paths])
    return { text: `Viewing ${n}/${s.paths.length} in pane ${paneId}. Click it, then + - arrows 0 [ ] q.` }
  })
}
