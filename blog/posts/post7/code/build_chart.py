"""Build the one interactive Plotly graphic from saved aggregate estimates."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'results/majors.json').read_text())
html=(root/'code/chart_template.html').read_text().replace('__DATA__',json.dumps(rows).replace('</','<\\/'))
html=html.replace('__OCCUPATIONS__',(root/'results/occupation_shares.json').read_text().replace('</','<\\/'))
(root/'results/chart.html').write_text(html)
print('Interactive chart built:',len(rows),'majors')

# Article values are generated from the same estimates, not copied manually.
by={d['code']:d for d in rows}
j,e,m,n=by['1902'],by['2408'],by['2499'],by['6107']
money=lambda v:'$'+format(round(v/100)*100,',')
values={'n_majors':str(len(rows)),
 'j_earnings':money(j['female_earnings']), 'e_women':money(e['female_earnings']),
 'e_men':money(e['male_earnings']), 'e_difference':money(e['female_earnings']-j['female_earnings']),
 'j_share':str(round(j['female_share'])), 'e_share':str(round(e['female_share'])),
 'e_ratio':str(round(e['ratio'])), 'm_share':str(round(m['female_share'])),
 'n_share':str(round(n['female_share'])), 'n_ratio':str(round(n['ratio'])),
 'j_low':str(round(j['ratio']-j['ratio_moe90'])), 'j_high':str(round(j['ratio']+j['ratio_moe90'])),
 'm_low':str(round(m['ratio']-m['ratio_moe90'])), 'm_high':str(round(m['ratio']+m['ratio_moe90'])),
 'journalist_share':format(j['journalist_share'],'.1f'),
 'finance_ratio':str(round(by['6207']['ratio'])),
 'finance_male_hours':format(by['6207']['male_mean_hours'],'.1f'),
 'finance_female_hours':format(by['6207']['female_mean_hours'],'.1f'),
 'n_excluded':str(json.loads((root/'results/sample_flow.json').read_text())['excluded_majors'])}
(root/'results/text_values.json').write_text(json.dumps(values,indent=2))
