# NIVARA AREIS — permanent dashboard launcher (never hardcode a dead Streamlit URL in the shortcut)
param(
    [string]$ConfigDir = $(Join-Path $env:LOCALAPPDATA "NIVARA"),
    [switch]$ForceWizard
)

$ErrorActionPreference = "Stop"
$ConfigFile = Join-Path $ConfigDir "dashboard.url"
$DefaultSubdomain = "nivara-areis"
$PrimaryUrl = "https://nivara-dashboard.onrender.com/"
$DeployRepo = "narendhrareddi-ship-it/Nivara-AREIS"
$DeployBranch = "main"
$DeployEntry = "streamlit_app.py"
$DeployPage = "https://share.streamlit.io"
$GitHubDeployLink = "https://github.com/$DeployRepo/blob/$DeployBranch/$DeployEntry"

function Read-SavedUrl {
    if (-not (Test-Path $ConfigFile)) { return "" }
    $raw = (Get-Content $ConfigFile -Raw -ErrorAction SilentlyContinue).Trim()
    if ($raw -match '^https?://') { return $raw.TrimEnd('/') + '/' }
    return ""
}

function Save-Url([string]$Url) {
    if (-not (Test-Path $ConfigDir)) {
        New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
    }
    $normalized = $Url.Trim().TrimEnd('/') + '/'
    Set-Content -Path $ConfigFile -Value $normalized -Encoding UTF8
    return $normalized
}

function Test-DashboardUrl([string]$Url) {
    if (-not $Url) { return $false }
    try {
        $response = Invoke-WebRequest -Uri $Url -TimeoutSec 20 -UseBasicParsing
        if ($response.StatusCode -ge 400) { return $false }
        $body = $response.Content
        if ($body -match 'do not have access|does not exist|You''re currently signed in') { return $false }
        if ($body -match '<title>Streamlit</title>' -or $body -match 'streamlit') { return $true }
        return $true
    }
    catch {
        return $false
    }
}

function Show-Wizard {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $form = New-Object System.Windows.Forms.Form
    $form.Text = "NIVARA AREIS — Set Dashboard URL"
    $form.Size = New-Object System.Drawing.Size(620, 420)
    $form.StartPosition = "CenterScreen"
    $form.FormBorderStyle = "FixedDialog"
    $form.MaximizeBox = $false

    $label = New-Object System.Windows.Forms.Label
    $label.Location = New-Object System.Drawing.Point(15, 15)
    $label.Size = New-Object System.Drawing.Size(570, 150)
    $label.Text = @"
The saved dashboard URL is missing or not reachable.

1) Click DEPLOY to open Streamlit Cloud (sign in as narendhrareddi-ship-it).
2) Deploy repo $DeployRepo, branch $DeployBranch, file $DeployEntry.
3) Render dashboard (auto-deployed): $PrimaryUrl
4) Or Streamlit subdomain: $DefaultSubdomain  ->  https://$DefaultSubdomain.streamlit.app/
5) After deploy succeeds, paste your live URL below and click SAVE.
"@
    $form.Controls.Add($label)

    $text = New-Object System.Windows.Forms.TextBox
    $text.Location = New-Object System.Drawing.Point(15, 175)
    $text.Size = New-Object System.Drawing.Size(570, 24)
    $text.Text = $PrimaryUrl
    $form.Controls.Add($text)

    $deployBtn = New-Object System.Windows.Forms.Button
    $deployBtn.Location = New-Object System.Drawing.Point(15, 220)
    $deployBtn.Size = New-Object System.Drawing.Size(120, 32)
    $deployBtn.Text = "Deploy"
    $deployBtn.Add_Click({
        Start-Process $DeployPage
        Start-Process $GitHubDeployLink
    })
    $form.Controls.Add($deployBtn)

    $saveBtn = New-Object System.Windows.Forms.Button
    $saveBtn.Location = New-Object System.Drawing.Point(470, 320)
    $saveBtn.Size = New-Object System.Drawing.Size(115, 32)
    $saveBtn.Text = "Save && Open"
    $saveBtn.DialogResult = [System.Windows.Forms.DialogResult]::OK
    $form.AcceptButton = $saveBtn
    $form.Controls.Add($saveBtn)

    $cancelBtn = New-Object System.Windows.Forms.Button
    $cancelBtn.Location = New-Object System.Drawing.Point(345, 320)
    $cancelBtn.Size = New-Object System.Drawing.Size(115, 32)
    $cancelBtn.Text = "Cancel"
    $cancelBtn.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
    $form.Controls.Add($cancelBtn)

    $result = $form.ShowDialog()
    if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
        return $text.Text.Trim()
    }
    return ""
}

$url = Read-SavedUrl
if ($ForceWizard -or -not (Test-DashboardUrl $url)) {
    $picked = Show-Wizard
    if (-not $picked) {
        [System.Windows.Forms.MessageBox]::Show(
            "No dashboard URL saved. Deploy on Streamlit Cloud first, then run Fix-NIVARA-Shortcut.bat again.",
            "NIVARA AREIS",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Information
        ) | Out-Null
        exit 1
    }
    $url = Save-Url $picked
    if (-not (Test-DashboardUrl $url)) {
        [System.Windows.Forms.MessageBox]::Show(
            "Saved URL still not reachable:`n$url`n`nFinish deploy on Streamlit Cloud, add secrets, reboot app, then try again.",
            "NIVARA AREIS",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Warning
        ) | Out-Null
    }
}

Start-Process $url
exit 0
