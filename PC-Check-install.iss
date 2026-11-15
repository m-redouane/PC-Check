#define MyAppName "PC Check"
#define MyAppVersion "1.0.6"
#define MyAppPublisher "Redouane MHEND"

[Setup]
AppName=PC Check
AppVersion=1.0.6
AppPublisher=Redouane MHEND
AppPublisherURL=https://pc-check.fr
DefaultDirName={autopf}\PC-Check
DefaultGroupName=PC Check
OutputDir=output
OutputBaseFilename=PC-Check-Setup-v1.0.6
Compression=lzma
SolidCompression=yes
; --- CES LIGNES SONT CRUCIALES POUR APPARAÎTRE DANS LES APPS ---
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\pc_check.exe

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Registry]
; Sauvegarde la langue de l'installateur dans le registre de l'utilisateur
Root: HKCU; Subkey: "Software\PCCheck"; ValueType: string; ValueName: "Langue"; ValueData: "{language}"; Flags: uninsdeletekey

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le bureau"; GroupDescription: "Tâches supplémentaires:"

[Files]
Source: "dist\PC-Check\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Assure-toi que ton en.qm est bien copié dans le dossier de destination
Source: "en.qm"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\PC Check"; Filename: "{app}\pc_check.exe"
Name: "{autodesktop}\PC Check"; Filename: "{app}\pc_check.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\PC-Check.exe"; Description: "Run PC Check"; Flags: nowait postinstall skipifsilent runascurrentuser