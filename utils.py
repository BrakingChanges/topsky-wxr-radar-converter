
import numpy as np

def rain_rate_to_dbz(rain_rate):
	if rain_rate <= 0:
		return -32
	z = 200 * (rain_rate ** 1.6)
	dbz = 10 * np.log10(z)
	return int(round(dbz))
