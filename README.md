# 小红书达人调研 + 商单脚本生成助手

这是“AI Agent 解决方案实习生——MCN AI 业务方向”的完整实操作品。项目围绕轻食酸奶“轻醒”，实现真实达人调研、达人风格抽象、合规脚本与分镜生成、风险质检、可复用 Skill 和飞书文档自动写入。

## 核心结果

- 联网并站内核实 10 位真实小红书达人，保存主页链接、核实日期和截图。
- 使用 6 维评分矩阵选择 `Shirley爱吃爱练💪` 为第一名候选。
- 抽象钩子、结构、语言、镜头和产品进入方式，不逐句复制原作。
- 生成 38 秒真人可拍短视频脚本和 8 镜分镜。
- 完成食品广告风险和拍摄可行性双重质检。
- 提供 5 步 Agent 工作流、核心 Prompt、可复用 Skill 和飞书写入程序。
- 已通过飞书 API 真实创建并回读验证[最终交付文档](https://feishu.cn/docx/Jmx5dhoT1oW1PxxXlFLclaD6nmc)。

## 目录

```text
research/                         达人调研、候选池、来源和10张截图
deliverables/                     风格拆解、工作流、脚本、质检、飞书说明
skills/mcn-script-assistant/      可复用 Codex Skill
automation/feishu_writer.py       飞书文档写入程序
automation/run_feishu_live.ps1     不回显 Secret 的真实写入启动器
FINAL-REPORT.md                   项目总报告
```

## 快速运行

项目仅使用 Python 标准库。以下命令默认 dry-run，不联网写入：

```powershell
python automation/feishu_writer.py `
  research/talent-research.md `
  deliverables/01-style-breakdown.md `
  deliverables/02-workflow-and-prompts.md `
  deliverables/03-script-storyboard.md `
  deliverables/04-compliance-qa.md
```

真实飞书写入步骤见 [飞书接入说明](deliverables/05-feishu-integration.md)。飞书应用 `MCN 商单脚本助手` 的 `1.0.0` 版本已发布；敏感凭据通过本地安全提示输入，并使用当前 Windows 用户的 DPAPI 加密保存，禁止发送到聊天或提交仓库。

## 数据与合规说明

- 达人账号、粉丝量级和近期内容于 2026-07-16 从小红书公开主页核实。
- 未登录公开页只显示 `1万+` 等区间，本项目不推断精确粉丝数。
- 粉丝画像属于基于公开内容的推断，不替代蒲公英后台数据。
- “0蔗糖”和“高蛋白”必须在拍摄前由最终产品标签或品牌材料确认。
- 本项目不承诺减肥、减脂、降糖或任何医疗/保健功效。

## 仍需人工完成

- 正式投放前通过蒲公英后台确认粉丝画像、报价、互动率、竞品排期和授权范围。
- 拍摄前由品牌确认产品标签、合作披露文案、包装版本、CTA 和非品牌配料展示规则。
