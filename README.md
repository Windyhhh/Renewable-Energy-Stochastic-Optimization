# ⚡ Renewable Energy Stochastic Optimization | 可再生能源交易多阶段随机优化模型

> **Multi-stage stochastic optimization model for renewable energy trading. Scenario tree generation, forward pricing, risk measures (CVaR), and comprehensive case studies. Optimize energy trading decisions under uncertainty.**
>
> 可再生能源交易多阶段随机优化模型。场景树生成、远期定价、风险度量（CVaR）和完整案例研究。在不确定性下优化能源交易决策。

---

## 🌟 Features | 核心特性

- **Multi-stage Stochastic Programming** — Optimize decisions across multiple time stages
- **Scenario Tree Generation** — Generate representative uncertainty scenarios
- **Forward Pricing** — Energy forward contract pricing models
- **Risk Measures** — CVaR (Conditional Value-at-Risk) and other risk metrics
- **Data Generation** — Synthetic renewable energy data generator
- **Case Studies** — Complete example implementations
- **Comprehensive Testing** — Basic and comprehensive test suites

---

## 📁 Project Structure | 项目结构

```
Renewable-Energy-Stochastic-Optimization/
├── src/
│   ├── optimization.py          # Core stochastic optimization
│   ├── scenario_tree.py         # Scenario tree generation
│   ├── forward_pricing.py       # Forward contract pricing
│   ├── risk_measures.py         # Risk measures (CVaR, etc.)
│   ├── data_generation.py       # Synthetic data generation
│   ├── utils.py                 # Utility functions
│   └── __init__.py
├── examples/
│   ├── simple_example.py        # Simple usage example
│   └── case_study.py            # Complete case study
├── data/
│   └── input_data.json          # Sample input data
├── comprehensive_test.py         # Comprehensive test suite
├── test_basic.py                 # Basic tests
├── install_dependencies.py       # Dependency installer
├── install_dependencies.bat
├── run_case_study.bat
├── run_simple_example.bat
├── requirements.txt
├── 可再生能源交易优化模型_爆款博客.md
└── README.md
```

---

## 🚀 Quick Start | 快速开始

```bash
# Install dependencies
pip install -r requirements.txt
# or: python install_dependencies.py

# Run simple example
python examples/simple_example.py
# or: run_simple_example.bat

# Run case study
python examples/case_study.py
# or: run_case_study.bat

# Run tests
python test_basic.py
python comprehensive_test.py
```

---

## 🔬 Methodology | 方法

### Scenario Tree | 场景树

Generate a scenario tree representing possible future outcomes of renewable energy production and prices:
- **Stage 0**: Current state (here-and-now decisions)
- **Stage 1**: First uncertainty realization
- **Stage N**: Final uncertainty realization

### Stochastic Optimization | 随机优化

Minimize expected cost + risk penalty:

```
min  Σ_s p_s · Cost(x_s) + λ · CVaR_α(Cost)
s.t.  x_s ∈ X (feasible set)
      non-anticipativity constraints
```

### Risk Measures | 风险度量

- **CVaR_α**: Conditional Value-at-Risk at confidence level α
- **Variance**: Standard deviation of costs
- **Downside Risk**: Only penalize unfavorable outcomes

---

## 📊 Applications | 应用场景

- **Wind/Solar Power Trading** — Optimize bidding strategy under production uncertainty
- **Energy Storage Operation** — Charge/discharge scheduling with price uncertainty
- **Forward Contract Hedging** — Optimal forward position sizing
- **Portfolio Optimization** — Diversify across multiple renewable assets
- **Risk Management** — Balance expected profit against downside risk

---

## 📚 References | 参考文献

1. **Shapiro, A., Dentcheva, D., & Ruszczyński, A.** (2014). *Lectures on stochastic programming: modeling and theory.* SIAM.
2. **Rockafellar, R. T., & Uryasev, S.** (2000). *Optimization of conditional value-at-risk.* Journal of Risk, 2(3), 21-42.
3. **Conejo, A. J., et al.** (2010). *Decision making under uncertainty in electricity markets.* Springer.

---

## 📄 License | 许可证

MIT License.

---

<div align="center">

**Built with ⚡ for energy systems optimization**

[GitHub](https://github.com/Windyhhh/Renewable-Energy-Stochastic-Optimization)

</div>
