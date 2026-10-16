import { test, expect } from 'claude-code/testing'

test('shot with nothing seen says so', async $ => {
  const out = await $.command.run({ command: 'shot', args: '' })
  expect(JSON.stringify(out)).toContain('No screenshots seen yet')
})
