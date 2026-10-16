import { test, expect } from 'claude-code/testing'

test('image with nothing seen says so', async $ => {
  const out = await $.command.run({ command: 'image', args: '' })
  expect(JSON.stringify(out)).toContain('No screenshots seen yet')
})
