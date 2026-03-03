$desktopPath = [Environment]::GetFolderPath("Desktop")
$tempPath = "C:\workspace\Daily_news\notebooklm-mcp\Daily News Automator.lnk"

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($tempPath)

# Use cmd.exe as the target so Windows allows pinning it
$Shortcut.TargetPath = "cmd.exe"
$Shortcut.Arguments = '/c "C:\workspace\Daily_news\notebooklm-mcp\Run_DailyNews.bat"'

# Override the default CMD icon with our custom one
$Shortcut.IconLocation = "C:\workspace\Daily_news\notebooklm-mcp\stylish_app_icon.ico"
$Shortcut.WorkingDirectory = "C:\workspace\Daily_news\notebooklm-mcp"
$Shortcut.Save()

Move-Item -Path $tempPath -Destination "$desktopPath\Daily News Automator.lnk" -Force
Write-Host "Pinnable shortcut successfully created and moved to Desktop!"
