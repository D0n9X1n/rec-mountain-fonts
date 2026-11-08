# 字体

[English](Fonts)

Rec Mountain Fonts 提供三套字体。St.Helens（用于写代码）和 Mt.Baker（相同字形、自然字宽，
用于日常文本）共用同一套 Recursive 设计；Mt.Adams 是用于长文阅读的衬线字体，基于 Anthropic Serif Text。

## 预览

### 样式

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/styles-dark.png">
  <img alt="Regular, Italic, Bold, and Bold Italic of all three families" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/styles-light.png" width="800">
</picture>

### 代码

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/code-dark.png">
  <img alt="TypeScript in Rec Mono St.Helens with code ligatures and italic keywords" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/code-light.png" width="800">
</picture>

### 终端

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/terminal-dark.png">
  <img alt="A shell prompt with Powerline segments, Nerd Font icons, and a CJK table aligned on the cell grid" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/terminal-light.png" width="800">
</picture>

### 连字

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/ligatures-dark.png">
  <img alt="Thirty code ligatures in Rec Mono St.Helens" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/ligatures-light.png" width="800">
</picture>

### 文本

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/text-dark.png">
  <img alt="English, Chinese, and Japanese paragraphs in Rec Sans Mt.Baker" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/text-light.png" width="800">
</picture>

### 衬线

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/serif-dark.png">
  <img alt="English, Chinese, and Japanese paragraphs in Rec Serif Mt.Adams" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/serif-light.png" width="800">
</picture>

### 字形覆盖

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/glyphs-dark.png">
  <img alt="Glyph coverage: Latin, Vietnamese, mathematical Greek, CJK, kana, box drawing, Powerline, and Nerd Font icons" src="https://raw.githubusercontent.com/D0n9X1n/rec-mountain-fonts/main/docs/previews/glyphs-light.png" width="800">
</picture>

## 字体家族

| 字体 | 用途 | 字宽 | 代码连字 |
|---|---|---|---|
| **Rec Mono St.Helens** | 编辑器和终端 | 等宽，单元格 600 单位 | 有 |
| **Rec Sans Mt.Baker** | 文档和界面 | 比例宽度 | 无 |
| **Rec Serif Mt.Adams** | 文章、笔记和电子书 | 比例宽度 | 无 |

每套字体有四种样式：Regular、Italic、Bold 和 Bold Italic。

## St.Helens 与 Mt.Baker 的设计

这两套字体来自同一份配置（`configs/st-helens.yaml`）；Mt.Baker 改了名称和字宽，并去掉带点的零。
见[配置](Configuration-zh-CN)。

| 设置 | 值 |
|---|---|
| 休闲度（`CASL`） | 1 — Recursive 的休闲笔刷风格 |
| 手写体（`CRSV`） | 1 — 手写体字形 |
| 倾斜（`slnt`） | Regular 和 Bold 为 -3°，Italic 和 Bold Italic 为 -10° |
| 字重（`wght`） | Regular 和 Italic 为 400，Bold 和 Bold Italic 为 600 |
| 风格集 | ss01–ss12；Mt.Baker 不含 ss10，因此 St.Helens 的零带点，Mt.Baker 的零不带点 |

Recursive 的 ss01–ss06 只作用于正体（`CRSV 0`）字形，因此在 `CRSV 1` 下看不出变化。
它们保留在配置里，方便正体字体复用。

## Mt.Adams 的设计

Mt.Adams（`configs/mt-adams.yaml`）的每种样式取自 Anthropic Serif Text 的一个静态字重：

| 样式 | Anthropic Serif Text 字重 |
|---|---|
| Regular | Regular |
| Italic | Italic（-10°） |
| Bold | Semibold，与其他字体的 wght 600 一致 |
| Bold Italic | Semibold Italic |

构建会把它的 CFF 轮廓转换为每 em 1000 单位的 TrueType 轮廓，使中日文合入和图标的对齐方式
与 Recursive 字体一致。

## 字形覆盖

| 来源 | 覆盖范围 |
|---|---|
| Recursive | 拉丁字母（含越南语）、20 个数学用希腊字母、制表符、方块、标点和符号。不含西里尔字母。 |
| Anthropic Serif Text（Mt.Adams） | Latin-1 和完整的拉丁扩展-A（西欧和中欧语言）、标点和符号。不含越南语、希腊字母、西里尔字母和制表符。 |
| 资源圆体 CN | 汉字（U+4E00–9FFF 中 20,976 个）、假名、CJK 标点、全角和半角字符 |
| Nerd Fonts | 补丁工具 `--complete` 选项加入的全部图标集，包括 Powerline |

Regular 和 Italic 使用资源圆体 Medium 字重的中日文字形，Bold 和 Bold Italic
使用其 Bold 字重。在每套字体中，字形先按拉丁字体的 em 缩放，只有高于其上伸部到下伸部的
字身时才缩小，然后放大 1.15 倍并在该字身中居中。不包含韩文音节。

## 字宽差异

| 字形组 | St.Helens | Mt.Baker | Mt.Adams |
|---|---|---|---|
| ASCII | 固定 600 | 自然宽度（例如 `i` 350、`m` 850） | 自然宽度（例如 `i` 300、`m` 944） |
| 汉字和全角字符 | 1200（两格） | 按比例缩放的原始宽度（1150） | 按比例缩放的原始宽度（1150） |
| 半角字符 | 600（一格） | 按比例缩放的原始宽度（575） | 按比例缩放的原始宽度（575） |
| Nerd Font 图标 | 两格，居中 | 自然宽度 | 自然宽度 |
| 代码连字（`=>`、`!=`） | 默认开启 | 关闭 | 无 |

St.Helens 还设置了 Windows Terminal 和 DirectWrite 让 ASCII 保持在单元格网格上所需的标志；
见[构建流程](Build-Pipeline-zh-CN)。
