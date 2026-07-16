# 飞书自动写入接入说明

## 已实现能力

`automation/feishu_writer.py` 可读取本项目 Markdown 交付物，默认执行脱机 dry-run；传入 `--execute` 后会：

1. 使用环境变量中的 App ID/Secret 获取 `tenant_access_token`。
2. 创建新版飞书文档。
3. 将内容转换为文本块，按每批 40 块写入文档根块。
4. 遇到 429、服务端错误或飞书频控码时指数退避。
5. 读取文档元数据和纯文本内容进行回读验证。
6. 在 `automation/output/feishu-receipt.json` 保存文档 URL 与验证结果；该目录被 Git 忽略。

## 当前应用配置（已完成）

- 应用名称：`MCN 商单脚本助手`
- App ID：`cli_aad232d702f99bb3`
- 最小权限：应用身份 `docx:document`（创建及编辑新版文档）
- 已发布版本：`1.0.0`
- 发布状态：已发布、审核通过、应用已启用
- 当前可用范围：成员 `Takuru`

## 真实写入验证（已完成）

- 验证时间：2026-07-16
- [飞书最终交付文档](https://feishu.cn/docx/Jmx5dhoT1oW1PxxXlFLclaD6nmc)
- 文档 ID：`Jmx5dhoT1oW1PxxXlFLclaD6nmc`
- 写入结果：5 份核心交付文档，共 206 个文档块、8010 个源字符
- 回读结果：标题匹配；正文 7944 个字符；正文包含项目名称
- 本地回执：`automation/output/feishu-receipt.json`（Git 忽略，仅作本机验证凭证）

## 你只需完成的一次性敏感凭据输入

在飞书开放平台的“凭证与基础信息”页复制 App Secret，然后在项目根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/run_feishu_live.ps1
```

首次运行时，脚本会以不回显方式提示粘贴 Secret，并使用 Windows DPAPI 加密保存到 Git 忽略目录 `automation/.secrets/`。密文只能由当前 Windows 用户在本机解密；Secret 不会以明文写入 `.env`、日志、回执或 Git。后续运行可直接读取密文，无需再次粘贴。

启动器会优先使用 Codex 工作区自带的 Python 运行时；如需指定其他 Python，可传入 `-PythonExecutable 'C:\path\to\python.exe'`。

如需写入指定文件夹，可额外传入：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/run_feishu_live.ps1 `
  -FolderToken '你的文件夹 token'
```

## 通用接入步骤

1. 在飞书开放平台创建企业自建应用。
2. 为应用申请“创建及编辑新版文档”权限；若要把既有文档授权给应用，再申请相应云文档权限。
3. 发布或在企业内启用应用。
4. 在本地会话中设置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`；不要把 Secret 发到聊天、写入 `.env.example` 或提交到 Git。
5. 如需写入指定文件夹，提供 `FEISHU_FOLDER_TOKEN` 并确保应用具有该目录权限。

## 脱机演练

```powershell
python automation/feishu_writer.py `
  research/talent-research.md `
  deliverables/01-style-breakdown.md `
  deliverables/02-workflow-and-prompts.md `
  deliverables/03-script-storyboard.md `
  deliverables/04-compliance-qa.md
```

## 真实写入

```powershell
$env:FEISHU_APP_ID='cli_xxx'
$env:FEISHU_APP_SECRET='只在本地设置'
python automation/feishu_writer.py `
  research/talent-research.md `
  deliverables/01-style-breakdown.md `
  deliverables/02-workflow-and-prompts.md `
  deliverables/03-script-storyboard.md `
  deliverables/04-compliance-qa.md `
  --execute
```

## 官方接口依据

- 自建应用获取租户访问凭证：https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal
- 新版文档接入指南：https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/guide
- 创建新版文档：https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document/create
- 创建文档块：https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/document-block-children/create
- 云文档协作者权限：https://open.feishu.cn/document/server-docs/docs/permission/permission-member/create
