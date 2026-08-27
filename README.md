<div align="center">

# ⚡ Renewable-Energy-Stochastic-Optimization

### Multi-stage stochastic optimization for energy trading.

Scenario trees, forward pricing and CVaR risk measures for renewable-energy trading.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

</div>

---

**Renewable-Energy-Stochastic-Optimization** solves multi-stage **stochastic optimization** for energy trading — using **scenario trees**, **forward pricing** and **CVaR** risk measures.

> [!NOTE]
> 中文项目：多阶段随机优化能源交易——场景树、远期定价、CVaR 风险度量。

---

## Quickstart

```bash
git clone https://github.com/Windyhhh/Renewable-Energy-Stochastic-Optimization.git
cd Renewable-Energy-Stochastic-Optimization

pip install -r requirements.txt

# simple example
python examples/simple_example.py

# case study
python examples/case_study.py
```

Or use the `.bat` launchers (`run_simple_example.bat`, `run_case_study.bat`).

---

## Features

- **Scenario trees** — multi-stage uncertainty modeling.
- **Forward pricing** — futures-style pricing module.
- **CVaR risk** — coherent risk measures.

---

## Project Structure

```
Renewable-Energy-Stochastic-Optimization/
├── src/
│   ├── data_generation.py
│   ├── optimization.py
│   ├── forward_pricing.py
│   └── risk_measures.py
├── examples/               # simple_example, case_study
├── data/input_data.json
└── comprehensive_test.py
```

---

## License

MIT — free to use, modify and distribute.
