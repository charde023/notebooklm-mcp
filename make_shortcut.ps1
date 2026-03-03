$desktopPath = [Environment]::GetFolderPath("Desktop")
$tempPath = "C:\workspace\Daily_news\notebooklm-mcp\Daily News Automator.lnk"
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($tempPath)
$Shortcut.TargetPath = "C:\workspace\Daily_news\notebooklm-mcp\Run_DailyNews.bat"
$Shortcut.IconLocation = "C:\workspace\Daily_news\notebooklm-mcp\stylish_app_icon.ico"
$Shortcut.WorkingDirectory = "C:\workspace\Daily_news\notebooklm-mcp"
$Shortcut.Save()

Move-Item -Path $tempPath -Destination "$desktopPath\Daily News Automator.lnk" -Force
Write-Host "Shortcut successfully moved to Desktop!"
