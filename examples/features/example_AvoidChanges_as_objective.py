"""Example of use of the AvoidChanges as an objective to minimize modifications
of a sequence."""

from dnachisel import (DnaOptimizationProblem, random_dna_sequence,
                       AvoidPattern, AvoidChanges, sequences_differences,
                       EnforceGCContent)

# Note: we are not providing a location for AvoidChanges: it applies globally

for boost in (0, 0.1, 1, 10.0):
    sequence = random_dna_sequence(1000, seed=123)
    problem = DnaOptimizationProblem(
        sequence=sequence,
        objectives=[EnforceGCContent(gc_min=0.45, gc_max=0.55, gc_window=80),
                    AvoidChanges(boost=boost).as_passive_objective()])

    problem.maximize_objectives(max_random_iters=1000, progress_bars=3)
    differences = sequences_differences(problem.sequence,
                                        problem.sequence_before)

    print("%d nucleotides modified for boost=%.1f" % (differences, boost))