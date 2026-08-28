<div align="center">

# ⚡ Renewable-Energy-Stochastic-Optimization

### Multi-stage stochastic optimization for energy trading.

Scenario trees, forward pricing and CVaR risk measures — with solving time optimized from minutes to seconds.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)

</div>

---

**Renewable-Energy-Stochastic-Optimization** models **renewable-energy trading** as a **multi-stage stochastic optimization** problem — using **scenario trees**, **forward pricing** and **CVaR** risk measures — with a modular, scalable Python implementation whose solving time was cut from minutes to seconds.

> [!NOTE]
> 中文项目：可再生能源交易多阶段随机优化模型——场景树 + 远期定价 + CVaR 风险度量，模块化实现，求解效率分钟级→秒级。

---

## Features

- **Multi-stage stochastic model** — scenario-tree based energy trading.
- **Forward pricing** — futures-style pricing module.
- **CVaR risk** — coherent risk measures for volatile markets.
- **Performance** — solving time optimized minutes → seconds.
- **Modular & extensible** — adaptable to scale / scenario.

---

## Quickstart

```bash
git clone https://github.com/Windyhhh/Renewable-Energy-Stochastic-Optimization.git
cd Renewable-Energy-Stochastic-Optimization

pip install -r requirements.txt

python examples/simple_example.py   # basic run
python examples/case_study.py       # full case study
```

Or use the `.bat` launchers (`run_simple_example.bat`, `run_case_study.bat`).

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
