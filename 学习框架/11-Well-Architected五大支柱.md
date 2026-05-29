# 11 · Well-Architected 五大支柱 — SAA 的"答题宪法"

> 这五个支柱不是抽象口号,它是 AWS 用来"打分"你架构方案的尺。**每道 SAA 题背后都是其中一个或多个支柱在被问。**

## 一、五大支柱总览

| 支柱 | 关键词 | 工具集 |
|------|--------|--------|
| 1️⃣ **Operational Excellence**(运维卓越) | 自动化、IaC、可观测、可演进 | CloudWatch、CloudTrail、CloudFormation、SSM |
| 2️⃣ **Security**(安全) | 身份、加密、审计、深度防御 | IAM、KMS、GuardDuty、Shield、WAF |
| 3️⃣ **Reliability**(可靠性) | 多 AZ、自动恢复、限流降级 | ASG、Multi-AZ、Route 53、SQS |
| 4️⃣ **Performance Efficiency**(性能效率) | 选对服务、用对实例族、缓存 | ElastiCache、CloudFront、Right-sizing |
| 5️⃣ **Cost Optimization**(成本优化) | 按需付费、关停闲置、采购优化 | Spot、Savings Plans、Lifecycle |

(2021 年后加了第 6 个:**Sustainability** — 可持续性,SAA 偶有涉及)

## 二、识别题目背后的支柱(超级实用)

| 题目关键词 | 主要支柱 |
|------------|---------|
| "高可用 / failover / RTO RPO / 多 AZ" | **Reliability** |
| "防护 / 加密 / 合规 / 审计 / 身份" | **Security** |
| "性能 / 延迟 / 吞吐 / 缓存 / scale" | **Performance Efficiency** |
| "便宜 / 优化成本 / 闲置 / right-size" | **Cost Optimization** |
| "运维负担 / fully managed / automation" | **Operational Excellence** |

⚠️ **大多数 SAA 题同时涉及 2-3 个支柱**,识别**主导支柱**就能锁定方向。

## 三、Reliability(可靠性)— 设计韧性

### 三层韧性原则

```
1. Foundations       Service Quotas、网络容量
        ↓
2. Workload Architecture   多 AZ、解耦、限流、bulkhead
        ↓
3. Change Management   滚动部署、IaC、自动恢复
```

### 高频考点

| 概念 | 一句话 |
|------|--------|
| **RPO**(Recovery Point Objective)| 能丢多久数据 |
| **RTO**(Recovery Time Objective)| 能停多久服务 |
| **Backup & Restore** | 最便宜,RTO 几小时,RPO 取决备份频率 |
| **Pilot Light** | DR Region 跑核心(DB)但不跑应用,RTO 10 分钟 |
| **Warm Standby** | DR Region 跑缩容版本,RTO 几分钟 |
| **Multi-Site Active-Active** | 两个 Region 都跑,RTO ~ 秒 |

### 四种 DR 策略 — 决策树

```
最便宜 ──────────────────────────── 最快恢复
Backup & Restore → Pilot Light → Warm Standby → Active-Active
```

| 题目说 | 答案 |
|--------|------|
| "最便宜的 DR,可接受小时级恢复" | **Backup & Restore** |
| "DB 跨 Region 复制,应用按需启动" | **Pilot Light** |
| "DR Region 平时跑小规模" | **Warm Standby** |
| "RTO < 1 分钟、RPO < 1 秒" | **Active-Active** + Aurora Global DB / DynamoDB Global Tables |

### 自动恢复模式

- **ASG + Multi-AZ ELB**:实例挂了自动起新的
- **EC2 Auto Recovery**(基于 CloudWatch):硬件故障自动迁
- **RDS Multi-AZ**:主挂了自动切到备
- **Route 53 Failover**:Region 级别切换

## 四、Security(安全)— 深度防御 5 层

(详见 [`08-安全与合规.md`](08-安全与合规.md))

```
            Identity → IAM, SSO, MFA, federation
                ↓
            Network → VPC, SG, NACL, WAF, Shield
                ↓
            Data    → KMS, S3 encryption, TLS, Macie
                ↓
            Detection → GuardDuty, Config, CloudTrail
                ↓
            Response → SNS, Lambda, Step Functions, IR
```

### 设计原则

- **最小权限**:能用 Role 就别用 User;能给具体 action 就别 `*`
- **静态加密 + 传输加密**(at rest + in transit)— **几乎每道安全题的答案都包含这两个**
- **不放凭证在代码里**:Secrets Manager / Parameter Store + IAM Role
- **分账户隔离环境**:Prod / Dev / Sandbox 独立账号

## 五、Performance Efficiency(性能效率)

### 四个维度的选择

| 维度 | 选项 |
|------|------|
| **计算** | EC2 / Lambda / ECS / Fargate / 实例族选择 |
| **存储** | 块 / 文件 / 对象,IOPS vs 吞吐 |
| **数据库** | SQL vs NoSQL vs 时序 vs 图 |
| **网络** | CloudFront / Global Accelerator / VPC Endpoints |

### 性能题的固定套路

```
1. 找瓶颈在哪一层?
2. 这一层有没有 AWS managed 服务可换?
3. 能不能加缓存 / CDN?
4. 能不能用更专用的服务(图、时序、流式)?
```

## 六、Cost Optimization(成本优化)

(详见 [`10-成本优化.md`](10-成本优化.md))

### 五大杠杆

1. **关停 / 缩容** — Auto Scaling、夜间停 EC2
2. **采购** — Savings Plans / Reserved / Spot
3. **架构** — Serverless、Right-sizing、Graviton
4. **数据生命周期** — S3 lifecycle、log retention
5. **流量** — CloudFront、Endpoint、同 AZ 调用

## 七、Operational Excellence(运维卓越)

| 概念 | 关键工具 |
|------|---------|
| **IaC**(代码即基础设施) | CloudFormation / CDK / Terraform |
| **可观测**(Observability) | CloudWatch / X-Ray / OpenSearch |
| **自动化运维** | SSM Automation / EventBridge + Lambda |
| **CI/CD** | CodePipeline / CodeBuild / CodeDeploy |
| **变更管理** | Change sets、deployment groups、Blue/Green |

### 题目套路

| 题目说 | 答案 |
|--------|------|
| "**多环境一致部署**" | **CloudFormation StackSets** |
| "**蓝绿部署 / canary**" | **CodeDeploy** + **Lambda alias** / ECS / Elastic Beanstalk |
| "运维人员故障定位慢" | **X-Ray + CloudWatch Logs Insights** |
| "**减少运维负担**" → 答案里**几乎一定**包含 | "**Serverless**" / "**managed service**" |

## 八、AWS Well-Architected Tool

- 控制台里给你一份"自测问卷",按 6 个支柱打分
- 输出"高风险问题"(HRI)
- 题目说"评估架构是否符合 best practice" → **Well-Architected Tool**

## 九、答题宪法 — 一句话送你

> **当你不确定时,挑那个"运维最少、最 managed、最 serverless、最便宜、最弹性"的选项。**

这一句话能帮你正确处理至少 30% 的题。

## 十、自查清单

- [ ] 我能在 5 秒内说出 5 大支柱
- [ ] 我能从题目关键词识别出主导支柱
- [ ] 我能区分 4 种 DR 策略的 RTO/RPO 排序
- [ ] 我知道 "深度防御 5 层" 的位置
- [ ] 我能背出 "运维卓越 = IaC + 可观测 + 自动化"

下一章:[`12-考前冲刺与答题套路.md`](12-考前冲刺与答题套路.md)
