# 00 · 从 CLF 到 SAA — 你需要换一颗"架构师的脑子"

> 这一章不讲服务,只讲"考试的本质变了"。如果你只用 CLF 的方式刷 SAA,会卡在 60% 的瓶颈上不去。

## 一、考试问法的根本变化

| 维度 | CLF-C02(Practitioner) | SAA-C03(Associate) |
|------|------------------------|---------------------|
| 问题形态 | "X 是什么?" "谁负责 X?" | "在 A、B、C、D 中,**哪个方案最符合**约束 X、Y、Z?" |
| 选项差异 | 通常 1 对 3 错 | 经常 **2 个都对**,选**更好/更便宜/更弹性/运维更少**的那个 |
| 服务广度 | ≈ 50 个核心服务 | ≈ 100+ 服务,且要知道**组合**用法 |
| 关键词 | 共担责任、定价模型、Region/AZ | **operational overhead, MOST cost-effective, MINIMAL changes, MOST resilient** |
| 你的角色 | 云的"消费者" | 系统的"设计者" |

### 真题示例 — 感受一下题感差异

**CLF 风格**:
> 哪项 AWS 服务用于无服务器函数运行?  
> A. EC2  B. Lambda  C. ECS  D. Batch  → 显然 B

**SAA 风格**:
> 一家公司有一个每 15 分钟运行一次、约 2 秒完成的清洗任务。要求**运维最少**、**成本最低**,且不需要 SSH 访问。下列哪个方案**最**满足要求?  
> A. EC2 + cron + ASG  B. Lambda + EventBridge Schedule  C. ECS Fargate 任务  D. Step Functions  
> → 仍然是 Lambda,**但理由必须是**:无运维、毫秒级计费、与 EventBridge 原生集成。**B 和 D 都"能做"**,只是 D 杀鸡用牛刀,贵且多余。

**记住**:SAA 题里,**能不能做** 不是关键;**最适合** 才是。

## 二、SAA 选项里高频出现的"陷阱关键词"

学会识别这些词,你能在不知道答案时排除掉一半选项。

| 陷阱关键词 | 通常意味着什么 | 排除信号 |
|------------|----------------|----------|
| **manual** / 手动 / cron 脚本 | 运维高、不弹性 | 题目说 "operational overhead minimal" 时排除 |
| **EC2 / self-managed** | 要打补丁、要扩容 | 题目说 "fully managed" 时排除 |
| **NAT instance**(不是 NAT Gateway) | 单点故障、需自己运维 | 几乎永远是错误选项 |
| **重新设计/重写应用** | 改动太大 | 题目说 "minimal changes" 时排除 |
| **跨 Region 复制 + 反向同步** | 复杂、慢 | 大多数题目里都不是"最"优解 |
| **存到 EBS 然后 Snapshot 再恢复** | 多余的中间步骤 | 直接 S3 几乎总更好 |
| **Snowball** 用于日常 < TB 传输 | 大材小用 | 只有 PB 级别 + 网络差才该选 |
| **用 EC2 跑数据库** 而不是 RDS | 运维高 | 题目要"managed"时排除 |

## 三、SAA 的"四种问法母模板"

你会发现 1019 道题 95% 都套这四个模板:

### 模板 1:可用性 / 弹性
> "一个应用部署在单 AZ 的 EC2 上,公司要求**避免任何单点故障**……"

**答题套路**:
- 多 AZ + ASG + ALB(无状态服务)
- RDS Multi-AZ(数据库)
- S3(对象天然多 AZ)
- DynamoDB Global Tables(跨 Region)
- Route 53 健康检查 + Failover routing

### 模板 2:性能
> "查询数据库的请求延迟太高 / 大流量下 RDS CPU 100% ……"

**答题套路**:
- 读多写少 → **ElastiCache**(Redis / Memcached)
- 读多但要持久 → **RDS Read Replica**
- 写多 → **Aurora**(更高吞吐)或拆 **DynamoDB**
- 静态资源慢 → **CloudFront**
- 跨区域上传慢 → **S3 Transfer Acceleration** 或 **Multipart Upload**

### 模板 3:解耦 / 异步
> "前端请求峰值时后端处理不过来 / 一个服务挂了影响整条链路 ……"

**答题套路**:
- 削峰填谷 → **SQS**
- 一对多扇出 → **SNS**(或 SNS → SQS Fan-out)
- 事件驱动 / 跨服务 → **EventBridge**
- 工作流编排 → **Step Functions**
- 实时流式数据 → **Kinesis Data Streams**

### 模板 4:成本优化
> "成本太高 / 闲置资源 / 长期可预测负载 ……"

**答题套路**:
- 可预测的常年负载 → **Savings Plan / Reserved Instances**
- 容错性强的批处理 → **Spot Instances**
- 冷数据存储 → **S3 Intelligent-Tiering / Glacier**
- 短期低频任务 → **Lambda / Fargate**
- 闲置资源识别 → **Trusted Advisor / Cost Explorer**

## 四、学习节奏建议

### 看每一个服务时,问自己 5 个问题

1. **它解决了什么问题?**(没有它,我会怎样痛苦?)
2. **它的"对手"是谁?**(同类服务里,选它而不选别人的理由?)
3. **它的硬约束是什么?**(配额、最大 size、时延、强一致还是最终一致?)
4. **它的默认设置安全吗?**(默认是否公开、是否加密、是否多 AZ?)
5. **它怎么收费?**(按存储 / 按请求 / 按运行时长 / 数据出口?)

### 不要做的事

- ❌ 把每个服务的所有 feature 都背一遍(没必要)
- ❌ 死记每种实例族(只需知道大类:通用 M、计算 C、内存 R、存储 I/D、GPU P/G)
- ❌ 用看视频代替做题 + 复盘(视频带不来"做选择"的肌肉记忆)

### 必须做的事

- ✅ 每道错题写一句**归因**:我错是因为不知道 X 服务的 Y 特性 / 我没读到题目里 Z 关键词
- ✅ 用本仓库 `quiz-app` 的"错题"过滤器二刷
- ✅ 临考 1 周内,只做错题 + 模考

---

**下一章**:[`01-架构师的全局视图.md`](01-架构师的全局视图.md) — Region / AZ / VPC / Account 的全局结构,你将看到所有服务怎么"挂"在这张地图上。
