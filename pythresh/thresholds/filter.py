import numpy as np
import scipy.stats as stats
from scipy import signal
from scipy.ndimage import gaussian_filter
from sklearn.utils import check_array
from .base import BaseThresholder
from .thresh_utility import normalize, cut, gen_kde

def GAU_fltr(decision, sig):
    """Gaussian filter scores"""

    return gaussian_filter(decision, sigma=sig)

def SAV_fltr(decision, sig):
    """Savgol filter scores"""

    return signal.savgol_filter(decision, window_length=round(0.5*sig),
                                polyorder=1)

def HIL_fltr(decision, sig):
    """Hilbert filter scores"""

    return signal.hilbert(decision, N=round(sig))

def WIE_fltr(decision, sig):
    """Wiener filter scores"""

    return signal.wiener(decision, mysize=len(decision))

def MED_fltr(decision, sig):
    """Medfilt filter scores"""
    
    sig = round(sig)

    if sig%2==0:
        sig+=1

    return signal.medfilt(decision, kernel_size=[sig])


def DEC_fltr(decision, sig):
    """Decimate filter scores"""

    return signal.decimate(decision, q=round(sig), ftype='fir')

def DET_fltr(decision, sig):
    """Detrend filter scores"""

    return signal.detrend(decision, bp=np.linspace(0,len(decision)-1,round(sig)).astype(int))

def RES_fltr(decision, sig):
    """Resampling filter scores"""

    return signal.resample(decision, num=round(np.sqrt(len(decision))),
                           window=round(np.sqrt(sig)))


class FILTER(BaseThresholder):
    """FILTER class for Filtering based thresholders.

       Use the filtering based methods to evaluate a non-parametric means
       to threshold scores generated by the decision_scores where outliers
       are set to any value beyond the maximum filter value
       
       Paramaters
       ----------

       method : str, optional (default='wiener')
        {'gaussian', 'savgol', 'hilbert', 'wiener', 'medfilt', 'decimate',
        'detrend', 'resample'}

       sigma : int, optional (default='native') 

       Attributes
       ----------

       eval_: numpy array of binary labels of the training data. 0 stands
           for inliers and 1 for outliers/anomalies.

    """

    def __init__(self, method='wiener', sigma='native'):

        super(FILTER, self).__init__()
        self.method = method
        self.method_funcs = {'gaussian': GAU_fltr, 'savgol': SAV_fltr,
                             'hilbert': HIL_fltr, 'wiener': WIE_fltr,
                             'medfilt': MED_fltr, 'decimate': DEC_fltr,
                             'detrend':DET_fltr, 'resample':RES_fltr}
        
        self.sigma = sigma

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

        # Get sigma variables for various applications for each filter
        if self.sigma=='native':
            sig = len(decision)*np.std(decision)

        # Filter scores
        fltr = self.method_funcs[str(self.method)](decision, sig)
        limit = np.max(fltr)

        self.thresh_ = limit

        return cut(decision, limit)