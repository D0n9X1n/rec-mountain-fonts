# 构建

[English](Building)

构建过程把固定版本的上游发布转换成十二个发布字体，在本地和 CI 中的运行方式相同。

## 前置依赖

| 工具 | macOS | Debian/Ubuntu |
|---|---|---|
| Python 3 | Xcode 工具或 Homebrew 自带 | `python3`、`python3-venv` |
| FontForge | `brew install fontforge` | `apt-get install fontforge python3-fontforge` |
| 7-Zip | `brew install sevenzip` | `apt-get install p7zip-full` |
| curl、unzip | 系统自带 | 系统自带 |

Python 包的版本固定在 `requirements.txt`：

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## 构建字体

```bash
./scripts/build-all.sh                       # 依次构建 configs/ 中的所有字体
./scripts/build.sh configs/st-helens.yaml    # 只构建一套
./scripts/build-all.sh 1.2                   # 覆盖中日文缩放比例（默认 1.15）
```

输出位于 `fonts/<紧凑字体名>/`，例如
`fonts/RecMonoSt.Helens/RecMonoSt.Helens-Regular.ttf`。在 Apple Silicon Mac 上
完整构建约需 90 秒。

## 上游源文件

首次构建会运行 `scripts/fetch-sources.sh`，把 `versions.env` 中固定的版本下载到 `sources/`：

| 目录 | 内容 |
|---|---|
| `sources/recursive/` | `Recursive_VF_<版本>.ttf` 和代码连字特性文件 |
| `sources/anthropic-serif/` | 四个 Anthropic Serif Text `.otf` 文件，每个都按固定的 SHA-256 校验 |
| `sources/resource-han-rounded/` | 从可变字体生成的 `ResourceHanRoundedCN-Regular.ttf`（wght 400）和 `-SemiBold.ttf`（wght 600），其压缩包按固定的 SHA-256 校验 |
| `sources/nerd-fonts-patcher/` | Nerd Fonts 的 `font-patcher` 及其图标源文件 |

每个目录在 `.version` 中记录版本；在 `versions.env` 改变之前，后续构建会跳过下载。
资源圆体缺少某个字重文件或 `scripts/instance-cjk.py` 改变时也会重新下载。
`sources/`、`build/` 和 `fonts/` 均被 git 忽略。

## 预览图

`README.md` 和[字体](Fonts-zh-CN)页面中的图片位于 `docs/previews/`。改动影响字体输出后，
用构建出的字体重新生成并提交：

```bash
python3 scripts/render-previews.py            # 读取 fonts/
python3 scripts/render-previews.py <目录>     # 或结构相同的其他目录
```

每张预览图分别使用 Apollo 深色和浅色配色。文字经 Pillow 调用 HarfBuzz 排版，
连字、中日文和图标的显示效果与应用中一致。

## 检查

```bash
./scripts/local-gate.sh            # 脚本、配置、百科、中日文源获取、发布说明（几秒）
./scripts/local-gate.sh --build    # 同时构建并校验所有字体
```

提交拉取请求前先运行检查。CI 运行相同的检查；见[发布流程](Release-Process-zh-CN)。
