from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
circ = QuantumCircuit(2, 2)
circ.h(0)
circ.cx(0, 1)
circ.measure([0, 1], [0, 1])
sim = AerSimulator()
result = sim.run(circ, shots=1024).result()
print("Total count for 00 and 11 are:", result.get_counts(circ))
