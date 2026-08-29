# ============================================================
# sauvegarde_bdd.ps1
#
# Sauvegarde automatique de la base PostgreSQL "keur_massar_nord" via
# pg_dump (format compressé, prêt à restaurer avec pg_restore).
#
# - Lit les identifiants directement dans le fichier .env du projet
#   (pas besoin de les redonner ici).
# - Stocke les sauvegardes dans le dossier "sauvegardes\" à la racine
#   du projet, un fichier par jour.
# - Supprime automatiquement les sauvegardes de plus de 30 jours,
#   pour ne pas remplir le disque indéfiniment.
#
# UTILISATION MANUELLE (test) :
#   powershell -ExecutionPolicy Bypass -File sauvegarde_bdd.ps1
#
# UTILISATION AUTOMATIQUE : voir LISEZ-MOI-SAUVEGARDES.txt pour la
# configuration du Planificateur de tâches Windows (une fois par jour).
# ============================================================

$ErrorActionPreference = "Stop"

# --- Emplacement de pg_dump.exe ---
# Ajustez cette ligne si votre PostgreSQL est installé ailleurs ou
# dans une autre version (cherchez "pg_dump.exe" dans
# C:\Program Files\PostgreSQL\ si besoin).
$PG_DUMP = "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe"

# --- Dossier du projet (celui où se trouve ce script) ---
$PROJET_DIR = $PSScriptRoot
$ENV_FILE = Join-Path $PROJET_DIR ".env"
$SAUVEGARDES_DIR = Join-Path $PROJET_DIR "sauvegardes"
$JOURS_RETENTION = 30

if (-not (Test-Path $PG_DUMP)) {
    Write-Host "ERREUR : pg_dump.exe introuvable à $PG_DUMP" -ForegroundColor Red
    Write-Host "Modifiez la variable `$PG_DUMP en haut de ce script avec le bon chemin." -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $ENV_FILE)) {
    Write-Host "ERREUR : fichier .env introuvable à $ENV_FILE" -ForegroundColor Red
    exit 1
}

# --- Lecture des identifiants depuis .env (format simple CLE=valeur) ---
$envValues = @{}
Get-Content $ENV_FILE | ForEach-Object {
    if ($_ -match '^\s*([A-Z_]+)\s*=\s*(.*)\s*$') {
        $envValues[$matches[1]] = $matches[2]
    }
}

$DB_NAME = $envValues["DB_NAME"]
$DB_USER = $envValues["DB_USER"]
$DB_PASSWORD = $envValues["DB_PASSWORD"]
$DB_HOST = $envValues["DB_HOST"]
$DB_PORT = $envValues["DB_PORT"]

if (-not $DB_NAME -or -not $DB_USER) {
    Write-Host "ERREUR : DB_NAME ou DB_USER introuvable dans .env" -ForegroundColor Red
    exit 1
}

# --- Préparation du dossier et du nom de fichier ---
if (-not (Test-Path $SAUVEGARDES_DIR)) {
    New-Item -ItemType Directory -Path $SAUVEGARDES_DIR | Out-Null
}

$horodatage = Get-Date -Format "yyyy-MM-dd_HHmm"
$fichierSortie = Join-Path $SAUVEGARDES_DIR "kmsn_$horodatage.backup"

# --- Lancement de pg_dump (format compressé -Fc, pour pg_restore) ---
Write-Host "Sauvegarde de la base '$DB_NAME' en cours..."

$env:PGPASSWORD = $DB_PASSWORD
& $PG_DUMP -h $DB_HOST -p $DB_PORT -U $DB_USER -Fc -f $fichierSortie $DB_NAME
$codeRetour = $LASTEXITCODE
Remove-Item Env:\PGPASSWORD

if ($codeRetour -ne 0) {
    Write-Host "ERREUR : pg_dump a échoué (code $codeRetour)." -ForegroundColor Red
    exit 1
}

$tailleMo = [math]::Round((Get-Item $fichierSortie).Length / 1MB, 1)
Write-Host "OK : sauvegarde créée -> $fichierSortie ($tailleMo Mo)" -ForegroundColor Green

# --- Nettoyage des sauvegardes de plus de 30 jours ---
$dateLimite = (Get-Date).AddDays(-$JOURS_RETENTION)
$anciennes = Get-ChildItem -Path $SAUVEGARDES_DIR -Filter "kmsn_*.backup" |
    Where-Object { $_.LastWriteTime -lt $dateLimite }

foreach ($fichier in $anciennes) {
    Remove-Item $fichier.FullName
    Write-Host "Supprimé (plus de $JOURS_RETENTION jours) : $($fichier.Name)"
}

Write-Host "Terminé."
