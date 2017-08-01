"""Implementation of AvoidBlastMatches."""

import numpy as np

from ..Specification import Specification, VoidSpecification
from ..SpecEvaluation import SpecEvaluation
from dnachisel.biotools import sequences_differences_array
from dnachisel.Location import Location



class AvoidChanges(Specification):
    """Specify that some locations of the sequence should not be changed.

    ``AvoidChanges`` Specifications are used to constrain the mutations space
    of DNA OptimizationProblem.

    Parameters
    ----------
    location
      Location object indicating the position of the segment that must be
      left unchanged. Alternatively,
      indices can be provided. If neither is provided, the assumed location
      is the whole sequence.

    indices
      List of indices that must be left unchanged.

    target_sequence
      At the moment, this is rather an internal variable. Do not use unless
      you're not afraid of side effects.

    """
    localization_interval_length = 8 # used when optimizing the minimize_diffs
    best_possible_score = 0

    def __init__(self, location=None, indices=None, target_sequence=None,
                 boost=1.0):
        """Initialize."""
        self.location = location
        self.indices = np.array(indices) if (indices is not None) else None
        self.target_sequence = target_sequence
        self.boost = boost

    def extract_subsequence(self, sequence):
        """Extract a subsequence from the location or indices.

        Used to initialize the function when the sequence is provided.

        """
        if (self.location is None) and (self.indices is None):
            return sequence
        elif self.indices is not None:
            return "".join(np.array(sequence)[self.indices])
        else: #self.location is not None:
            return self.location.extract_sequence(sequence)


    def initialize_on_problem(self, problem, role):
        """Find out what sequence it is that we are supposed to conserve."""

        if self.target_sequence is None:
            result = self.copy_with_changes()
            result.target_sequence = self.extract_subsequence(problem.sequence)
        else:
            result = self
        return result

    def evaluate(self, problem):
        """Return a score equal to -number_of modifications.

        Locations are "binned" modifications regions. Each bin has a length
        in nucleotides equal to ``localization_interval_length`.`
        """
        target = self.target_sequence
        sequence = self.extract_subsequence(problem.sequence)
        discrepancies = np.nonzero(
            sequences_differences_array(sequence, target))[0]

        if self.indices is not None:
            discrepancies = self.indices[discrepancies]
        elif self.location is not None:
            if self.location.strand == -1:
                discrepancies = self.location.end - discrepancies
            else:
                discrepancies = discrepancies + self.location.start

        l = self.localization_interval_length
        intervals = [
            (l * start, l * (start + 1))
            for start in sorted(set([int(d / l) for d in discrepancies]))
        ]
        locations = [Location(start, end, 1) for start, end in intervals]

        return SpecEvaluation(self, problem, score=-len(discrepancies),
                              locations=locations)

    def localized(self, location):
        """Localize the spec to the overlap of its location and the new.
        """
        start, end = location.start, location.end
        if self.location is not None:
            new_location = self.location.overlap_region(location)
            if new_location is None:
                return VoidSpecification(parent_specification=self)
            else:
                return self
        elif self.indices is not None:
            inds = self.indices
            new_indices = inds[(start <= inds) & (inds <= end)]
            return self.copy_with_changes(indices=new_indices)
        else:
            return self

    def restrict_nucleotides(self, sequence, location=None):
        """When localizing, forbid any nucleotide but the one already there."""
        if location is not None:
            start = max(location.start, self.location.start)
            end = min(location.end, self.location.end)
        else:
            start, end = self.location.start, self.location.end

        return [(i, set(sequence[i])) for i in range(start, end)]

    def __repr__(self):
        """Represent."""
        return "AvoidChanges(%s)" % str(self.location)
