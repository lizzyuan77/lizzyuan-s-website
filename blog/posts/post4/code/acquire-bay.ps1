# Run from the blog4 directory after setting CENSUS_API_KEY in the process environment.
$ErrorActionPreference='Stop'
$years=@(2018,2019,2021,2022,2023,2024)
$vars=@('S2401_C01_001E','S2401_C01_001M','S2401_C01_007E','S2401_C01_007M','S2301_C03_001E','S2301_C03_001M','S2301_C04_001E','S2301_C04_001M')
$rows=@()
foreach($year in $years){
 $url="https://api.census.gov/data/$year/acs/acs1/subject?get=NAME,"+($vars -join ',')+'&for=county:075,085&in=state:06'
 try{$response=Invoke-RestMethod ($url+'&key='+$env:CENSUS_API_KEY)}catch{throw 'Census request failed.'}
 if($response -is [string] -or $response.Count -ne 3){throw 'Expected two counties.'}
 $response | ConvertTo-Json -Depth 8 | Set-Content "data/acs-bay-$year.json" -Encoding utf8
 foreach($row in $response[1..2]){
  $obj=[ordered]@{year=$year}
  for($j=0;$j -lt $response[0].Count;$j++){$obj[$response[0][$j]]=$row[$j]}
  $obj.tech_share=100*[double]$obj.S2401_C01_007E/[double]$obj.S2401_C01_001E
  $rows += [pscustomobject]$obj
 }
}
$rows | Export-Csv data/bay-panel.csv -NoTypeInformation -Encoding utf8
Write-Output "Downloaded $($rows.Count) county-year observations."
