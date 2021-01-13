import matplotlib.pyplot as plt
import pickle as pkl
import sys

method = sys.argv[2]
cat = sys.argv[1]
with open(method+'_'+cat+'_opts.pkl', 'rb') as f:
    xydict = pkl.load(f)

x = xydict['x']
effns = [val/max(xydict['effns']) for val in xydict['effns']]
statsigs = [val/max(xydict['statsigs']) for val in xydict['statsigs']]

plt.plot(x, statsigs, 'g^')
plt.plot(x, effns, 'r^')
plt.legend(['$S/\sqrt{S+B}$','$(N_{sig}/\sigma_{Nsig})^2$'])
plt.xlabel(method+' Cut Value')
plt.ylabel('Normaliased values')

plt.show()

