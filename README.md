# Fuzzy Controllers for Dynamic Configuration of Messaging Systems

## Overview

This project implements Fuzzy Controllers combined with Genetic Algorithms to dynamically configure message brokers in distributed systems that use the publisher/subscriber model. The solution addresses the inefficiencies caused by manual tuning in traditional control systems, which often assume a linear relationship between system parameters and performance. By using fuzzy logic, this project adapts to non-linear environments and provides an automated solution for message broker configuration.

## Features

- **Dynamic Configuration**: Fuzzy controllers automatically adjust message broker parameters based on real-time system behavior.
- **Genetic Algorithm Optimization**: Optimizes fuzzy controller parameters without manual intervention, ensuring the system adapts to various workloads and configurations.
- **Performance Metrics**: Comprehensive evaluation using throughput metrics, comparing fuzzy controllers against traditional control strategies.
- **Test Environment**: Integrated with RabbitMQ (or other message brokers) to simulate real-world distributed system conditions.

## Project Structure

```bash
├── app/
│   ├── outputs/                 # Output folder for experiment results
│   ├── pc_changes.csv           # CSV file for tracking changes in PC (prefetch count)
│   ├── run_experiments.sh       # Shell script to run the experiment suite
│   └── subscriber.py            # Main subscriber script
├── controller/
│   ├── AsTAR/
│   │   └── AsTAR.py             # Implementation of AsTAR controller
│   ├── fuzzy/
│   │   ├── first_check.csv      # Initial check for fuzzy controller validation
│   │   ├── fuzzy_controller.py  # Fuzzy logic controller implementation
│   │   └── sigma_optimization.py# Sigma optimization for fuzzy controller
│   ├── hpa/
│   │   └── hpa_controller.py    # HPA controller
│   └── rules/
│       ├── const.py             # Constants for rule generation
│       ├── results.csv          # Final results after running rules
│       ├── rules_generator.py   # Rule generation logic
│       └── results_old.csv      # Previous result set
├── shared/
│   ├── shared.py                # Shared utility functions for the controllers
├── utils/
│   ├── core_functions.py        # Core utility functions for the project
└── README.md                    # Project documentation

## Customization

- Fuzzy Logic Rules: You can modify the fuzzy logic rules and membership functions in controller/fuzzy/fuzzy_controller.py to fit different system requirements.
- Adjusting Genetic Algorithm Parameters: Customize parameters such as population size, mutation rate, and generations in controller/fuzzy/sigma_optimization.py to control the optimization process.

## Contributing

Contributions are welcome! Please feel free to submit issues, fork the repository, and open pull requests.
