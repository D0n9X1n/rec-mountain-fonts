# Building

[简体中文](Building-zh-CN)

The build turns pinned upstream releases into the twelve release fonts. It runs
the same way locally and in CI.

## Prerequisites

| Tool | macOS | Debian/Ubuntu |
|---|---|---|
| Python 3 | Included with Xcode tools or Homebrew | `python3`, `python3-venv` |
| FontForge | `brew install fontforge` | `apt-get install fontforge python3-fontforge` |
| 7-Zip | `brew install sevenzip` | `apt-get install p7zip-full` |
| curl, unzip | Preinstalled | Preinstalled |

Python packages are pinned in `requirements.txt`:

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Build

```bash
./scripts/build-all.sh                       # every family in configs/, in parallel
./scripts/build.sh configs/st-helens.yaml    # one family
./scripts/build-all.sh 1.2                   # override the CJK scale (default 1.15)
```

Output goes to `fonts/<CompactFamily>/`, for example
`fonts/RecMonoSt.Helens/RecMonoSt.Helens-Regular.ttf`. A full build takes about
90 seconds on an Apple Silicon Mac.

## Upstream sources

The first build runs `scripts/fetch-sources.sh`, which downloads the versions
pinned in `versions.env` into `sources/`:

| Directory | Contents |
|---|---|
| `sources/recursive/` | `Recursive_VF_<version>.ttf` and the code-ligature feature file |
| `sources/anthropic-serif/` | Four Anthropic Serif Text `.otf` files, each checked against its pinned SHA-256 |
| `sources/resource-han-rounded/` | `ResourceHanRoundedCN-Regular.ttf` (wght 400) and `-SemiBold.ttf` (wght 600), made from the variable font, whose archive is checked against its pinned SHA-256 |
| `sources/nerd-fonts-patcher/` | The Nerd Fonts `font-patcher` and its glyph sources |

Each directory records its version in `.version`; later builds skip the download
until `versions.env` changes. Resource Han Rounded is also downloaded again
when one of its weight files is missing or `scripts/instance-cjk.py` changes. `sources/`, `build/`, and `fonts/` are git-ignored.

## Preview images

The images in `README.md` and on the [Fonts](Fonts) page live in `docs/previews/`.
After any change that affects font output, regenerate them from the built fonts
and commit the result:

```bash
python3 scripts/render-previews.py            # reads fonts/
python3 scripts/render-previews.py <dir>      # or another folder with the same layout
```

Each preview is written in the Apollo dark and light palettes. Text is shaped
with HarfBuzz through Pillow, so ligatures, CJK, and icons appear as they do in
apps.

## Checks

```bash
./scripts/local-gate.sh            # scripts, configs, wiki, CJK fetch, release notes (seconds)
./scripts/local-gate.sh --build    # also builds and verifies every family
```

Run the gate before opening a pull request. CI runs the same checks; see
[Release Process](Release-Process).
