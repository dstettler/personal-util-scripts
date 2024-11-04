mkdir pyrelease

$archiveTag = ""

if ($null -eq $args[0]) {
    $archiveTag = $(git rev-parse HEAD)
} else {
    $archiveTag = $args[0]
}

$pyreleaseName = "python-bins-$archiveTag.zip"

# Build simple utils
Get-ChildItem "." -Filter *.py | 
ForEach-Object {
    pyinstaller $_
}

Get-ChildItem "dist" | 
ForEach-Object {
    $distpath = $(Split-Path -Path $_ -Leaf)
    Get-ChildItem dist\$distpath -Filter *.exe | 
    ForEach-Object {
        $filename = $(Split-Path -Path $_ -Leaf)
        Copy-Item dist\$distpath\$filename pyrelease\$filename
    }
}

# Delete simple util intermediary files
Remove-Item build -Recurse -Force 
Remove-Item dist -Recurse -Force 

# Build pin-to-all-apps
mkdir pyrelease\pin-to-all-apps
Get-ChildItem "pin-to-all-apps" -Filter *.py | 
ForEach-Object {
    $pyFile = $(Split-Path -Path $_ -Leaf)
    pyinstaller .\pin-to-all-apps\$pyFile
}

Get-ChildItem "dist" | 
ForEach-Object {
    $distpath = $(Split-Path -Path $_ -Leaf)
    Get-ChildItem dist\$distpath -Filter *.exe | 
    ForEach-Object {
        $filename = $(Split-Path -Path $_ -Leaf)
        Copy-Item dist\$distpath\$filename pyrelease\pin-to-all-apps\$filename
    }
}

Copy-Item .\pin-to-all-apps\reg .\pyrelease\pin-to-all-apps -Recurse

# Delete pin-to-all-apps intermediary files
Remove-Item build -Recurse -Force 
Remove-Item dist -Recurse -Force 

$compress = @{
    Path = ".\pyrelease\*"
    CompressionLevel = "Optimal"
    DestinationPath = ".\$pyreleaseName"
}
Compress-Archive @compress

Remove-Item pyrelease -Recurse -Force 

Copy-Item $pyreleaseName release