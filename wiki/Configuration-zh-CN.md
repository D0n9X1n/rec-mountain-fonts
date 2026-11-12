# 配置

[English](Configuration)

每套字体对应 `configs/` 中的一个 YAML 文件。上游版本记录在 `versions.env`。

## 字体配置

`configs/st-helens.yaml` 保存共同的 Recursive 设计：

| 键 | 含义 |
|---|---|
| `Family Name` | 完整字体名，例如 `Rec Mono St.Helens`。文件名和 PostScript 名去掉空格。 |
| `Base` | 拉丁字形来源：`recursive`（默认）或 `anthropic-serif` |
| `Mono` | `true` 构建等宽字体（`MONO 1`）；`false` 构建比例字体（`MONO 0`）。`anthropic-serif` 必须为 `false`。 |
| `Styles` | `recursive`：Regular、Italic、Bold、Bold Italic 各自的 `CASL`、`wght`、`slnt` 和 `CRSV`。`anthropic-serif`：每种样式使用的源字重。 |
| `Code Ligatures` | 默认开启 Recursive 的代码连字。只对等宽字体生效。 |
| `Features` | 固化进字体的风格集 |
| `Exclude Features` | 从继承的 `Features` 中移除的风格集 |

`configs/mt-baker.yaml` 以 St.Helens 为基础：

```yaml
Extends: st-helens.yaml

Family Name: Rec Sans Mt.Baker
Mono: false

Exclude Features:
  - ss10  # Dotted 0
```

`Extends` 先加载指定文件，再用当前文件中的键覆盖父配置。`Exclude Features` 随后从继承的
`Features` 中移除风格集；列出未启用的风格集会报错。因此对 St.Helens 样式或风格集的其他修改
也会作用到 Mt.Baker。

`configs/mt-adams.yaml` 独立存在：

```yaml
Family Name: Rec Serif Mt.Adams

Base: anthropic-serif
Mono: false

Styles:
  Regular:     Regular
  Italic:      RegularItalic
  Bold:        Semibold
  Bold Italic: SemiboldItalic
```

`Styles` 的每个值对应 `scripts/fetch-sources.sh` 下载的一个 Anthropic Serif Text 文件：
`Regular`、`RegularItalic`、`Semibold` 或 `SemiboldItalic`。Bold 使用 Semibold，与 Recursive
字体的 wght 600 一致。

## 代码连字

Recursive 把代码连字画成宽于一格的字形。对等宽字体，构建会把每个连字的步进宽度设为
一格，并把轮廓左移，覆盖到前面的单元格上。在比例字体中这会压缩所有宽于空格的字形，
因此当 `Mono` 为 `false` 时，即使 `Code Ligatures` 为 `true`，构建也会跳过连字。

## 风格集

| 特性 | 变化 | 适用 |
|---|---|---|
| ss01 | 单层 a | 仅正体 |
| ss02 | 单层 g | 仅正体 |
| ss03 | 简化 f | 仅正体 |
| ss04 | 简化 i | 仅正体 |
| ss05 | 简化 l | 仅正体 |
| ss06 | 简化 r | 仅正体 |
| ss07 | 简化斜体斜笔画（kwxyz） | 正体和手写体 |
| ss08 | 无衬线 L 和 Z | 正体和手写体 |
| ss09 | 简化 6 和 9 | 正体和手写体 |
| ss10 | 带点的 0 | 正体和手写体 |
| ss11 | 简化 1 | 正体和手写体 |
| ss12 | 简化 @ | 正体和手写体 |

## 上游版本

`versions.env` 固定每个上游发布：

```bash
RECURSIVE_VERSION=1.085
ANTHROPIC_SERIF_VERSION=25.324
RESOURCE_HAN_ROUNDED_VERSION=1.910
NERD_FONTS_VERSION=3.5.1
```

`./scripts/check-updates.sh` 把这些版本与 GitHub 上的最新发布（不含预发布）比较，
有落后时以状态码 1 退出。资源圆体固定为预发布版本（唯一提供可变字体的版本），因此与包括预发布在内的最新发布比较，
`scripts/fetch-sources.sh` 按 SHA-256 固定它的压缩包。Anthropic Serif 没有发布源：`ANTHROPIC_SERIF_VERSION` 是它的名称表版本，
`scripts/fetch-sources.sh` 按 SHA-256 固定它的每个文件，因此要同时修改那里的哈希值和版本号。要更新某个版本，修改版本号，同时更新 `README.md` 中的版本徽章和
两个配置页面中的上述代码块（不一致时本地检查会失败），运行
`./scripts/local-gate.sh --build`，并在编辑器中检查效果后再合并。

## 添加字体

1. 新建 `configs/<名称>.yaml`：Recursive 字体通常写上 `Extends: st-helens.yaml`，衬线字体写上
   `Base: anthropic-serif`。
2. 运行 `./scripts/build.sh configs/<名称>.yaml`。

`build-all.sh`、校验脚本、CI 和发布打包都会自动处理 `configs/` 中的每个文件。
