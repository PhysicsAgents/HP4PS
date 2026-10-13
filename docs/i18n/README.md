# Bilingual documentation

English | [中文](README.zh.md)

This repository follows the bilingual convention of [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/i18n/README.md), in a lighter form.

## Documents

- **A pair is two sibling files.** The English `foo.md` and the Chinese `foo.zh.md` sit in the same directory. No locale directories, no separate translation repo, no interleaved bilingual files.
- **Both languages carry equal authority.** Write either side first; the other is translated from it. A change that edits one side updates the other in the same commit, patching only the changed sections.
- **Language switcher.** The line right after the H1 is `English | [中文](foo.zh.md)` in the English file and `[English](foo.md) | 中文` in the Chinese file.
- **Structure mirrors the counterpart.** Headings, lists, tables, links and code blocks match one to one; code blocks stay byte-identical. Links to other paired documents point at `.md` from English and `.zh.md` from Chinese.
- **Excluded**: `AGENTS.md` and `CLAUDE.md`, which stay English only.

## Homepage

Interface text lives only in the locale dictionaries `homepage/locales/en_US.json` and `homepage/locales/zh_CN.json`; page code never hard-codes copy. Both dictionaries have exactly the same keys. Data such as names and scores in `homepage/data/site.json` is not translated.

## The check

`python scripts/verify_i18n.py` checks that every document has its pair with both switchers, and that the two locale dictionaries have the same keys. The homepage deployment runs it first and stops on failure. It cannot judge whether the two sides say the same thing; that is the reviewer's job.
