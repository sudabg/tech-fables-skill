# Skill Feedback Log

> 运行时监控记录。每次使用 skill 时，Agent 或用户在此记录触发情况和问题。
> 格式：`- [YYYY-MM-DD HH:MM] trigger: success|miss|over | issue | context`

## 触发记录

<!-- 示例（删除这些注释行后使用）
### 成功触发
- [2026-04-24 10:00] trigger: success | user said "create fables project" | loaded correctly

### 欠触发
- [2026-04-24 10:30] trigger: miss | user said "build tech storytelling site" | expected to trigger but didn't

### 过触发
- [2026-04-24 11:00] trigger: over | user said "write technical documentation" | loaded incorrectly
-->

### 成功触发（Expected + Triggered）

<!-- 用户说了触发短语，skill 正确加载 -->

### 欠触发（Expected but Missed）

<!-- 用户说了相关任务，skill 没有自动加载 -->

### 过触发（Unexpected but Triggered）

<!-- skill 在不相关场景下被加载 -->

## 执行问题

<!-- 示例（删除这些注释行后使用）
- [2026-04-24 12:00] exec: error | scaffold failed with "directory already exists" | expected to prompt for overwrite
-->

<!-- skill 加载后，执行不符合预期 -->

## 用户反馈

<!-- 定性反馈 -->

## 改进记录

<!-- 基于反馈进行的改进，追踪效果 -->
