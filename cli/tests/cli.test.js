// Tests for the mcps-ai CLI internals. Run: node --test cli/tests/
const { test } = require('node:test');
const assert = require('node:assert');

const { mergeServers } = require('../src/agents')._test;
const { dirExists, fileExists } = require('../src/install')._test;

test('mergeServers keeps existing valid entries and adds missing ones', () => {
  const existing = { telegram: { type: 'local', command: ['uv', '--directory', '/tmp', 'run', 'main.py'], environment: { TELEGRAM_BOT_TOKEN: 'keepme' } } };
  const incoming = { telegram: { type: 'local', command: ['other'] }, github: { type: 'local', command: ['x'] } };
  const merged = mergeServers(existing, incoming);
  assert.deepEqual(merged.github, incoming.github, 'missing server added');
  assert.strictEqual(merged.telegram.environment.TELEGRAM_BOT_TOKEN, 'keepme', 'existing non-empty env preserved');
});

test('mergeServers does not overwrite with empty env values', () => {
  const existing = { minecraft: { type: 'local', command: ['uv'], environment: { MC_RCON_PASSWORD: 'secret', MC_PLAYER: 'Steve' } } };
  const incoming = { minecraft: { type: 'local', command: ['uv'], environment: { MC_RCON_PASSWORD: '', MC_PLAYER: '' } } };
  const merged = mergeServers(existing, incoming);
  assert.strictEqual(merged.minecraft.environment.MC_RCON_PASSWORD, 'secret');
  assert.strictEqual(merged.minecraft.environment.MC_PLAYER, 'Steve');
});

test('mergeServers takes incoming command when existing dir is gone', () => {
  const existing = { web: { type: 'local', command: ['uv', '--directory', '/nonexistent/path/xyz', 'run', 'main.py'] } };
  const incoming = { web: { type: 'local', command: ['uv', '--directory', '/tmp', 'run', 'main.py'] } };
  const merged = mergeServers(existing, incoming);
  assert.deepEqual(merged.web.command, incoming.web.command);
});

test('dirExists and fileExists are distinct', () => {
  assert.strictEqual(dirExists('/tmp'), true);
  assert.strictEqual(dirExists('/etc/hostname'), false);
  assert.strictEqual(fileExists('/etc/hostname'), true);
  assert.strictEqual(fileExists('/tmp'), false);
  assert.strictEqual(dirExists('/nonexistent-definitely-xyz'), false);
  assert.strictEqual(fileExists('/nonexistent-definitely-xyz'), false);
});

test('mergeServers handles empty inputs', () => {
  assert.deepEqual(mergeServers(null, { a: { x: 1 } }), { a: { x: 1 } });
  assert.deepEqual(mergeServers({ a: { x: 1 } }, null), { a: { x: 1 } });
});
