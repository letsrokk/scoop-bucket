# letsrokk Scoop bucket

A collection of Windows apps for [Scoop](https://scoop.sh).

## Add the bucket

With [Scoop](https://github.com/ScoopInstaller/Scoop#installation) and Git installed, run in PowerShell:

```powershell
scoop bucket add letsrokk https://github.com/letsrokk/scoop-bucket.git
```

## Supported apps

### Herdr GPUI

[Herdr GPUI](https://github.com/penso/herdr-gpui) is a portable desktop interface for the Herdr daemon. Supports Windows x64 and ARM64; Scoop selects the appropriate architecture automatically.

The Windows builds are experimental and unsigned. An existing Herdr daemon is required; this package installs only the GUI.

```powershell
scoop install letsrokk/herdr-gpui
```

Launch **Herdr** from the Start Menu or run `herdr-gpui`.
