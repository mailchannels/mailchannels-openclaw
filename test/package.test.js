const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');

function loadPackageJson() {
  const raw = fs.readFileSync('package.json', 'utf8');
  return JSON.parse(raw);
}

test('package.json includes npm package metadata', () => {
  const pkg = loadPackageJson();

  assert.equal(pkg.name, 'mailchannels-moltbot');
  assert.match(pkg.version, /^\d+\.\d+\.\d+$/);
  assert.equal(pkg.scripts.test, 'node --test');
  assert.ok(Array.isArray(pkg.keywords));
  assert.ok(pkg.keywords.includes('mailchannels'));
});
