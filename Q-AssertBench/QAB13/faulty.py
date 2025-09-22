from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer

class DeutschJozsaCircuit:
    def __init__(self, shots=1024):
        """
        Faulty version: Oracle implemented as constant function f(x)=0
        This breaks the expected balanced behavior.
        """
        self.shots = shots
        self.circuit = QuantumCircuit(3, 2)
        self.backend = Aer.get_backend("qasm_simulator")

    def apply_oracle(self):
        # ❌ Faulty: constant oracle, do nothing
        pass

    def build_circuit(self):
        # Step 1: Initialize ancilla qubit in |1⟩
        self.circuit.x(2)

        # Step 2: Apply Hadamard to all qubits
        for i in range(3):
            self.circuit.h(i)

        # Step 3: Oracle (faulty: constant)
        self.apply_oracle()

        # Step 4: Apply Hadamard to input qubits
        self.circuit.h(0)
        self.circuit.h(1)

        # Step 5: Measure only the input qubits
        self.circuit.measure(0, 0)
        self.circuit.measure(1, 1)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()
        return counts

if __name__ == "__main__":
    circuit_runner = DeutschJozsaCircuit()
    output = circuit_runner.run()
    print("Measurement Counts (Faulty):", output)
