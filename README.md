# TLE/SGP4 预报误差统计分析项目

本项目用于完成数理统计大作业：用历史 TLE 作为预报初值，借助 SGP4 传播到 1/3/7 天后，并用目标时刻附近的新 TLE 作为近似参考轨道，统计位置预报误差、误差增长律、Bootstrap 置信区间，以及不同轨道类型的差异检验。

## 目录结构

```text
scripts/                 命令行入口
src/tle_accuracy/         核心 Python 模块
data/raw/                 原始 TLE/GP 数据
data/interim/             标准化后的 TLE 记录
data/processed/           误差明细表
outputs/tables/           统计表格
outputs/figures/          图表
reports/                  报告模板
tests/                    基础测试
```

## 1. 安装环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 下载数据

### 2.1 CelesTrak 当前快照

CelesTrak 当前 GP 数据是直接 HTTP GET 下载。脚本显式指定 `FORMAT=TLE`，避免接口默认格式变化影响解析。

```bash
python scripts/download_tle.py \
  --source celestrak \
  --groups active geo gps-ops \
  --format TLE
```

注意：单次 CelesTrak 当前快照通常每个目标只有一组 TLE，不能独立形成 1/3/7 天误差样本。可以每天运行一次该命令累积快照，或使用 Space-Track 历史数据。

### 2.2 Space-Track 历史数据

先注册 Space-Track 账号，然后设置环境变量：

```bash
export SPACE_TRACK_IDENTITY="your-email@example.com"
export SPACE_TRACK_PASSWORD="your-password"
```

项目已提供一个平衡样本文件 `data/catalog_ids.txt`，每行一个 NORAD 编号，共 75 个目标，LEO/MEO/GEO 各 25 个。对应的名称、轨道类型和来源分组见 `data/catalog_ids_metadata.csv`。然后下载历史 `gp_history`：

```bash
python scripts/download_tle.py \
  --source spacetrack \
  --ids-file data/catalog_ids.txt \
  --start 2025-01-01 \
  --end 2025-03-31
```

也可以直接传入少量编号：

```bash
python scripts/download_tle.py \
  --source spacetrack \
  --ids 25544 43013 43226 \
  --start 2025-01-01 \
  --end 2025-03-31
```

## 3. 计算 SGP4 预报误差

```bash
python scripts/compute_errors.py \
  --input data/raw \
  --horizons 1 3 7 \
  --max-reference-offset-hours 12
```

输出：

- `data/interim/tle_records.csv`：标准化 TLE 记录
- `data/processed/errors.csv`：误差明细，包含 TEME 三轴误差、RIC 径向/沿迹/法向误差、三维位置误差

误差定义：

```text
e(t) = r_old_TLE_SGP4(t) - r_reference_TLE_SGP4(t)
position_error = ||e(t)||_2
```

参考 TLE 的历元允许与目标时间相差不超过 `--max-reference-offset-hours`。

## 4. Bootstrap、增长律、统计检验与协方差

```bash
python scripts/analyze_errors.py \
  --errors data/processed/errors.csv \
  --n-bootstrap 5000
```

输出表格：

- `outputs/tables/summary.csv`：均值、中位数、RMSE、分位数
- `outputs/tables/bootstrap_ci.csv`：Gaussian、Percentile Bootstrap、BCa Bootstrap 置信区间
- `outputs/tables/growth_fit.csv`：线性增长律与幂律增长律
- `outputs/tables/group_tests.csv`：ANOVA、Kruskal-Wallis、Levene 方差齐性检验
- `outputs/tables/pairwise_mannwhitney_holm.csv`：两两 Mann-Whitney U 检验与 Holm 校正
- `outputs/tables/covariance_ric.csv`、`covariance_teme.csv`：误差协方差矩阵
- `outputs/tables/process_noise_identity_*.csv`：在 `Phi=I` 基线下估计的过程噪声矩阵

## 5. 生成图表

```bash
python scripts/generate_plots.py
```

输出：

- `outputs/figures/error_boxplot_by_orbit_horizon.png`
- `outputs/figures/error_growth_median_iqr.png`
- `outputs/figures/error_distribution_log10.png`
- `outputs/figures/ci_gaussian_vs_bootstrap.png`

## 6. 一键运行

已有历史 TLE 数据后：

```bash
python scripts/run_pipeline.py \
  --raw data/raw \
  --horizons 1 3 7 \
  --n-bootstrap 5000
```

## 7. 轨道类型划分

脚本默认按 TLE 平均运动估算轨道周期：

- `LEO`：周期小于 225 分钟，或近地点高度小于 2000 km
- `MEO`：周期在 225 到 1200 分钟之间
- `GEO`：周期在 1200 到 1600 分钟之间，且远地点高度约在 30000 到 50000 km
- `OTHER`：不属于上述类别

`compute_errors.py` 默认只保留 `LEO MEO GEO`，如需保留全部类别，可传入：

```bash
python scripts/compute_errors.py --input data/raw --orbit-types
```

## 8. 报告

见 `reports/报告.md`。
