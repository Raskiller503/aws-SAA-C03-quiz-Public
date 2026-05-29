# AWS SAA-C03 Solutions Architect Associate 学习仓库

> 从 CLF-C02 进阶到 SAA-C03 — **不只是刷题，更是建立"架构师式"的思维框架**。

## 📁 仓库结构

```
SAA03/
├── README.md                  ← 你现在看的这份
├── index.html                 ← 跳转到刷题应用
├── quiz-app.html              ← 刷题 UI(与 CLF02 同一套代码)
├── questions.json             ← 1019 道题(双语)
├── questions.js               ← 同上,作为 <script> 直接加载
├── parse_questions.py         ← 从 source/raw_questions.json 重新生成
├── source/
│   └── raw_questions.json    ← 从 nicetd.github.io 爬取的原始数据
└── 学习框架/
    ├── 00-从CLF到SAA的心智转换.md
    ├── 01-架构师的全局视图.md
    ├── 02-存储选型决策树.md
    ├── 03-数据库选型决策树.md
    ├── 04-网络架构.md
    ├── 05-计算服务选型.md
    ├── 06-解耦与事件驱动.md
    ├── 07-监控与运维.md
    ├── 08-安全与合规.md
    ├── 09-迁移与混合云.md
    ├── 10-成本优化.md
    ├── 11-Well-Architected五大支柱.md
    └── 12-考前冲刺与答题套路.md
```

---

## 🎯 SAA-C03 考试速览

| 维度 | 数据 |
|------|------|
| 题数 | **65 道**(其中约 50 道计分,15 道为试用题不计分) |
| 题型 | 单选 + 多选(多选会标注"选 N 个") |
| 时长 | **130 分钟** |
| 合格线 | **720 / 1000** |
| 题库本地 | **1019 道**(本仓库) |
| 费用 | $150 USD |
| 有效期 | 3 年 |

### 四大考试域

| Domain | 名称 | 权重 |
|--------|------|------|
| 1 | **Design Secure Architectures**(安全架构) | 30% |
| 2 | **Design Resilient Architectures**(弹性架构) | 26% |
| 3 | **Design High-Performing Architectures**(高性能架构) | 24% |
| 4 | **Design Cost-Optimized Architectures**(成本优化架构) | 20% |

⚠️ **看清楚 —— 安全权重最高**,且每道题几乎都同时涉及 2-3 个维度。SAA 不再像 CLF 那样"是什么 / 多少钱",而是问"哪种方案**最**符合 X 个要求"。

---

## 🧭 12 周学习路线建议

> 假设你已经过了 CLF,每天 1 小时,周末 3 小时。

| 周次 | 主题 | 对应学习框架文档 | 配套刷题章节(每 50 题) |
|------|------|------------------|--------------------------|
| W0 | 心智转换 + 报名 + 浏览大纲 | `00` | 不做题 |
| W1 | 基础设施 + IAM + VPC 入门 | `01`, `08`(IAM 部分) | 题库 §1(1–50)|
| W2 | 存储四大件 | `02` | §2(51–100)|
| W3 | 数据库选型 | `03` | §3(101–150)|
| W4 | 网络(ELB/Route53/CloudFront/VPC 进阶) | `04` | §4–5(151–250)|
| W5 | 计算选型(EC2 / Lambda / 容器) | `05` | §6–7(251–350)|
| W6 | 解耦与事件驱动 | `06` | §8–9(351–450)|
| W7 | 监控、CloudTrail、Config | `07` | §10–11(451–550)|
| W8 | 安全深入(KMS / WAF / Shield / GuardDuty / Macie) | `08` | §12–13(551–650)|
| W9 | 迁移服务 + 混合云 | `09` | §14–15(651–750)|
| W10 | 成本优化 + Well-Architected | `10`, `11` | §16–17(751–850)|
| W11 | 真题模考 × 3 套 + 错题复盘 | `12` | §18–21(851–1019)|
| W12 | 错题二刷 + 考试 | `12` | "错题"过滤器 |

### 学习方法论

1. **看文档 → 抽象框架 → 做题验证 → 错题归因到框架**。  
   单纯刷题是低效的;只有把每道错题映射回某个"决策点",知识网络才稳固。
2. **每天结束前回答三个问题**:
   - 今天我学的服务,**解决了什么问题**?
   - 它和已有的哪个服务**长得像但不一样**?(差异点是什么?)
   - 在题目里,它通常**和谁组合出现**?
3. **用画图代替记忆**。VPC、ELB、ASG、RDS 的拓扑,自己手画 10 张比死记 100 个参数管用。

---

## 🛠️ 使用刷题应用

```bash
cd /Users/yutong.chen/AWS/SAA03
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000/quiz-app.html
```

刷题应用功能(继承 CLF02):
- 顺序练习 / 随机练习 / 章节练习(每 50 题一组)
- 错题本、收藏夹、笔记
- 模拟考试模式(65 题 / 130 分钟 / 720 合格线)
- 双语切换、AI 解析跳转、本地进度自动保存
- GitHub Gist 跨设备同步

---

## 🔁 重新生成题库

题源更新或需要修改解析格式时:

```bash
# 1. 重新爬取(可选,若上游有更新)
curl -sL "https://nicetd.github.io/saa-c03-quiz/data/questions.json" \
  -o source/raw_questions.json

# 2. 转换成本仓库 schema
python3 parse_questions.py
```

---

## 📝 字段对照(供后续维护参考)

| 上游 raw_questions.json | 本仓库 questions.json | 说明 |
|-------------------------|----------------------|------|
| `id` | `id` | 题号 |
| —(衍生) | `topic` | `(id-1) // 50 + 1`,即 section 序号 |
| `zh.stem` | `cn_question` | 中文题干 |
| `zh.options[]` | `cn_options{}` | 由数组转成 `{A: text,...}` |
| `en.stem` | `en_question` | 英文题干 |
| `en.options[]` | `en_options{}` | 同上 |
| `answer` | `answer` | `["A"]` 或 `["A","C"]` |
| `en.explanation` | `comments[]` | 按段落 / `Option X` / `Reference` 自动切分 |
| —(无数据) | `votes` | 空对象;CLF02 有但 SAA 上游不提供 |
