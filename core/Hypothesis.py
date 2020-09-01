from scipy.stats import shapiro


# uniform distribution hypothesis test
def uniform_test(data, p_thresh=0.05):
  # TODO: scipy uniform test is for 1D array
  pass


# Shapiro-Wilk normal distribution hypothesis test
def normal_test(data, p_thresh=0.05):
  stat, p = shapiro(data)
  return stat, p > p_thresh
