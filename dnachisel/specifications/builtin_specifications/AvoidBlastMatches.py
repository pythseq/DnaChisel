"""Implementation of AvoidBlastMatches."""

from ..Specification import Specification, VoidSpecification
from ..SpecEvaluation import SpecEvaluation
from dnachisel.biotools import blast_sequence
from dnachisel.Location import Location

class AvoidBlastMatches(Specification):
    """Enforce that the given pattern is absent in the sequence.

    Uses NCBI Blast+. Only local BLAST is supported/tested as for now

    Parameters
    ----------

    blast_db
      Path to a local BLAST database. These databases can be obtained with
      NCBI's `makeblastdb`. Omit the extension, e.g. `ecoli_db/ecoli_db`.

    word_size
      Word size used by the BLAST algorithm

    perc_identity
      Minimal percentage of identity for BLAST matches. 100 means that only
      perfect matches are considered.

    num_alignments
      Number alignments

    num_threads
      Number of threads/CPU cores to use for the BLAST algorithm.

    min_align_length
      Minimal length that an alignment should have to be considered.
    """

    def __init__(self, blast_db, word_size=4, perc_identity=100,
                 num_alignments=1000, num_threads=3, min_align_length=20,
                 location=None):
        """Initialize."""
        self.blast_db = blast_db
        self.word_size = word_size
        self.perc_identity = perc_identity
        self.num_alignments = num_alignments
        self.num_threads = num_threads
        self.min_align_length = min_align_length
        self.location = location

    def evaluate(self, problem):
        """Return (-M) as a score, where M is the number of BLAST matches found
        in the BLAST database."""
        location = self.location
        if location is None:
            location = Location(0, len(problem.sequence))
        sequence = location.extract_sequence(problem.sequence)
        blast_record = blast_sequence(
            sequence, blast_db=self.blast_db,
            word_size=self.word_size,
            perc_identity=self.perc_identity,
            num_alignments=self.num_alignments,
            num_threads=self.num_threads
        )
        query_locations = [
            Location(min(hit.query_start, hit.query_end),
                     max(hit.query_start, hit.query_end),
                     1 - 2 * (hit.query_start > hit.query_end))
            for alignment in blast_record.alignments
            for hit in alignment.hsps
        ]
        locations = sorted([
            loc for loc in query_locations
            if len(location) >= self.min_align_length
        ])
        if locations == []:
            return SpecEvaluation(self, problem, score=1,
                                       message="Passed: no BLAST match found")

        return SpecEvaluation(
            self, problem, score=-len(locations), locations=locations,
            message="Failed - matches at %s" % locations)

    def localized(self, location):
        """Localize the evaluation."""
        if self.location is not None:
            new_location = self.location.overlap_region(location)
            if new_location is None:
                return VoidSpecification(parent_specification=self)
        else:
            new_location = location.extended(self.min_align_length)

        return self.copy_with_changes(location=new_location)

    def __repr__(self):
        return "NoBlastMatchesSpecification%s(%s, %d+ bp, perc %d+)" % (
            self.location, self.blast_db, self.min_align_length,
            self.perc_identity
        )
