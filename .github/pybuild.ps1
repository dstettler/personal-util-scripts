mkdir pyrelease

# Build simple utils
Get-ChildItem "." -Filter *.py | 
ForEach-Object {
    pyinstaller $_
}

Get-ChildItem "dist" | 
ForEach-Object {
    $distpath = $_
    Get-ChildItem dist\$distpath -Filter *.exe | 
    ForEach-Object {
        Copy-Item dist\$distpath\$_ pyrelease\$_
    }
}

# Delete simple util intermediary files
Remove-Item build -Recurse -Force 
Remove-Item dist -Recurse -Force 

# Build pin-to-all-apps
mkdir pyrelease\pin-to-all-apps
Get-ChildItem "pin-to-all-apps" -Filter *.py | 
ForEach-Object {
    pyinstaller .\pin-to-all-apps\$_
}

Get-ChildItem "dist" | 
ForEach-Object {
    $distpath = $_
    Get-ChildItem dist\$distpath -Filter *.exe | 
    ForEach-Object {
        Copy-Item dist\$distpath\$_ pyrelease\pin-to-all-apps\$_
    }
}

Copy-Item .\pin-to-all-apps\reg .\pyrelease\pin-to-all-apps -Recurse

# Delete pin-to-all-apps intermediary files
Remove-Item build -Recurse -Force 
Remove-Item dist -Recurse -Force 

$archiveCommit = $(git rev-parse HEAD)

$compress = @{
    Path = ".\pyrelease\*"
    CompressionLevel = "Optimal"
    DestinationPath = ".\pyrelease-$archiveCommit.zip"
}
Compress-Archive @compress

Remove-Item pyrelease -Recurse -Force 

Copy-Item "pyrelease-$archiveCommit.zip" release