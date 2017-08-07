"""Example of use of the AvoidPAttern specification"""

from dnachisel import (DnaOptimizationProblem, random_dna_sequence,
                       reverse_complement, AvoidHairpins)


def test_basics():
    random_sequences = [random_dna_sequence(30) for i in range(10)]

    full_sequence = "".join([
        seq
        for sequence in random_sequences
        for seq in (random_dna_sequence(50),
                    sequence,
                    random_dna_sequence(50),
                    reverse_complement(sequence),
                    random_dna_sequence(50))
    ])

    problem = DnaOptimizationProblem(full_sequence,
                                     constraints=[AvoidHairpins()])
    assert not problem.all_constraints_pass()
    problem.resolve_constraints(progress_bars=2)
    assert problem.all_constraints_pass()