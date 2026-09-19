# kuroneko-cmd-skills

[English](README.md)

一组轻量、可移植的AI Agent技能，由[KURONEKO-CMD](https://github.com/KURONEKO-CMD)创建和维护。

## 现有技能

| Skill | 用途 |
| --- | --- |
| [kuroneko-paper-reader](skills/kuroneko-paper-reader/SKILL.md) | 一篇一篇读论文：先建立索引，再结合原图和证据逐步解释，通过HTML阅读页面跨对话继续。 |

## 安装

下载或克隆仓库后，复制**完整skill目录**，保留references、assets和scripts。不需要npm、marketplace、API密钥或全局配置。打包工具需要Python 3.10以上，PDF和浏览器能力由Agent所在环境提供。

在本仓库根目录运行，将`/path/to/project`替换为目标项目：

```sh
# Codex
mkdir -p /path/to/project/.agents/skills
cp -R skills/kuroneko-paper-reader /path/to/project/.agents/skills/

# Claude Code
mkdir -p /path/to/project/.claude/skills
cp -R skills/kuroneko-paper-reader /path/to/project/.claude/skills/
```

个人安装可将完整目录复制到Codex的`~/.agents/skills/`或Claude Code的`~/.claude/skills/`，也可创建指向完整目录的软链接。更新时替换已安装的skill目录，已有阅读包保留自己的模板，不会自动迁移。

## 开始阅读

在Codex中使用`$kuroneko-paper-reader`，在Claude Code中使用`/kuroneko-paper-reader`。例如：

> 用kuroneko-paper-reader帮我读这篇PDF。我有生化基础，但不熟悉这个方向。请用中文、中度解释，将阅读包保存到代码仓库外。

首版包含整篇索引、建议阅读路线、必要术语，以及一个完整展开的单元。其余部分明确标记为待展开。轻度、中度、深度分别对应零基础、相关领域背景和专业背景，不限制继续深入的程度。

在浏览器打开`reader.html`，可以直接切换已经生成的解释。需要补充时，点击章节中的提示词按钮，可以追加具体问题，然后把提示词粘贴到Agent对话中。Agent更新同一个阅读包，保留已有档位和原始证据。

新对话使用全局的“在新对话中继续”，并提供阅读包位置。换设备或平台时，携带**完整阅读文件夹**，包括原文、素材、内容、模板和状态文件。仅凭skill名称或一份HTML无法恢复不可访问的原始资料。

## 输出与语言

每篇论文独立保存，默认位于工作目录的`paper-readings/`下。阅读包包含原文副本、提取图表、解释片段、`project.json`、界面与模板，以及生成的`reader.html`。HTML内嵌解释和展示图片，可离线阅读，打开原始PDF和继续编辑需要完整阅读包。

页面与导出的提示词跟随用户要求的语言。预置英文、简体中文、日文界面，其他语言由Agent补充完整翻译。尚未生成的档位明确显示待生成，原始技术名称和原图像素保持不变。

ImageGen仅在用户明确要求、宿主具备能力时调用，并以论文原图为参考。常规阅读不需要生图服务。来源缺失和图文冲突会保留显示。

## 开发与验证

```sh
python -m unittest discover -s tests -v
```

公开测试只用自编样例。真实PDF、提取文本、图表、阅读页面、截图和报告保存在仓库外。仓库已忽略PDF和常见阅读产物目录，不应强制加入Git。

2026-09-19本地验证结果：

- 18项Python标准库回归测试，以及skill元数据和相对资源路径检查。
- Chromium中的中、英、日界面与提示词，原图查看、档位切换、待展开状态、手动复制回退、独立HTML阅读，以及桌面和390px移动端布局。
- 在隔离的项目目录中验证Codex原生发现。新对话使用浏览器导出的提示词，为现有论文阅读包增加中度解释，保留轻度解释、其他章节、原始文件和模板。进一步核对发现资料缺口后，旧解释也追加了相应说明。
- 三篇真实论文分别验证解释升级与返回、补充材料缺失、图文表述不一致，相关资料全部保存在仓库外。自编算法片段用于检查非生命科学结构。

Claude Code保留安装说明与通用skill格式，**未验证实际运行**。其他界面语言、ImageGen集成、其他浏览器及多个Agent同时编辑同一个阅读包均未验证。打包成功不等于科学结论已经核实。

## 许可

[MIT](LICENSE)。Copyright (c) 2026 KURONEKO-CMD。用户提供的论文与原图保留其原有权利，不包含在本仓库中。
