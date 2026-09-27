# 🤝 贡献指南

感谢你对 PandaCode 感兴趣！无论是修 bug、加功能、改文档，都欢迎提交 PR。

---

## 📋 提交 PR 前

请先确认：

- [ ] 你的改动**没有破坏现有功能**
- [ ] 代码在 **Python 3.8+** 下能跑
- [ ] 新增关键字已加入 `src/keywords.py`
- [ ] 如果改了运行逻辑，README 相关部分也同步更新

---

## 🚀 提交流程

### 1. Fork 本仓库

点击 GitHub 页面右上角的 **Fork** 按钮，把仓库复制到你自己的账号下。

### 2. 克隆到本地

```bash
git clone https://github.com/你的用户名/PandaCode.git
cd PandaCode
```

### 3. 创建分支

**不要直接在 `main` 分支上改**，请新建一个分支：

```bash
git checkout -b feature/你的功能名
```

分支命名建议：

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 新功能 | `feature/xxx` | `feature/add-list-keyword` |
| 修 bug | `fix/xxx` | `fix/repl-multiline` |
| 文档 | `docs/xxx` | `docs/update-readme` |
| 重构 | `refactor/xxx` | `refactor/translator` |

### 4. 修改代码

- 保持代码风格一致（本项目用 **4 空格缩进**）
- 中文命名变量是允许的，但**尽量语义清晰**
- 新增函数**写一行中文 docstring**

### 5. 本地测试

```bash
# 确保能启动 GUI
python PandaCode.py

# 确保 CLI 正常
python PandaCode.py -e "打印（'测试'）"

# 确保 REPL 正常
python PandaCode.py repl
```

### 6. 提交

```bash
git add .
git commit -m "feat: 添加 XXX 功能"
```

**Commit 信息规范**（参考 [Conventional Commits](https://www.conventionalcommits.org/)）：

| 前缀 | 含义 |
|------|------|
| `feat:` | 新功能 |
| `fix:` | 修复 bug |
| `docs:` | 文档改动 |
| `style:` | 格式调整（不影响逻辑） |
| `refactor:` | 重构 |
| `test:` | 测试相关 |
| `chore:` | 杂项 |

示例：

```
feat: 新增 集合 关键字映射
fix: 修复 REPL 多行块提前执行的问题
docs: README 添加三种模式介绍
```

### 7. 推送

```bash
git push origin feature/你的功能名
```

### 8. 创建 Pull Request

回到 GitHub 你自己的仓库页面，会看到 **Compare & pull request** 按钮，点击进入。

**PR 标题**：和 commit 信息保持一致

**PR 描述**：填写下面模板

```markdown
## 改动说明

简要描述这次改了什么。

## 改动类型

- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档
- [ ] 重构
- [ ] 其他：______

## 测试情况

- [ ] 本地运行通过
- [ ] GUI 测试通过
- [ ] CLI 测试通过
- [ ] REPL 测试通过

## 相关 Issue

Closes #（如果有对应 issue，填编号）
```

---

## ✅ PR 检查清单

提交后，请自查：

- [ ] 只改了**必要的文件**，没有夹带无关改动
- [ ] 没有把 `build/`、`dist/`、`.vs/`、`__pycache__/` 提交上来
- [ ] 没有提交个人 IDE 配置（`.vscode/`、`.idea/`）
- [ ] commit 信息清晰，没有 `update`、`fix bug` 这种模糊描述
- [ ] PR 描述完整，说明了**为什么改**和**怎么测试**

---

## 🚫 不会被合并的 PR

以下情况 PR 可能被拒绝：

| 情况 | 原因 |
|------|------|
| 只改空格 / 换行 | 没有实质改动 |
| 大规模重命名变量 | 影响可读性，且无功能提升 |
| 提交 `build/` / `dist/` | 这些应由 `.gitignore` 排除 |
| 引入第三方依赖 | 本项目**坚持零依赖** |
| 删掉中文命名 | 中文命名是本项目的**特色** |
| PR 描述为空 | 无法判断改动意图 |

---

## 💡 给新贡献者的建议

- **第一次贡献**：从文档、注释、示例开始，最容易上手
- **不确定方向**：先开一个 Issue 讨论，再动手写代码
- **改动较大**：拆成多个小 PR，方便 review
- **遇到问题**：在 Issue 里提问，不用怕

---

## 📜 行为准则

- 友善交流，不人身攻击
- 尊重不同水平的贡献者
- 技术讨论对事不对人

---

## 🐼 最后

**PandaCode 是一个学习项目，欢迎任何人参与。**

哪怕只是改一个错别字，也是贡献。

> 写代码最快乐的事，是有人愿意读你的代码，还愿意帮你改。