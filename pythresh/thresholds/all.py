import numpy as np
import scipy.stats as stats
from sklearn.metrics import auc
from sklearn.utils import check_array
from .base import BaseThresholder
from .thresh_utility import normalize, cut, gen_kde

from .iqr import IQR
from .mad import MAD
from .fwfm import FWFM
from .yj import YJ
from .kmeans import KMEANS
from .zscore import ZSCORE
from .aucp import AUCP
from .qmcd import QMCD
from .fgd import FGD
from .dsn import DSN
from .clf import CLF
from .gf import GF
from .wind import WIND
from .eb import EB
from .regr import REGR
from .boot import BOOT
from .mcst import MCST
from .hist import HIST
from .moll import MOLL
from .chau import CHAU
from .gesd import GESD
from .mtt import MTT
from .shift import SHIFT


class ALL(BaseThresholder):
    """ALL class for Combined thresholder.

       Use the multiple thresholders as a non-parametric means
       to threshold scores generated by the decision_scores where outliers
       are set to any value beyond the (mean, median, or gmean) of the
       contamination from all the combined thresholders.
       
       Paramaters
       ----------

       thresholders : list, optional (default='all')
            list of instantiated thresholders, e.g. [DSN()]
       
       max_contam : float, optional (default=0.5)

       method : str, optional (default='mean')
           statistic to apply to contamination levels
           {'mean', 'median', 'gmean'}

       Attributes
       ----------

       eval_: numpy array of binary labels of the training data. 0 stands
           for inliers and 1 for outliers/anomalies.

    """

    def __init__(self, thresholders='all', max_contam=0.5, method='mean'):

        self.thresholders = thresholders
        self.max_contam = max_contam
        stat = {'mean':np.mean, 'median':np.median, 'gmean':stats.gmean}
        self.method = stat[method]

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

        decision = np.sort(normalize(decision))

        # Initialize thresholders
        if self.thresholders=='all':
            self.thresholders = [IQR(), MAD(), FWFM(), YJ(), KMEANS(),
                                 ZSCORE(), AUCP(), QMCD(), FGD(), DSN(),
                                 CLF(), GF(), WIND(), EB(), REGR(), BOOT(),
                                 MCST(), HIST(), MOLL(), CHAU(), GESD(),
                                 MTT(), SHIFT()]

        # Apply each thresholder
        contam = []
        
        for thresholder in self.thresholders:
            
            labels = thresholder.eval(decision)
            outlier_ratio = np.sum(labels)/len(labels)
            
            if outlier_ratio<self.max_contam:
            
                contam.append(outlier_ratio)

        # Get [mean, median, or gmean] of inliers
        inlier_ratio = 1-self.method(np.array(decision))
        limit = decision[int(len(decision)*inlier_ratio)]
        
        self.thresh_ = limit
        
        return cut(decision, limit)