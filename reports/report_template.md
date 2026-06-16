# TLE/SGP4 轨道预报误差的统计分析

作者：  
课程：数理统计  
日期：  

## 摘要

本文基于公开 TLE 编目数据与 SGP4 传播模型，研究空间目标在 1 天、3 天和 7 天预报时长下的位置误差分布及其增长规律。以较早历元 TLE 作为预报初值，将其传播到未来目标时刻；以目标时刻附近的新 TLE 传播结果作为近似参考轨道，计算三维位置误差。进一步使用 Percentile Bootstrap 与 BCa Bootstrap 对误差统计量给出置信区间，并与 Gaussian 近似区间比较。最后，采用 ANOVA 与 Kruskal-Wallis 检验比较 LEO、MEO、GEO 三类轨道目标的误差差异。

## 1. 研究背景

TLE 是目前最广泛使用的公开空间目标轨道根数格式，配合 SGP4 模型可以快速预报卫星位置。然而，TLE 是基于观测数据拟合得到的平均轨道根数，并非高精度动力学轨道，预报误差会随时间积累。本文关注如下问题：

1. 预报 1 天、3 天、7 天后，三维位置误差有多大？
2. 误差随预报时间如何增长？
3. LEO、MEO、GEO 三类轨道的误差增长规律是否存在显著差异？
4. Bootstrap 置信区间与 Gaussian 近似置信区间有何差别？

## 2. 数据来源与预处理

数据来源包括：

- CelesTrak 当前 GP/TLE 数据快照；
- Space-Track `gp_history` 历史 TLE 数据。

原始 TLE 文件被解析为如下标准字段：

- NORAD 编号；
- 卫星名称；
- TLE line 1、line 2；
- TLE 历元；
- 平均运动、偏心率、轨道周期、近地点高度、远地点高度；
- 轨道类型：LEO、MEO、GEO。

轨道类型划分规则如下：

```text
LEO: period < 225 min 或 perigee < 2000 km
MEO: 225 min <= period < 1200 min
GEO: 1200 min <= period <= 1600 min 且 apogee 约在 30000-50000 km
```

## 3. 误差计算方法

对同一 NORAD 目标，设较早 TLE 为 \(T_i\)，其历元为 \(t_i\)。对预报时长 \(\Delta t \in \{1,3,7\}\) 天，目标时刻为：

```math
t^\* = t_i + \Delta t
```

将 \(T_i\) 用 SGP4 传播到 \(t^\*\)，得到预报位置：

```math
\mathbf r_{\text{pred}}(t^\*) = \mathrm{SGP4}(T_i, t^\*)
```

选择同一目标在 \(t^\*\) 附近的新 TLE \(T_j\) 作为参考，并传播到同一目标时刻：

```math
\mathbf r_{\text{ref}}(t^\*) = \mathrm{SGP4}(T_j, t^\*)
```

三维位置误差定义为：

```math
E(\Delta t) = \left\|\mathbf r_{\text{pred}}(t^\*) - \mathbf r_{\text{ref}}(t^\*)\right\|_2
```

同时将误差向量分解到 RIC 坐标系：

- R：径向；
- I：沿迹方向；
- C：轨道面法向。

## 4. 协方差传播

误差向量记为：

```math
\mathbf e(t) = \mathbf r_{\text{pred}}(t) - \mathbf r_{\text{ref}}(t)
```

对每个轨道类型和预报时长，估计经验协方差矩阵：

```math
\hat\Sigma(\Delta t) = \operatorname{Cov}[\mathbf e(\Delta t)]
```

理论协方差传播形式为：

```math
\Sigma(\Delta t) = \Phi(\Delta t)\Sigma_0\Phi(\Delta t)^T + Q(\Delta t)
```

其中 \(\Phi(\Delta t)\) 是状态转移矩阵，\(Q(\Delta t)\) 是过程噪声协方差。本文实现中给出两类经验协方差表：

- TEME 坐标系下的误差协方差；
- RIC 坐标系下的误差协方差。

在没有额外动力学线性化模型时，采用 \(\Phi=I\) 作为经验基线，估计：

```math
\hat Q(\Delta t) = \hat\Sigma(\Delta t) - \hat\Sigma(\Delta t_0)
```

## 5. 误差增长律拟合

分别拟合线性模型与幂律模型。

线性模型：

```math
E(t) = \alpha + \beta t + \varepsilon
```

幂律模型：

```math
E(t) = a t^b
```

对幂律模型取对数：

```math
\log E(t) = \log a + b\log t
```

比较不同轨道类型下的 \(a\)、\(b\)、\(R^2\)，判断误差增长速度差异。

## 6. Bootstrap 置信区间

对每个“轨道类型 × 预报时长”的误差样本，估计如下统计量：

- 均值误差；
- 中位数误差；
- RMSE。

采用三种区间：

1. Gaussian 近似区间；
2. Percentile Bootstrap 区间；
3. BCa Bootstrap 区间。

记 Bootstrap 重采样统计量为 \(\hat\theta^\*_b\)，Percentile 区间为：

```math
\left[
Q_{\alpha/2}(\hat\theta^\*),
Q_{1-\alpha/2}(\hat\theta^\*)
\right]
```

BCa 区间进一步使用偏差修正项和加速度项，适合偏态误差分布。

## 7. 轨道类型差异检验

对每个预报时长分别检验 LEO、MEO、GEO 的误差分布差异。

若满足近似正态与方差齐性，可参考单因素 ANOVA：

```math
H_0: \mu_{\text{LEO}}=\mu_{\text{MEO}}=\mu_{\text{GEO}}
```

考虑到 TLE 误差通常偏态且可能有长尾，本文同时采用 Kruskal-Wallis 非参数检验：

```math
H_0: F_{\text{LEO}}=F_{\text{MEO}}=F_{\text{GEO}}
```

若整体检验显著，再使用 Mann-Whitney U 两两比较，并进行 Holm 多重检验校正。

## 8. 实验结果

### 8.1 误差描述统计

填入 `outputs/tables/summary.csv` 的主要结果。

| 轨道类型 | 预报天数 | 样本量 | 均值/km | 中位数/km | RMSE/km | 95%分位/km |
|---|---:|---:|---:|---:|---:|---:|
| LEO | 1 |  |  |  |  |  |
| LEO | 3 |  |  |  |  |  |
| LEO | 7 |  |  |  |  |  |
| MEO | 1 |  |  |  |  |  |
| MEO | 3 |  |  |  |  |  |
| MEO | 7 |  |  |  |  |  |
| GEO | 1 |  |  |  |  |  |
| GEO | 3 |  |  |  |  |  |
| GEO | 7 |  |  |  |  |  |

插入图：

```text
outputs/figures/error_boxplot_by_orbit_horizon.png
outputs/figures/error_distribution_log10.png
```

### 8.2 误差增长律

填入 `outputs/tables/growth_fit.csv` 的拟合结果。

| 轨道类型 | 模型 | 参数 | 参数值 | R² |
|---|---|---|---:|---:|
| LEO | power_law | a, b |  |  |
| MEO | power_law | a, b |  |  |
| GEO | power_law | a, b |  |  |

插入图：

```text
outputs/figures/error_growth_median_iqr.png
```

### 8.3 Bootstrap 与 Gaussian 区间比较

填入 `outputs/tables/bootstrap_ci.csv` 的结果。

重点讨论：

- 误差分布是否偏态；
- BCa 区间是否明显不对称；
- Gaussian 区间是否低估长尾不确定性。

插入图：

```text
outputs/figures/ci_gaussian_vs_bootstrap.png
```

### 8.4 轨道类型差异检验

填入 `outputs/tables/group_tests.csv` 与 `outputs/tables/pairwise_mannwhitney_holm.csv`。

| 预报天数 | ANOVA p值 | Kruskal-Wallis p值 | 结论 |
|---:|---:|---:|---|
| 1 |  |  |  |
| 3 |  |  |  |
| 7 |  |  |  |

## 9. 讨论

可从以下角度讨论：

- LEO 误差可能受大气阻力、BSTAR、空间天气影响更明显；
- MEO 目标通常受大气阻力影响较小，但长期相位误差仍会积累；
- GEO 目标可能受定点保持、机动、东西漂移影响；
- TLE 对机动目标和近期变轨目标的预报误差可能出现异常长尾；
- 新 TLE 本身并非真值，因此本文误差是“旧 TLE 预报相对于新 TLE 后验轨道”的近似误差。

## 10. 结论

总结三点：

1. 1/3/7 天误差量级；
2. 误差增长律及不同轨道类型差异；
3. Bootstrap 相比 Gaussian 近似的优势。

## 参考文献与数据链接

1. CelesTrak GP Data: https://celestrak.org/NORAD/elements/
2. CelesTrak GP query documentation: https://celestrak.org/NORAD/documentation/gp-data-formats.php
3. Space-Track: https://www.space-track.org/
4. Vallado et al., Revisiting Spacetrack Report #3.
5. Python `sgp4` package documentation.
