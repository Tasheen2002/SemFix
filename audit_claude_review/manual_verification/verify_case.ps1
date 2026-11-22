<#
.SYNOPSIS
  Manually re-run one BUMP case and compare the result with its proposed classification.

.EXAMPLE
  .\verify_case.ps1 -Case 104              # run BREAKING, summarise, show the proposed label
  .\verify_case.ps1 -Case 104 -Pre         # also run PRE
  .\verify_case.ps1 -Case 104 -Tree        # also print the dependency tree for the updated dependency's group
  .\verify_case.ps1 -Case 104 -SummaryOnly # re-summarise saved logs without running Docker

.NOTES
  Run from this folder. Logs go to .\logs\case<N>_<phase>.log (UTF-8). Maven's own exit code is
  recorded as MAVEN_EXIT=<n>; no tee, so it is never masked. Each run uses a fresh --rm container
  named manual-case<N>-<phase>. The workspace is never mounted or modified.
  Some builds take a long time (e.g. Case 163's scheduler-choco module ran for over 2 hours).
#>
param(
  [Parameter(Mandatory = $true)][ValidateRange(1, 188)][int]$Case,
  [switch]$Pre,
  [switch]$Tree,
  [switch]$SummaryOnly
)
$ErrorActionPreference = 'Stop'
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $Here '..\..')).Path
$LogDir = Join-Path $Here 'logs'
New-Item -ItemType Directory -Force $LogDir | Out-Null

$cand = (Import-Csv (Join-Path $Root 'results\test_failure_candidates.csv'))[$Case - 1]
$final = Import-Csv (Join-Path $Root 'results\final_classification_rule_based.csv') | Where-Object { $_.case_number -eq "$Case" }
$id = $cand.case_id

Write-Host ""
Write-Host "=== Case $Case  $id ===" -ForegroundColor Cyan
Write-Host "Project : $($cand.organisation)/$($cand.project)"
Write-Host "Update  : $($cand.dependency_group):$($cand.dependency_artifact)  $($cand.previous_version) -> $($cand.new_version)"

function Invoke-Phase([string]$phase, [string]$mvn, [string]$tag = '') {
  if (-not $tag) { $tag = $phase }
  $img = "ghcr.io/chains-project/breaking-updates:$id-$phase"
  $log = Join-Path $LogDir "case${Case}_$tag.log"
  if (-not $SummaryOnly) {
    $present = docker images -q $img
    if (-not $present) {
      Write-Host "Image not present locally, pulling $img ..." -ForegroundColor Yellow
      $old = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
      docker pull -q $img | Out-Null
      $ErrorActionPreference = $old
    }
    $name = "manual-case$Case-$tag"
    Write-Host "Running $phase in container $name (this can take several minutes) ..." -ForegroundColor Yellow
    $start = Get-Date
    # Merge stderr into stdout INSIDE the container (exec 2>&1). Windows PowerShell 5.1 turns native stderr
    # lines into terminating errors under $ErrorActionPreference='Stop', which truncated earlier runs.
    # The backtick keeps $? literal so the container's shell expands it.
    $cmd = "exec 2>&1; $mvn; echo MAVEN_EXIT=`$?"
    $old = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
    try {
      & docker run --rm --name $name --entrypoint sh $img -c $cmd |
        ForEach-Object { "$_" } | Out-File -FilePath $log -Encoding utf8
    } finally { $ErrorActionPreference = $old }
    Write-Host ("Finished in {0:N0} s -> {1}" -f ((Get-Date) - $start).TotalSeconds, $log)
  }
  if (-not (Test-Path $log)) { Write-Host "No log for $phase yet." -ForegroundColor Red; return }
  $lines = Get-Content $log -Encoding utf8
  Write-Host ""
  Write-Host "--- $tag summary ---" -ForegroundColor Green
  ($lines | Select-String -Pattern 'BUILD (SUCCESS|FAILURE)' | Select-Object -Last 1).Line
  ($lines | Select-String -Pattern 'MAVEN_EXIT=\d+' | Select-Object -Last 1).Line
  $lines | Select-String -Pattern 'Tests run: \d+, Failures: \d+, Errors: \d+, Skipped: \d+\s*$' | ForEach-Object { "  " + $_.Line.Trim() }
  $lines | Select-String -Pattern '(SUCCESS|FAILURE|SKIPPED) \[|SKIPPED$' | ForEach-Object { "  reactor: " + $_.Line.Replace('[INFO] ', '').Trim() }
  if ($tag -eq 'breaking') {
    Write-Host "First failing tests / errors:" -ForegroundColor Green
    $lines | Select-String -Pattern '<<< (FAILURE|ERROR)!' | Where-Object { $_.Line -notmatch 'Tests run' } |
      Select-Object -First 3 | ForEach-Object {
        "  " + $_.Line.Trim()
        $i = $_.LineNumber
        $lines[$i..($i + 2)] | ForEach-Object { "      " + $_.Trim() }
      }
    Write-Host "First 'Caused by' lines (the initiating cause is usually the deepest one):" -ForegroundColor Green
    $lines | Select-String -Pattern '^\s*Caused by:' | Select-Object -First 4 | ForEach-Object { "  " + $_.Line.Trim() }
    Write-Host "Linkage / bytecode signals:" -ForegroundColor Green
    $sig = $lines | Select-String -Pattern 'NoClassDefFoundError|NoSuchMethodError|NoSuchFieldError|AbstractMethodError|IncompatibleClassChangeError|UnsupportedClassVersionError|VerifyError|IllegalAccessError|ClassNotFoundException|API incompatibility' |
      ForEach-Object { $_.Matches[0].Value } | Group-Object | ForEach-Object { "  $($_.Name) x$($_.Count)" }
    if ($sig) { $sig } else { "  none" }
    $slf = $lines | Select-String -Pattern '^SLF4J: (Ignoring binding|No SLF4J providers|Failed to load class)' | Select-Object -First 3
    if ($slf) { Write-Host "SLF4J console:" -ForegroundColor Green; $slf | ForEach-Object { "  " + $_.Line } }
  }
}

if ($Pre) { Invoke-Phase 'pre' 'mvn clean test -B' }
Invoke-Phase 'breaking' 'mvn clean test -B'

if ($Tree) {
  $g = $cand.dependency_group
  # dependency:tree is not cached in the images, so Maven downloads the plugin from Maven Central
  Invoke-Phase 'breaking' "mvn -B -DskipTests test-compile dependency:tree -Dincludes=$g" 'tree' | Out-Null
  Write-Host "Dependency tree ($g):" -ForegroundColor Green
  Get-Content (Join-Path $LogDir "case${Case}_tree.log") -Encoding utf8 |
    Select-String -Pattern "^\[INFO\] [^-\[].*:jar:|^\[INFO\] [|+\\ -]+.*$([regex]::Escape($g))" | ForEach-Object { "  " + $_.Line.Replace('[INFO] ', '') }
}

Write-Host ""
Write-Host "--- Proposed classification ---" -ForegroundColor Cyan
Write-Host "Label   : $($final.rule_based_label)   (rule $($final.rule): $($final.rule_name))"
if ($final.behavior_change_category) { Write-Host "Category: $($final.behavior_change_category)" }
Write-Host "Cause   : $($final.primary_cause)"
if ($final.behavior_change) { Write-Host "Change  : $($final.behavior_change)" }
Write-Host "Codex   : $($final.codex_label)   Claude blind: $($final.claude_blind_label)"
Write-Host ""
Write-Host "Check: (1) the first error above matches 'Cause' and is not a follow-on;" -ForegroundColor Cyan
Write-Host "       (2) BUILD/MAVEN_EXIT and test counts match the original run;" -ForegroundColor Cyan
Write-Host "       (3) the label follows from the rule. Record your label in ..\verification_plan\human_sample.csv." -ForegroundColor Cyan
