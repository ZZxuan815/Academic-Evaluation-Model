# 学业评估模型（大创项目）

大学生创新训练项目：学业成长评估与个性发展激励研究原型。

**仓库地址：https://github.com/ZZxuan815/Academic-Evaluation-Model**

## 目录结构

| 目录/文件 | 内容 |
|---|---|
| `平台/` | 网页评估平台（前端 + Node.js 后端 + 账号系统 + 激励模块） |
| `数据实验/` | 公开数据加工、基线预测实验、900 条合成数据及校验脚本 |
| `周五汇报材料/` | 阶段汇报稿、公式笔记、文献对应表与历史网页快照 |
| `调研/` | 文献调研笔记与阅读卡片（论文全文转录未入库） |
| `资料/` | 文献综述与立项报告（论文 PDF 未入库） |
| `中期答辩开发方案.md` 等 | 方案、选型、激励设计等说明文档 |

## 运行平台

```powershell
cd 平台
powershell -File 启动本地平台.ps1
# 浏览器访问 http://127.0.0.1:8787
```

依赖：Node.js ≥ 22（`node:sqlite`）；模型推荐功能需本地 Ollama + qwen3:4b，或通过 `MODEL_BASE_URL / MODEL_NAME / MODEL_API_KEY` 环境变量接入托管兼容 API。未配置模型时平台仍可使用规则模式。

## 测试

```powershell
cd 平台
node verify.cjs                 # 核心评分与边界回归
node synthetic.test.cjs         # 900 条合成数据前后端一致性
node intent.test.cjs            # 自然语言选指标
node rewards.test.cjs           # 激励逻辑
node server/accounts.test.mjs   # 账号接口
node server/model-adapter.test.mjs
```

## 重要说明

- 合成数据完全人工生成，不代表真实学生，不用于证明准确率或激励有效。
- 分数与阈值仅用于演示，不作为实际学生评价依据；权重方案为研究候选，尚未经效度验证。
- 公网部署尚未完成；账号数据库 `平台/server/private/` 不入库。

## 数据来源与许可

公开数据加工自 [Nitrene123/college-student-dea-evaluation-system](https://github.com/Nitrene123/college-student-dea-evaluation-system)（固定版本 43c04d6）中的 UCI 697 筛选样本，原始数据 CC BY 4.0：Realinho et al. (2021), *Predict Students' Dropout and Academic Success*, UCI Machine Learning Repository, https://doi.org/10.24432/C5MC89 。
