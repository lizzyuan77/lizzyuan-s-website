"""Run from post5 after analyze.R and mechanisms.R.
Requires matplotlib, numpy, pyshp, pyproj.
"""
import csv, os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', str(Path('results/.matplotlib').resolve()))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.colors import LinearSegmentedColormap, Normalize
import numpy as np
import shapefile
from pyproj import Transformer

rows={r['state'].zfill(2):r for r in csv.DictReader(open('results/states-expanded.csv'))}
reader=shapefile.Reader('data/boundaries/cb_2024_us_state_20m.shp')
features=[s for s in reader.iterShapeRecords() if s.record['STATEFP'] in rows]
assert len(features)==len(rows)==50
assert {s.record['STATEFP'] for s in features}==set(rows)
bg='#fbf9f3'; ink='#173f3b'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
for field,title,subtitle,legend,limits,colors,name in [
 ('ratio','How much do women earn relative to men?', '2024 | Median annual earnings of full-time, year-round workers age 16+',
  "Women’s median earnings per $100 of men’s median earnings",(70,100),['#f2d8bc','#a9c8bc','#17665d'],'map-earnings.png'),
 ('tech_share','Where are technology occupations concentrated?', '2024 | Computer & mathematical occupations as a share of employed residents age 16+',
  'Share of employed residents (%)',(0,7),['#f1eee4','#a9c8bc','#17665d'],'map-tech.png'),
 ('representation_shortfall','Women are underrepresented in tech in every state', '2024 | Women’s share of all employment minus women’s share of technology occupations',
  'Representation shortfall (percentage points)',(0,30),['#f1e9e3','#bc94a4','#653951'],'map-representation.png')]:
 fig=plt.figure(figsize=(13,8.5),facecolor=bg)
 main=fig.add_axes([.025,.28,.95,.54]); ak=fig.add_axes([.04,.13,.22,.23]); hi=fig.add_axes([.27,.16,.13,.15])
 cmap=LinearSegmentedColormap.from_list('earnings',colors); norm=Normalize(*limits)
 vals={f:float(r[field]) for f,r in rows.items()}
 assert min(vals.values())>=limits[0] and max(vals.values())<=limits[1]
 for region,ax,epsg in [('main',main,5070),('02',ak,3338),('15',hi,26904)]:
  transform=Transformer.from_crs(4269,epsg,always_xy=True)
  selected=[s for s in features if (s.record['STATEFP']==region if region!='main' else s.record['STATEFP'] not in ['02','15'])]
  patches=[]; values=[]; centres=[]
  for sr in selected:
   f=sr.record['STATEFP']; rings=[]; ends=list(sr.shape.parts)+[len(sr.shape.points)]
   for k in range(len(ends)-1):
    xy=[transform.transform(*p) for p in sr.shape.points[ends[k]:ends[k+1]]]
    patches.append(Polygon(xy,closed=True));values.append(vals[f])
    pairs=list(zip(xy,xy[1:]+xy[:1]));cross=[u[0]*v[1]-v[0]*u[1] for u,v in pairs]; area=sum(cross)
    if abs(area)>1:
     cx=sum((u[0]+v[0])*c for (u,v),c in zip(pairs,cross))/(3*area)
     cy=sum((u[1]+v[1])*c for (u,v),c in zip(pairs,cross))/(3*area)
     rings.append((abs(area),cx,cy))
   _,x,y=max(rings);centres.append((sr.record['STUSPS'],x,y,f))
  coll=PatchCollection(patches,cmap=cmap,norm=norm,edgecolor='white',linewidth=.75)
  coll.set_array(np.array(values));ax.add_collection(coll);ax.autoscale_view();ax.set_aspect('equal');ax.axis('off')
  for abbr,x,y,f in centres:
   if region=='main':
    if abbr in ['MA','RI','CT','NJ','DE','MD']:
     yy={'MA':2420000,'RI':2260000,'CT':2100000,'NJ':1940000,'DE':1780000,'MD':1620000}[abbr]
     ax.annotate(abbr,(x,y),xytext=(2600000,yy),ha='left',va='center',fontsize=8,arrowprops={'arrowstyle':'-','color':'#687a73','lw':.6})
    elif abbr in ['VT','NH']:
     ax.annotate(abbr,(x,y),xytext=(x+(-190000 if abbr=='VT' else 170000),y+170000),fontsize=8,ha='center',color=ink,arrowprops={'arrowstyle':'-','color':'#687a73','lw':.6})
    else: ax.text(x,y,abbr,ha='center',va='center',fontsize=8,weight='bold',color='white' if norm(vals[f])>.62 else ink)
   else: ax.set_title(abbr+': '+(f'${vals[f]:.1f}' if field=='ratio' else f'{vals[f]:.1f} pp' if field=='representation_shortfall' else f'{vals[f]:.1f}%'),color=ink,fontsize=11)
  if region=='main':ax.set_xlim(-2600000,2950000)
 fig.text(.035,.945,title,color=ink,fontsize=23,weight='bold')
 fig.text(.035,.900,subtitle,color='#52665f',fontsize=12)
 cax=fig.add_axes([.48,.175,.44,.023]); cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cax,orientation='horizontal')
 cb.set_label(legend,fontsize=10,labelpad=7)
 fig.text(.48,.24,'Darker green = closer to earnings parity' if field=='ratio' else 'Darker plum = greater underrepresentation' if field=='representation_shortfall' else 'Darker green = greater occupational concentration',color=ink,fontsize=11)
 fig.text(.035,.066,'Sources: Census ACS 2024 1-year, B20017, B24010 and S2401; 2024 Census cartographic boundaries.',fontsize=10,color='#52665f')
 fig.text(.035,.040,'50 states; DC excluded. Alaska and Hawaii are relocated and resized. Point estimates; no significance claims.',fontsize=10,color='#52665f')
 fig.savefig('results/'+name,dpi=180,facecolor=bg);plt.close(fig)
print('Three maps saved; all 50 state FIPS codes matched exactly.')
