<#
.SYNOPSIS
  Run verify_case.ps1 for every case in ..\verification_plan\human_sample.csv (or a given list),
  saving each console summary to .\summaries\case<N>.txt. Cases that already have a summary are skipped,
  so the script can be stopped and restarted.

.EXAMPLE
  .\run_sample.ps1                       # all 47 sample cases
  .\run_sample.ps1 -Cases 49,67,69,109   # only these cases
#>
param([int[]]$Cases)
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$SumDir = Join-Path $Here 'summaries'
New-Item -ItemType Directory -Force $SumDir | Out-Null
if (-not $Cases) {
  $Cases = Import-Csv (Join-Path $Here '..\verification_plan\human_sample.csv') | ForEach-Object { [int]$_.case_number }
}
$i = 0
foreach ($c in $Cases) {
  $i++
  $out = Join-Path $SumDir "case$c.txt"
  if (Test-Path $out) { Write-Host "[$i/$($Cases.Count)] case $c already done, skipping"; continue }
  Write-Host "[$i/$($Cases.Count)] case $c ..." -ForegroundColor Cyan
  & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Here 'verify_case.ps1') -Case $c *>&1 |
    ForEach-Object { "$_" } | Out-File -FilePath $out -Encoding utf8
  Write-Host ("  -> " + ((Get-Content $out | Select-String 'MAVEN_EXIT=\d+' | Select-Object -Last 1).Line))
}
Write-Host "Done. Summaries in $SumDir"
