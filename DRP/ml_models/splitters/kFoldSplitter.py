"""Contains a class for performing k-fold validation splits."""
import random
from .abstractSplitter import AbstractSplitter
import logging
logger = logging.getLogger(__name__)


class Splitter(AbstractSplitter):
    """The splitter class for K-fold validation."""

    def __init__(self, namingStub, num_folds=4):
        """Standard splitter initialisation."""
        super(Splitter, self).__init__(namingStub)
        self.k = num_folds

    def split(self, reactions, verbose=False):
        """Perform the split."""
        super(Splitter, self).split(reactions, verbose=verbose)
        # Split the reactions' IDs into K randomly-organized buckets.
        rxn_ids = [reaction.id for reaction in reactions]
        random.shuffle(rxn_ids)
        buckets = [rxn_ids[i::self.k] for i in range(self.k)]

        if verbose:
            logger.info("Split into {} buckets with sizes: {}".format(len(buckets), map(len, buckets)))

        splits = []
        for i in range(self.k):
            train = reactions.filter(id__in=[item for b in buckets[:i] + buckets[i + 1:]
                                             for item in b])
            test = reactions.filter(id__in=buckets[i])
            splits.append((self.package(train), self.package(test)))

        return splits
