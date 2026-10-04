# Public Census ACS 1-year subject tables. No API key is stored.
# Run from output/blog4. 2020 standard ACS 1-year estimates do not exist.
$ErrorActionPreference='Stop'
$years=@(2018,2019,2021,2022,2023,2024)
$vars=@('S2401_C01_001E','S2401_C01_001M','S2401_C01_007E','S2401_C01_007M','S2301_C03_001E','S2301_C03_001M','S2301_C04_001E','S2301_C04_001M')
$rows=@()
if(-not $env:CENSUS_API_KEY){throw 'Set CENSUS_API_KEY in the process environment before refreshing data.'}
Set-Content data/source-urls.txt -Value 'Census ACS public data queries (authentication omitted)'
foreach($year in $years){
 $base="https://api.census.gov/data/$year/acs/acs1/subject"
 $meta=Invoke-RestMethod "$base/groups/S2401.json"
 if($meta.variables.S2401_C01_007E.label -notmatch 'Computer and mathematical occupations'){throw "Occupation label changed: $year"}
 $url=$base+'?get=NAME,'+($vars -join ',')+'&for=state:*'
 try { $response=Invoke-RestMethod ($url+'&key='+$env:CENSUS_API_KEY) } catch { throw 'Census request failed; check connectivity or API key activation.' }
 if($response -is [string] -or $response.Count -lt 51){throw "Census did not return a valid state table. API access may require a key; do not interpret the response as observations."}
 $response | ConvertTo-Json -Depth 8 | Set-Content "data/acs-state-$year.json" -Encoding utf8
 $url | Add-Content data/source-urls.txt
 foreach($row in $response[1..($response.Count-1)]){
  $obj=[ordered]@{year=$year}
  for($j=0;$j -lt $response[0].Count;$j++){$obj[$response[0][$j]]=$row[$j]}
  if($obj.state -eq '72'){continue}
  $obj.tech_share=100*[double]$obj.S2401_C01_007E/[double]$obj.S2401_C01_001E
  $rows += [pscustomobject]$obj
 }
}
$rows | Export-Csv data/state-panel.csv -NoTypeInformation -Encoding utf8
Write-Output "Downloaded $($rows.Count) state-year observations, including DC."



