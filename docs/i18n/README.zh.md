# 双语文档

[English](README.md) | 中文

本仓库沿用 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/i18n/README.zh.md) 的双语约定，做了简化。

## 文档

- **一对文档是两个同级文件。** 英文 `foo.md` 和中文 `foo.zh.md` 放在同一目录下。不设语言目录，不另建翻译仓库，也不在一个文件里中英混排。
- **两种语言同等权威。** 哪一边先写都可以，另一边据此翻译。修改一边的提交，要在同一个提交里同步修改另一边，只改动对应的段落。
- **语言切换链接。** H1 标题下一行，英文文件写 `English | [中文](foo.zh.md)`，中文文件写 `[English](foo.md) | 中文`。
- **结构与对应文件一致。** 标题、列表、表格、链接和代码块一一对应；代码块逐字节相同。指向其他成对文档的链接，英文侧用 `.md`，中文侧用 `.zh.md`。
- **例外**：`AGENTS.md` 和 `CLAUDE.md` 只保留英文。

## 主页

界面文字只放在语言字典 `homepage/locales/en_US.json` 和 `homepage/locales/zh_CN.json` 里，页面代码不直接写文案。两个字典的键必须完全一致。`homepage/data/site.json` 中的名称、分数等数据不翻译。

## 检查

`python scripts/verify_i18n.py` 检查每个文档都有成对文件且带两种切换链接，并检查两个语言字典的键一致。主页部署会先运行它，失败就停止部署。它无法判断两边说的是否是同一件事，这要靠审阅者把关。
