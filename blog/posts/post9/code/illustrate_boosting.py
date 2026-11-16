"""Draw an illustrative boosting update; these numbers are not fitted stock results."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
OUT=Path(__file__).resolve().parents[1]/"results"
fig=plt.figure(figsize=(9,6.8),facecolor="#fffcf5")
ax=fig.add_axes([0,0,1,1]);ax.set_xlim(0,1);ax.set_ylim(0,1);ax.axis("off")
ink="#42392f"; green="#526f61"; brown="#936044"
def text(x,y,s,size=12,**kw):
 ax.text(x,y,s,fontsize=size,color=ink,va="center",**kw)
text(.04,.95,"One small correction, then repeat",19,weight="bold")
text(.04,.90,"Illustrative training example: the actual return is already known.",11)
for y,title,body in [(.73,"1  Find the error","Actual 3% − prediction 1% = +2 percentage points"),(.52,"2  Learn a correction","A new small tree learns patterns in the remaining errors."),(.31,"3  Take a small step","If its correction here is +2 points: 0.05 × 2 = +0.1 point")]:
 ax.add_patch(FancyBboxPatch((.04,y-.07),.92,.14,boxstyle="round,pad=0.008,rounding_size=0.02",facecolor="#eee9de",edgecolor="#d8cebe"))
 text(.065,y+.025,title,13,weight="bold");text(.065,y-.025,body,11)
for y in [.625,.415]:
 ax.annotate("",xy=(.5,y-.025),xytext=(.5,y+.025),arrowprops=dict(arrowstyle="->",color=green,lw=2))
text(.04,.17,"Updated prediction: 1% + 0.1 point = 1.1%",14,weight="bold")
text(.04,.115,"Remaining error: 3% − 1.1% = 1.9 points → the next tree learns from this.",10.5)
text(.04,.05,"The tree learns from many training observations, not just this one stock.",10)
fig.savefig(OUT/"boosting-update.png",dpi=180,bbox_inches="tight");plt.close(fig)
