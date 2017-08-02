"""Implement EnforceSequence (DO NOT USE YET: Work in progress, stabilizing)"""

# TODO: factorize with self.sequence ?

from dnachisel.biotools import complement, IUPAC_NOTATION

from ..Specification import Specification
from ..SpecEvaluation import SpecEvaluation
from dnachisel.Location import Location



class EnforceSequence(Specification):
    """WORK IN PROGRESS. Enforces a degenerate sequence."""
    localization_interval_length = 6 # used when optimizing the minimize_diffs
    best_possible_score = 0
    enforced_by_mutations_restrictions = True


    def __init__(self, sequence, location=None, boost=1.0):
        self.sequence = sequence
        self.location = location
        self.boost = boost

            return self.location.extract_sequence(sequence)

    def initialize_on_problem(self, problem, role):
        """Find out what sequence it is that we are supposed to conserve."""
        if self.location is None:
            result = self.copy_with_changes()
            result.location = Location(0, len(problem.sequence), 1)
            return result
        else:
            return self

    def evaluate(self, problem):
        """Return a score equal to -number_of modifications.

        Locations are "binned" modifications regions. Each bin has a length
        in nucleotides equal to ``localization_interval_length`.`
        """
        sequence = self.location.extract_sequence(problem.sequence)
        discrepancies = np.array([
            i
            for i, nuc in enumerate(sequence)
            if nuc not in IUPAC_NOTATION[self.sequence[i]]
        ])

        if self.location.strand == -1:
            discrepancies = self.location.end - discrepancies
        else:
            discrepancies = discrepancies + self.location.start
        intervals = [
            (r[0], r[-1])
            for r in group_nearby_indices(
                discrepancies,
                max_group_spread=self.localization_interval_length)
        ]
        locations = [Location(start, end, 1) for start, end in intervals]

        return SpecEvaluation(self, problem, score=-len(discrepancies),
                              locations=locations)

    def localized(self, location):
        """Localize the spec to the overlap of its location and the new.
        """
        start, end = location.start, location.end
        new_location = self.location.overlap_region(location)
        if new_location is None:
            return VoidSpecification(parent_specification=self)
        else:
            if self.location.strand == -1:
                start = self.location.end - new_location.end
                end = self.location.end - new_location.start
            else:
                start = new_location.start - self.location.start
                end = new_location.end - self.location.start
            new_sequence = self.sequence[start:end]

            return self.copy_with_changes(location=new_location,
                                          sequence=new_location)

    def restrict_nucleotides(self, sequence, location=None):
        """When localizing, forbid any nucleotide but the one already there."""
        new_location = self.location.overlap_region(location)
        if new_location is None:
            return []
        else:
            start, end = new_location.start, new_location.end
            if self.location.strand == -1:
                lend = self.location.end
                return [(i, set(reverse_complement(n) for n in
                                IUPAC_NOTATION[self.sequence[lend - i]]))
                        for i in range(start, end)]
            else:
                lstart = self.location.start
                return [(i, IUPAC_NOTATION[self.sequence[i - lstart]]))
                        for i in range(start, end)]

    def __repr__(self):
        """Represent."""
        return "AvoidChanges(%s)" % str(self.location)

    def __str__(self):
        """Represent."""
        return "AvoidChanges(%s)" % str(self.location)