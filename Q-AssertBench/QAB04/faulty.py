from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
import numpy as np

class PauliGatesCircuit:
    def __init__(self, shots=1024):
        self.shots = shots
        self.circuit = QuantumCircuit(1, 1)
        self.backend = Aer.get_backend("qasm_simulator")

    def build_circuit(self):
        # Faulty: Use wrong angle to get probability distribution
        self.circuit.ry(1 * np.pi / 4, 0)

        self.circuit.measure(0, 0)

    def run(self):
        self.build_circuit()
        transpiled = transpile(self.circuit, self.backend)
        job = self.backend.run(transpiled, shots=self.shots)
        result = job.result()
        counts = result.get_counts()

        return counts

if __name__ == "__main__":
    circuit_runner = PauliGatesCircuit()
    output = circuit_runner.run()
    print("Measurement Counts:", output)
