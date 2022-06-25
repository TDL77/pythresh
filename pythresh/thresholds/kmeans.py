import numpy as np
from scipy.cluster.vq import kmeans
from sklearn.utils import check_array
from .base import BaseThresholder
from .thresh_utility import normalize, cut, gen_kde


class KMEANS(BaseThresholder):
    """KMEANS class for KMEANS clustering thresholder.

       Use the kmeans clustering to evaluate a non-parametric means to
       threshold scores generated by the decision_scores where outliers
       are set to any value beyond the radius distance of the single
       cluster centroid

       Paramaters
       ----------
       

       Attributes
       ----------

       eval_: numpy array of binary labels of the training data. 0 stands
           for inliers and 1 for outliers/anomalies.

    """

    def __init__(self):

        super(KMEANS, self).__init__()

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

        # Find the most prominent kmeans center and radius
        codebook, distortion = kmeans(decision, 1)

        # Set limit to the radius distance from the center
        limit = codebook + distortion

        self.thresh_ = limit

        return cut(decision, limit)

