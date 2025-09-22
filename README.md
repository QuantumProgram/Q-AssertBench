# Q-AssertBench
Q-AssertBench is an open benchmark designed to evaluate the ability of large language models (LLMs) to generate executable assertions for quantum programs. It provides a curated dataset of 31 tasks covering basic gate operations, state preparation routines, and representative quantum algorithms. 
Each task is paired with:
a quantum program implemented in Qiskit,
a natural language prompt describing the intended correctness property,
an expert-authored gold assertion, and
a set of faulty program variants for robustness testing.

# Dataset Structure
The repository is organized as follows:
Q-AssertBench/
├── QAB01/
│   ├── program.py          # Quantum program in Qiskit
│   ├── prompt.py           # Natural language prompt describing the property
│   ├── gold_assertion.py   # Expert-authored reference assertion
│   └── faulty.py           # Faulty program variants for robustness testing
├── QAB02/
├── QAB03/
├── QAB04/
├── QAB05/
...
samples_json/
samples_yaml/
Q-AssertBench.json
Q-AssertBench.yaml

Q-AssertBench/ is the main dataset directory. Each subdirectory (e.g., QAB01, QAB02, …) is a benchmark task.samples_json/ and samples_yaml/ are example datasets provided in JSON and YAML formats, which make integration with external pipelines easier.

Q-AssertBench.json and Q-AssertBench.yaml are the complete benchmark specifications provided in JSON and YAML formats.
