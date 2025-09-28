from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import numpy as np


class ShorLargeCircuitFaulty:
    def __init__(self, N=15, a=7, shots=1024):
        self.N = N
        self.a = a
        self.n_count = 8
        self.work_qubits = 7
        self.total_qubits = self.n_count + self.work_qubits
        self.backend = AerSimulator()
        self.shots = shots
        self.circuit = None
        self.counts = None

    def build_circuit(self):
        qc = QuantumCircuit(self.total_qubits, self.n_count)

        for q in range(self.n_count):
            qc.h(q)

        # Faulty: Remove all entanglement (missing QPE-like CX structure)
        # (This simulates a circuit with structural fault in phase estimation)

        for j in range(self.n_count // 2):
            qc.swap(j, self.n_count - j - 1)

        for j in range(self.n_count):
            qc.h(j)
            for k in range(j + 1, self.n_count):
                angle = -np.pi / (2 ** (k - j))
                qc.cp(angle, k, j)

        for i in range(self.n_count):
            qc.measure(i, i)

        self.circuit = qc

    def run(self):
        self.build_circuit()
        compiled = transpile(self.circuit, self.backend)
        job = self.backend.run(compiled, shots=self.shots)
        result = job.result()
        self.counts = result.get_counts()
        return self.counts


if __name__ == "__main__":
    program = ShorLargeCircuitFaulty()
    result = program.run()
    print("Faulty Measurement Results:")
    for b, c in result.items():
        print(f"{b}: {c}")
