import sys
import unittest
from itertools import product
from os.path import dirname as up

# noinspection PyProtectedMember
import numpy as np
from numpy.testing import assert_equal
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.pca import PCA
from pyod.utils.data import generate_data

from pythresh.thresholds.dsn import DSN

# temporary solution for relative imports in case pythresh is not installed
# if pythresh is installed, no need to use the following line

path = up(up(up(__file__)))
sys.path.append(path)


class TestDSN(unittest.TestCase):
    def setUp(self):
        self.n_train = 200
        self.n_test = 100
        self.contamination = 0.1
        self.X_train, self.X_test, self.y_train, self.y_test = generate_data(
            n_train=self.n_train, n_test=self.n_test,
            contamination=self.contamination, random_state=42)

        clf = KNN()
        clf.fit(self.X_train)

        scores = clf.decision_scores_

        clfs = [KNN(), PCA(), IForest()]

        multiple_scores = [
            clf.fit(self.X_train).decision_scores_ for clf in clfs]
        multiple_scores = np.vstack(multiple_scores).T

        self.all_scores = [scores, multiple_scores]

        self.metrics = ['JS', 'WS', 'ENG', 'BHT', 'HLL', 'HI', 'LK',
                        'LP', 'MAH', 'TMT', 'RES', 'KS', 'INT', 'MMD']

    def test_prediction_labels(self):

        params = product(self.all_scores, self.metrics)

        for scores, metric in params:

            self.thres = DSN(metric=metric)
            pred_labels = self.thres.eval(scores)
            assert (self.thres.thresh_ is not None)

            assert_equal(pred_labels.shape, self.y_train.shape)

            if (not np.all(pred_labels == 0)) & (not np.all(pred_labels == 1)):

                assert (pred_labels.min() == 0)
                assert (pred_labels.max() == 1)
