# 获取当前工作路径
$currentDir = Get-Location

# 定义 ZIP 文件路径和解压目标路径
$zipFiles = @("$currentDir\chrome-win64.zip", "$currentDir\chromedriver-win64.zip")
$destinationPaths = @("$currentDir\chrome-win64", "$currentDir\chromedriver-win64")  # 解压到当前目录下的 a 和 b 文件夹

# 解压 ZIP 文件
Add-Type -AssemblyName System.IO.Compression.FileSystem

# 初始化一个变量来保存现有的 PATH 值
$envName = "Path"
$envValue = [System.Environment]::GetEnvironmentVariable($envName, [System.EnvironmentVariableTarget]::Machine)

for ($i = 0; $i -lt $zipFiles.Length; $i++) {
    $zipFilePath = $zipFiles[$i]
    $destinationPath = $destinationPaths[$i]

    # 打印调试信息
    Write-Host "Attempting to extract $zipFilePath to $destinationPath"

    # 删除现有文件夹（如果存在）
    if (Test-Path $destinationPath) {
        Remove-Item -Recurse -Force $destinationPath
    }

    # 解压 ZIP 文件到目标路径
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipFilePath, $currentDir)

    # 添加路径到系统环境变量
    if ($envValue -notlike "*$destinationPath*") {
        $envValue = "$envValue;$destinationPath"
        # 以管理员权限运行
        Start-Process powershell -ArgumentList "-Command [System.Environment]::SetEnvironmentVariable('$envName', '$envValue', [System.EnvironmentVariableTarget]::Machine)" -Verb RunAs
        Write-Host "Added $destinationPath to system PATH."
    } else {
        Write-Host "$destinationPath is already in system PATH."
    }
}

# 刷新环境变量 (使得当前会话可用)
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", [System.EnvironmentVariableTarget]::Machine)
Write-Host "Updated PATH: $env:Path"
