import numpy as np
import scipy.stats as stats
from sklearn.utils import check_array

from .base import BaseThresholder
from .thresh_utility import cut, normalize


class REGR(BaseThresholder):
    """REGR class for Regression based thresholder.

       Use the regression to evaluate a non-parametric means
       to threshold scores generated by the decision_scores where outliers
       are set to any value beyond the y-intercept value of the linear fit.
       See :cite:`aggarwal2017clf` for details.

       Parameters
       ----------

       method : {'siegel', 'theil'}, optional (default='siegel')
            Regression based method to calculate the y-intercept

            - 'siegel': implements a method for robust linear regression using repeated medians
            - 'theil':  implements a method for robust linear regression using paired values

       random_state : int, optional (default=1234)
            random seed for the normal distribution. Can also be set to None

       Attributes
       ----------

       thresh_ : threshold value that separates inliers from outliers

    """

    def __init__(self, method='siegel', random_state=1234):

        super(REGR, self).__init__()
        self.method = method
        self.random_state = random_state

    def eval(self, decision):
        """Outlier/inlier evaluation process for decision scores.

        Parameters
        ----------
        decision : np.array or list of shape (n_samples)
                   which are the decision scores from a
                   outlier detection.

        Returns
        -------
        outlier_labels : numpy array of shape (n_samples,)
            For each observation, tells whether or not
            it should be considered as an outlier according to the
            fitted model. 0 stands for inliers and 1 for outliers.
        """

        decision = check_array(decision, ensure_2d=False)

        decision = normalize(decision)

        # Create a normal distribution and normalize
        norm = np.random.default_rng(self.random_state).normal(
            loc=0.0, scale=1.0, size=decision.shape)
        norm = normalize(norm)

        # Set limit to the y-intercept
        try:
            if self.method == 'siegel':
                res = stats.siegelslopes(norm, decision)
            elif self.method == 'theil':
                res = stats.theilslopes(norm, decision)
        except MemoryError:
            res = [0.0, 1.0]

        limit = res[1]

        self.thresh_ = limit

        return cut(decision, limit)
