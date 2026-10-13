import assert from 'node:assert/strict';
import { readFile, mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { GlobalConfig } from '/usr/local/renovate/dist/config/global.js';
import { extractPackageFile } from '/usr/local/renovate/dist/modules/manager/custom/regex/index.js';
import { doAutoReplace } from '/usr/local/renovate/dist/workers/repository/update/branch/auto-replace.js';
import { RegExpVersioningApi } from '/usr/local/renovate/dist/modules/versioning/regex/index.js';
import { GithubReleaseAttachmentsDatasource } from '/usr/local/renovate/dist/modules/datasource/github-release-attachments/index.js';

const config = JSON.parse(await readFile('renovate.json', 'utf8'));
const packageFile = 'bucket/herdr-gpui.json';
const original = await readFile(packageFile, 'utf8');
const current = JSON.parse(original).version;

test('Renovate updates both architectures atomically across revisions and dates', async () => {
  const localDir = await mkdtemp(join(tmpdir(), 'herdr-renovate-'));
  GlobalConfig.set({ localDir });
  try {
    for (const next of ['20261013.10', '20261014.1']) {
      let content = original;
      const hashes = { x86_64: 'a'.repeat(64), aarch64: 'b'.repeat(64) };
      for (const manager of config.customManagers) {
        const extracted = extractPackageFile(content, packageFile, manager);
        assert.equal(extracted.deps.length, manager.datasourceTemplate === 'github-releases' ? 1 : 2);
        for (const [depIndex, dependency] of extracted.deps.entries()) {
          assert.equal(dependency.currentValue, `v${current}`);
          content = await doAutoReplace({
            ...manager, ...dependency, manager: 'regex', packageFile, depIndex,
            newValue: `v${next}`, newDigest: hashes[dependency.depType],
          }, content, false);
        }
      }
      const updated = JSON.parse(content);
      assert.equal(updated.version, next);
      for (const [arch, target] of Object.entries({ '64bit': 'x86_64', arm64: 'aarch64' })) {
        const directory = `Herdr-${next}-${target}-pc-windows-msvc`;
        assert.deepEqual(updated.architecture[arch], {
          url: `https://github.com/penso/herdr-gpui/releases/download/v${next}/${directory}.zip`,
          hash: hashes[target], extract_dir: directory,
        });
      }
      assert.equal(updated.bin, 'herdr-gpui.exe');
      assert.deepEqual(updated.shortcuts, [['herdr-gpui.exe', 'Herdr']]);
    }
  } finally {
    GlobalConfig.reset();
    await rm(localDir, { recursive: true, force: true });
  }
});

test('release ordering is numeric and ignores prerelease tag formats', () => {
  const api = new RegExpVersioningApi(config.customManagers[0].versioningTemplate.slice('regex:'.length));
  assert.ok(api.isGreaterThan('v20261013.10', 'v20261013.9'));
  assert.ok(api.isGreaterThan('v20261014.1', 'v20261013.10'));
  assert.ok(!api.isVersion('v20261014.1-rc1'));
});

test('a release without the matching Windows asset has no replacement checksum', async () => {
  const datasource = new GithubReleaseAttachmentsDatasource();
  const digest = await datasource.mapDigestAssetToRelease({
    assetName: `Herdr-${current}-x86_64-pc-windows-msvc.zip`,
    currentVersion: `v${current}`, currentDigest: 'a'.repeat(64),
  }, { tag_name: 'v20261014.1', assets: [] });
  assert.equal(digest, null);
});
