# letsrokk Scoop bucket

Install the portable [Herdr desktop interface](https://github.com/penso/herdr-gpui) on Windows x64 or ARM64 using Scoop. This bucket currently contains only `herdr-gpui`.

The Windows builds are experimental and unsigned. An existing Herdr daemon is required; this package installs only the GUI.

## Install

With [Scoop](https://github.com/ScoopInstaller/Scoop#installation) and Git installed, run in PowerShell:

```powershell
scoop bucket add letsrokk https://github.com/letsrokk/scoop-bucket.git
scoop install letsrokk/herdr-gpui
```

Launch **Herdr** from the Start Menu or run `herdr-gpui`. Scoop selects the appropriate architecture automatically.

To install a later version published in this bucket:

```powershell
scoop update
scoop update herdr-gpui
```

## Update automation

GitHub Actions runs Renovate daily at approximately 03:17 UTC. Stable Herdr releases produce one PR updating the version, both download URLs, extraction directories, and SHA-256 hashes. Herdr update PRs auto-merge after the required checks pass. Missing assets, changed archive layouts, and checksum mismatches fail validation.

Before running the Renovate workflow:

1. Add a fine-grained token as the repository secret `RENOVATE_TOKEN`. Scope it to this repository with **Contents** and **Pull requests** read/write permissions, and **Checks** and **Actions** read permissions. Use an account allowed to merge PRs without bypassing required checks.
2. Enable **Allow auto-merge** and squash merging in repository settings.
3. Protect `main`, require pull requests, and require **Manifest and Renovate** and **Windows Scoop install** before merging. Do not require approvals for automatic Herdr updates.
4. Run **Validate** once to register the checks, then manually run **Renovate** and confirm it completes successfully. Scheduled workflows run from the default branch; GitHub may delay them or disable them after extended repository inactivity.

Validate the archives locally with `python3 scripts/validate.py`. Run the update regression checks using the pinned Renovate image:

```sh
docker run --rm -v "$PWD:/work:ro" -w /work --entrypoint node ghcr.io/renovatebot/renovate:44.155.1 --test tests/renovate.test.mjs
```

Archive validation covers both architectures; the installation workflow covers x64. These checks do not launch the GUI or test daemon connectivity.
