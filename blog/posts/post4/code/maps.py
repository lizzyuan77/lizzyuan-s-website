"""Two reproducible maps. Run from the post directory: python code/maps.py.
Dependencies: matplotlib, pyshp, pyproj. Official Census boundaries are cached.
"""
from pathlib import Path
import csv, zipfile, urllib.request
import shapefile
import os
os.environ.setdefault('MPLCONFIGDIR',str(Path('results/.matplotlib').resolve()))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from pyproj import Transformer

root=Path('data/boundaries');root.mkdir(parents=True,exist_ok=True)
archive=root/'cb_2024_us_state_20m.zip'
url='https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip'
if not archive.exists(): urllib.request.urlretrieve(url,archive)
with zipfile.ZipFile(archive) as f: f.extractall(root)
reader=shapefile.Reader(str(root/'cb_2024_us_state_20m.shp'))
rows={str(int(r['state'])).zfill(2):r for r in csv.DictReader(open('results/state-changes.csv',encoding='utf-8-sig'))}
features=[r for r in reader.iterShapeRecords() if r.record['STATEFP'] in rows]
assert len(rows)==len(features)==50
cmap=LinearSegmentedColormap.from_list('change',['#b96130','#fbf9f3','#17665d'])
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12})

for key,title,subtitle,legend,limit,filename in [
 ('tech_change','5. Where did tech employment gain ground?','2018 to 2024 | Change in computer & mathematical occupation share','Tech-share change (percentage points) | green = increase',1.5,'map-tech.png'),
 ('unemployment_change','6. Where did unemployment improve?','2018 to 2024 | A decline in unemployment is shown as a positive improvement','Unemployment improvement (percentage points) | green = lower unemployment',2.5,'map-unemployment.png')]:
 fig=plt.figure(figsize=(13,8.8),facecolor='#fbf9f3')
 ax=fig.add_axes([.02,.22,.96,.65]);ak=fig.add_axes([.06,.11,.19,.20]);hi=fig.add_axes([.27,.12,.14,.15])
 axes={'main':(ax,5070),'02':(ak,3338),'15':(hi,26904)}
 norm=TwoSlopeNorm(vmin=-limit,vcenter=0,vmax=limit)
 vals={f:(-float(r[key]) if key=='unemployment_change' else float(r[key])) for f,r in rows.items()}
 assert max(abs(v) for v in vals.values())<=limit
 for region,(a,epsg) in axes.items():
  transform=Transformer.from_crs(4326,epsg,always_xy=True)
  selected=[s for s in features if (s.record['STATEFP']==region if region!='main' else s.record['STATEFP'] not in ['02','15'])]
  patches=[];values=[]
  for sr in selected:
   fips=sr.record['STATEFP'];shape=sr.shape
   parts=list(shape.parts)+[len(shape.points)]
   for i in range(len(parts)-1):
    pts=shape.points[parts[i]:parts[i+1]]
    xy=[transform.transform(x,y) for x,y in pts]
    patches.append(Polygon(xy,closed=True));values.append(vals[fips])
  coll=PatchCollection(patches,cmap=cmap,norm=norm,edgecolor='white',linewidth=.8)
  coll.set_array(__import__('numpy').array(values));a.add_collection(coll);a.autoscale_view();a.set_aspect('equal');a.axis('off')
  for sr in selected:
   rec=sr.record;f=rec['STATEFP'];abbr=rec['STUSPS']
   # Label at the area centroid of the largest projected polygon ring.
   rings=[];ends=list(sr.shape.parts)+[len(sr.shape.points)]
   for j in range(len(ends)-1):
    pts=[transform.transform(*p) for p in sr.shape.points[ends[j]:ends[j+1]]]
    pairs=list(zip(pts,pts[1:]+pts[:1]));cross=[u[0]*v[1]-v[0]*u[1] for u,v in pairs];area=sum(cross)
    if abs(area)>1:
     cx=sum((u[0]+v[0])*c for (u,v),c in zip(pairs,cross))/(3*area)
     cy=sum((u[1]+v[1])*c for (u,v),c in zip(pairs,cross))/(3*area)
     rings.append((abs(area),cx,cy))
   _,x,y=max(rings)
   if region=='main':
    if abbr in ['MA','RI','CT','NJ','DE','MD']:
     positions={'MA':2420000,'RI':2260000,'CT':2100000,'NJ':1940000,'DE':1780000,'MD':1620000}
     a.annotate(abbr,(x,y),xytext=(2600000,positions[abbr]),fontsize=8,ha='left',va='center',arrowprops={'arrowstyle':'-','color':'#63736d','lw':.6})
    else:
     a.text(x,y,abbr,fontsize=8,ha='center',va='center',color='white' if abs(vals[f])/limit>.58 else '#203d36',weight='bold')
   else:
    a.set_title(f"{abbr}: {vals[f]:+.2f} pp",fontsize=11,color='#173f3b',pad=2)
  if region=='main':a.set_xlim(-2600000,2950000)
 fig.text(.035,.95,title,fontsize=23,fontweight='bold',color='#173f3b')
 fig.text(.035,.91,subtitle,fontsize=13,color='#52665f')
 cax=fig.add_axes([.46,.15,.47,.025]);cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal')
 cb.set_label(legend,fontsize=10,labelpad=7);cb.ax.tick_params(labelsize=10)
 fig.text(.46,.23,'Orange = decrease' if key=='tech_change' else 'Orange = unemployment worsened',fontsize=11,color='#a65a32')
 fig.text(.035,.044,'Sources: Census ACS 1-year (S2401, S2301); Census 2024 state boundaries. All 50 states; DC excluded.',fontsize=10,color='#52665f')
 fig.text(.035,.022,'Alaska and Hawaii are relocated and resized insets. Point estimates; colors do not indicate statistical significance.',fontsize=10,color='#52665f')
 fig.savefig('results/'+filename,dpi=180,facecolor=fig.get_facecolor());plt.close(fig)
print('Created two maps; all 50 states matched by FIPS.')
