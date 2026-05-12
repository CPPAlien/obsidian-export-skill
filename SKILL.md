---
name: obsidian-export
description: 将 Obsidian Vault 中的笔记导出为标准 Markdown 文件。支持单篇、子目录或全库导出，自动处理 Wiki 链接、嵌入图片、frontmatter、标签过滤。当用户想导出/推送 Obsidian 笔记、把 .md 转换为标准格式、或提到 obsidian-export 工具时使用。
---

# obsidian-export

将 Obsidian Vault 导出为 CommonMark 标准 Markdown，使用 [obsidian-export](https://github.com/zoni/obsidian-export) CLI 工具。

## Vault 默认路径

```
/Users/chris/Documents/Obsidian Vault
```

## 安装检测

每次执行前先确认工具存在：

```bash
source $HOME/.cargo/env 2>/dev/null; which obsidian-export
```

如果未找到，执行以下命令安装并激活：

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://github.com/zoni/obsidian-export/releases/download/v24.11.0/obsidian-export-installer.sh | sh
source $HOME/.cargo/env
```

安装后所有后续命令都需要在 `source $HOME/.cargo/env` 之后执行，或使用完整路径 `$HOME/.cargo/bin/obsidian-export`。

## 命令语法

```
obsidian-export [OPTIONS] <VAULT> <DESTINATION>
```

参数说明：
- `<VAULT>` — Vault 根目录路径，或单篇 .md 文件路径
- `<DESTINATION>` — 输出目录（或文件路径，当源为单文件时）

## 常用选项

| 选项 | 说明 |
|------|------|
| `--start-at <PATH>` | 只导出 Vault 的某个子目录/文件，但 Wiki 链接仍按整个 Vault 解析 |
| `--frontmatter always` | 始终插入 frontmatter（无则生成空块）|
| `--frontmatter never` | 去除所有 frontmatter |
| `--skip-tags TAG` | 跳过含指定 tag 的文件，可重复使用 |
| `--only-tags TAG` | 只导出含指定 tag 的文件，可重复使用 |
| `--hidden` | 包含隐藏文件（默认排除）|
| `--no-git` | 禁用 Git 忽略规则 |
| `--no-recursive-embeds` | 递归嵌入时改为插入链接而非报错 |

## 导出场景

### 单篇文章

```bash
obsidian-export \
  "/Users/chris/Documents/Obsidian Vault" \
  --start-at "/Users/chris/Documents/Obsidian Vault/Vibe Design/M3-M4-M5 架构演变.md" \
  /tmp/obsidian-out/
```

### 某个子目录

```bash
obsidian-export \
  "/Users/chris/Documents/Obsidian Vault" \
  --start-at "/Users/chris/Documents/Obsidian Vault/Vibe Design" \
  /tmp/obsidian-out/
```

### 整个 Vault

```bash
obsidian-export \
  "/Users/chris/Documents/Obsidian Vault" \
  /tmp/obsidian-out/
```

## 执行流程

1. **解析意图** — 根据用户描述的文档名、目录名或关键词，在 Vault 中定位目标文件/目录（用 `find` 搜索）
2. **确认目标** — 把找到的路径告诉用户并确认（如果唯一则直接确认）
3. **检查工具** — 确认 obsidian-export 已安装
4. **确定输出目录** — 默认 `/tmp/obsidian-out/<slug>`，如用户指定则优先使用
5. **运行导出** — 执行命令，捕获输出，报告成功/失败
6. **后续操作** — 导出后询问用户是否需要推送到某个目标（如 CF Pages、服务器等）

## 错误处理

- **找不到文件**：用 `find` 模糊匹配后列出候选，让用户选择
- **recursive embed 报错**：追加 `--no-recursive-embeds` 重试
- **工具未安装**：给出安装指引后暂停
- **输出目录非空**：提示用户确认覆盖或换路径

## .export-ignore

如果 Vault 根目录有 `.export-ignore`（gitignore 语法），工具会自动遵守。可以建议用户创建该文件来排除草稿、模板等目录。

示例 `.export-ignore`：
```
templates/
drafts/
*.canvas
```
