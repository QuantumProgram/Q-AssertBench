## Q-AssertBench
Q-AssertBench is an open benchmark designed to evaluate the ability of large language models (LLMs) to generate executable assertions for quantum programs. It provides a curated dataset of 31 tasks covering basic gate operations, state preparation routines, and representative quantum algorithms.

Each task is paired with:

A quantum program implemented in Qiskit;
a natural language prompt describing the intended correctness property;
an expert-authored gold assertion;
a set of faulty program variants for robustness testing.

## Dataset Structure
The benchmark dataset is organized as follows:
```text
Q-AssertBench/
├── QAB01/
│   ├── program.py
│   ├── prompt.py
│   ├── gold_assertion.py
│   └── faulty.py
├── QAB02/
├── QAB03/
├──...
samples_json/
├── QAB01.json
├── QAB02.json
├──...
samples_yaml/
├── QAB01.yaml
├── QAB02.yaml
├──...
Q-AssertBench.json
Q-AssertBench.yaml
```
Q-AssertBench/ is the main dataset directory. Each subdirectory (e.g., QAB01, QAB02, …) is a benchmark task. 

samples_json/ and samples_yaml/ are example datasets provided in JSON and YAML formats, which make integration with external pipelines easier.

Q-AssertBench.json and Q-AssertBench.yaml are the complete benchmark specifications provided in JSON and YAML formats.

## Usage

Q-AssertBench can be used to systematically evaluate the ability of large language models (LLMs) to generate executable assertions for quantum programs.

1. Input to the Model

For each benchmark task (QABxx/):

program.py is the quantum program written in Qiskit.

prompt.py is the natural language description of the intended correctness property.

To evaluate an LLM, provide the model with the program and the corresponding prompt.

Interaction with the model may be conducted via chat (e.g., ChatGPT, Claude, Gemini) or via API calls.

It is recommended to append an assertion format hint to the prompt for consistency.
Templates for such hints are available in Q-AssertBench.json.

2. Model Output

The LLM is expected to produce an assertion in Qiskit/Python code that enforces the property described in the prompt.

3. Evaluation Methods

Generated assertions can be evaluated along multiple dimensions:

Execution Test: Run the assertion within the original program to verify that it executes without error.

Comparison with Gold Assertion: Compare the generated assertion with the expert-authored gold_assertion.py.

Mutation Testing: Run the assertion against the faulty.py variants of the program to test whether it can detect violations of the intended property.

4. Integration

JSON/YAML Interface: The complete benchmark specifications are provided in Q-AssertBench.json and Q-AssertBench.yaml, which can be easily parsed in evaluation pipelines.

Flexible Use: Depending on your experimental setup, you can use Q-AssertBench in an interactive setting (chat-based) or an automated pipeline (API-based).
