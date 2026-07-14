#define MyAppName "AgroSocial Analytics"
#define MyAppVersion "1.0"
#define MyAppPublisher "Universidad Laica Eloy Alfaro de Manabí"
#define MyAppExeName "AgroSocialAnalytics.exe"

[Setup]
AppId={{C9E8A2F4-74C6-4D56-91A5-52E5E1D5A111}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\AgroSocial Analytics
DefaultGroupName=AgroSocial Analytics
OutputDir=Instalador
OutputBaseFilename=Setup_AgroSocialAnalytics
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
SetupIconFile=web\static\img\logo_uleam.ico
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Files]
Source: "dist\AgroSocialAnalytics\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AgroSocial Analytics"; Filename: "{app}\AgroSocialAnalytics.exe"
Name: "{autodesktop}\AgroSocial Analytics"; Filename: "{app}\AgroSocialAnalytics.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\AgroSocialAnalytics.exe"; Description: "Ejecutar AgroSocial Analytics"; Flags: nowait postinstall skipifsilent