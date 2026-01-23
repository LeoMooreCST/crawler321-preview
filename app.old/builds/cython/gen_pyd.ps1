rm -r build
rm -r dist
rm -r crawler321.egg-info
rm -r output
cd ../../
python setup.py build_ext --inplace
python setup.py sdist bdist_wheel

$buildFolder = ".\builds\cython\"
mv build $buildFolder
mv dist $buildFolder
mv crawler321.egg-info $buildFolder
# 设置源文件夹和目标文件夹路径
$sourceFolder = ".\crawler321\"   # 替换为你的源文件夹路径
$c_destinationFolder = ".\builds\cython\output\c"  # 替换为你的目标文件夹路径
$pyd_destinationFolder = ".\builds\cython\output\pyd"  # 替换为你的目标文件夹路径

# 检查目标文件夹是否存在，如果不存在则创建
if (-Not (Test-Path $c_destinationFolder)) {
    New-Item -ItemType Directory -Path $c_destinationFolder
}
if (-Not (Test-Path $pyd_destinationFolder)) {
    New-Item -ItemType Directory -Path $pyd_destinationFolder
}

# 查找并移动所有 .c 和 .pyd 文件
Get-ChildItem -Path $sourceFolder -Filter *.c -Recurse | Move-Item -Destination $c_destinationFolder
Get-ChildItem -Path $sourceFolder -Filter *.pyd -Recurse | Move-Item -Destination $pyd_destinationFolder

Write-Host "All .c and .pyd files have been moved to .\builds\cython\output"


