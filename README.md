# Joincap Projects

项目全景、学校与教授关系、投资管理和每周会议更新。

**网页：<https://nhien462206dang30-dev.github.io/Joincap_Projects/>**

GitHub Pages 从 `main` 分支根目录发布 `index.html`。推送更新后，GitHub 自动构建并更新网页。

## 更新

- `index.html` 是完整离线网页，包含样式、交互和数据。
- `data.json` 是维护数据；`src/` 是网页模板与代码。
- 修改数据后运行 `python build.py`，再提交并推送 `data.json` 和 `index.html`。
- 周会更新包保存在 `meetings/`。使用 `python apply_meeting.py meetings/2026-11-09.json --data data.json` 导入；同一会议不会重复导入。
- 网页中的数字编辑只保存到当前浏览器。请从“数据与导出”下载最新数据包交给 AI 合并，再推送到 GitHub；手机与电脑的本地修改不会自动同步。

## 内容

当前为 2026-11-09 周会版：177 个公司主档、183 条原始业务记录；8 个项目的会议进展，以及独立列出的待核实和跨项目事项。

更详细的操作说明见 `README.txt`，本周处理说明见 `本周更新-2026-11-09.txt`。初版交付报告中的“未发布”描述为当时的历史状态，本仓库现已启用 GitHub Pages。

本仓库和 Pages 网页为公开访问。更新前备份位于本地 `snapshots/`，不提交到仓库。
