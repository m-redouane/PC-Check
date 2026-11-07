#define MyAppName "PC Check"
#define MyAppVersion "1.0.6"
#define MyAppPublisher "Redouane MHEND"

[Setup]
AppId={{55F981E3-4110-4A32-A3DE-B4BF1EF799B9}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
; Crée le dossier dans C:\Program Files\PC Check
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=C:\Users\mhend\PC-Check\Licence.txt
OutputBaseFilename=PC-Check-Setup-v1.0.6
SetupIconFile=C:\Users\mhend\PC-Check\assets\logo.ico
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Registry]
; Sauvegarde la langue de l'installateur dans le registre de l'utilisateur
Root: HKCU; Subkey: "Software\PCCheck"; ValueType: string; ValueName: "Langue"; ValueData: "{language}"; Flags: uninsdeletekey

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Tâches supplémentaires:"

[Files]
; DestDir est maintenant {app} (le dossier Program Files) au lieu de {win}
Source: "C:\Users\mhend\PC-Check\dist\PC-Check.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Raccourci dans le menu Démarrer
Name: "{group}\{#MyAppName}"; Filename: "{app}\PC-Check.exe"
; Raccourci sur le bureau
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\PC-Check.exe"; Tasks: desktopicon

[Run]
; Lancer l'application à la fin de l'installation
Filename: "{app}\PC-Check.exe"; Description: "Lancer {#MyAppName} maintenant"; Flags: nowait postinstall skipifsilent