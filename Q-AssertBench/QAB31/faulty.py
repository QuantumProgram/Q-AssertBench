from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit_aer import AerSimulator
from math import pi, floor, sqrt


class GroverBenchmark:
    """
    QAB-31 FAULTY: Grover's Algorithm with missing diffuser.
    The oracle correctly marks the target, but amplitude amplification is disabled.
    """

    def __init__(self, shots=4096):
        self.n = 15
        self.target = "101010101010101"
        self.shots = shots

        self.backend = AerSimulator()
        self.qr = QuantumRegister(self.n, "q")
        self.anc = QuantumRegister(self.n - 2, "anc")
        self.cr = ClassicalRegister(self.n, "c")
        self.circuit = QuantumCircuit(self.qr, self.anc, self.cr)

        self.counts = None

    def apply_oracle(self):
        for i, bit in enumerate(self.target):
            if bit == '0':
                self.circuit.x(self.qr[i])
        self.circuit.h(self.qr[self.n - 1])
        self.circuit.mcx(
            control_qubits=self.qr[: self.n - 1],
            target_qubit=self.qr[self.n - 1],
            ancilla_qubits=self.anc,
            mode='v-chain'
        )
        self.circuit.h(self.qr[self.n - 1])
        for i, bit in enumerate(self.target):
            if bit == '0':
                self.circuit.x(self.qr[i])

    def apply_diffuser(self):
        for q in self.qr:
            self.circuit.h(q)
            self.circuit.x(q)
        self.circuit.h(self.qr[self.n - 1])
        self.circuit.mcx(
            control_qubits=self.qr[: self.n - 1],
            target_qubit=self.qr[self.n - 1],
            ancilla_qubits=self.anc,
            mode='v-chain'
        )
        self.circuit.h(self.qr[self.n - 1])
        for q in self.qr:
            self.circuit.x(q)
            self.circuit.h(q)

    def build_circuit(self):
        self.circuit.h(self.qr)
        num_iterations = min(10, floor(pi / 4 * sqrt(2 ** self.n)))
        for _ in range(num_iterations):
            self.apply_oracle()
            # diffuser intentionally skipped
        self.circuit.measure(self.qr, self.cr)

    def run(self):
        self.build_circuit()
        compiled = transpile(self.circuit, self.backend)
        job = self.backend.run(compiled, shots=self.shots)
        result = job.result()
        self.counts = result.get_counts()
        return self.counts

    def summarize_results(self):
        total = sum(self.counts.values())
        sorted_counts = sorted(self.counts.items(), key=lambda x: -x[1])
        print("\nTop 10 Measured States:")
        for bitstring, count in sorted_counts[:10]:
            prob = count / total
            print(f"{bitstring}: {count} ({prob:.3%})")

        target_count = self.counts.get(self.target, 0)
        target_prob = target_count / total
        print(f"\n[INFO] Target bitstring: {self.target}")
        print(f"[INFO] Target count: {target_count} ({target_prob:.3%})")
        return target_prob


if __name__ == "__main__":
    grover = GroverBenchmark()
    output = grover.run()
    grover.summarize_results()
