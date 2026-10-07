const { test } = require('node:test');
const assert = require('node:assert/strict');
const document = require('../design-tokens.json');
const { resolveTokens } = require('./resolve-tokens.cjs');
test('every theme resolves all four modes without fallback', () => {
  for (const [id, theme] of Object.entries(document.themes)) {
    for (const mode of ['light', 'dark', 'light_hc', 'dark_hc']) {
      const result = resolveTokens(document, id, mode);
      assert.equal(result.colors.text, theme[mode].ink);
      assert.equal(result.colors.action, theme[mode].accent);
      assert.ok(Number.isFinite(result.cardRadius));
      assert.equal(result.minTargetSize, 44);
    }
  }
});
test('future versions, missing modes and corrupted roles fail explicitly', () => {
  assert.throws(() => resolveTokens({ ...document, native_contract_version: 2 }, 'A', 'light'));
  assert.throws(() => resolveTokens(document, '__proto__', 'light'));
  assert.throws(() => resolveTokens(document, 'A', 'auto'));
  const copy = structuredClone(document);
  delete copy.themes.A.dark_hc;
  assert.throws(() => resolveTokens(copy, 'A', 'dark_hc'));
  copy.themes.A.light.ink = 'red';
  assert.throws(() => resolveTokens(copy, 'A', 'light'));
});
test('invalid or overflowing geometry never reaches native styles', () => {
  for (const radius of ['50%', '-1px', `${'9'.repeat(400)}px`]) {
    const copy = structuredClone(document);
    copy.themes.A.light.r_card = radius;
    assert.throws(() => resolveTokens(copy, 'A', 'dark'), /Invalid card radius/);
  }
});
