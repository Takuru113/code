[CmdletBinding()]
param(
    [string]$FolderToken,
    [string]$PythonExecutable
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$secretDirectory = Join-Path $PSScriptRoot '.secrets'
$secretPath = Join-Path $secretDirectory 'feishu-app-secret.dpapi'
$secretPointer = [IntPtr]::Zero

if (-not $PythonExecutable) {
    $bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Test-Path -LiteralPath $bundledPython) {
        $PythonExecutable = $bundledPython
    }
    else {
        $PythonExecutable = (Get-Command python.exe -ErrorAction Stop).Source
    }
}

Push-Location $repoRoot
try {
    if (Test-Path -LiteralPath $secretPath) {
        $encryptedSecret = (Get-Content -LiteralPath $secretPath -Raw).Trim()
        $secureSecret = $encryptedSecret | ConvertTo-SecureString
        Write-Host 'Loaded the DPAPI-encrypted Feishu App Secret for the current Windows user.'
    }
    else {
        Write-Host 'Paste Feishu App Secret (input is hidden and will not be stored as plaintext):'
        $secureSecret = Read-Host -AsSecureString
        New-Item -ItemType Directory -Path $secretDirectory -Force | Out-Null
        $secureSecret | ConvertFrom-SecureString | Set-Content -LiteralPath $secretPath -Encoding ASCII
        Write-Host 'Saved with Windows DPAPI encryption. Only the current Windows user can decrypt it.'
    }

    $secretPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureSecret)
    $plainSecret = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($secretPointer)

    if ([string]::IsNullOrWhiteSpace($plainSecret)) {
        throw 'App Secret cannot be empty.'
    }

    $env:FEISHU_APP_ID = 'cli_aad232d702f99bb3'
    $env:FEISHU_APP_SECRET = $plainSecret
    if ($FolderToken) {
        $env:FEISHU_FOLDER_TOKEN = $FolderToken
    }

    & $PythonExecutable automation/feishu_writer.py `
        research/talent-research.md `
        deliverables/01-style-breakdown.md `
        deliverables/02-workflow-and-prompts.md `
        deliverables/03-script-storyboard.md `
        deliverables/04-compliance-qa.md `
        --execute

    if ($LASTEXITCODE -ne 0) {
        throw "Feishu live-write verification failed. Python exit code: $LASTEXITCODE"
    }
}
finally {
    Remove-Item Env:FEISHU_APP_SECRET -ErrorAction SilentlyContinue
    Remove-Item Env:FEISHU_APP_ID -ErrorAction SilentlyContinue
    Remove-Item Env:FEISHU_FOLDER_TOKEN -ErrorAction SilentlyContinue
    $plainSecret = $null
    $encryptedSecret = $null
    $secureSecret = $null
    if ($secretPointer -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($secretPointer)
    }
    Pop-Location
}
