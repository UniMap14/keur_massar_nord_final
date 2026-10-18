# -*- coding: utf-8 -*-
"""
Ajoute le CSS des nouvelles actions du topbar : boutons ronds
(notifications, plein ecran), badge de notification, panneau
deroulant de notifications. S'appuie sur les variables existantes
(--brand-gold, --line, --shadow-lg, etc.).

Idempotent.
"""
CHEMIN = "foncier/static/dashboard/css/dashboard.css"

with open(CHEMIN, "r", encoding="utf-8") as f:
    contenu = f.read()

erreurs = []
remplacements_ok = 0

ANCIEN = '''.topbar-search input:focus {
  outline: none;
  border-color: var(--brand-gold);
  box-shadow: 0 0 0 3px rgba(201,152,46,0.18);
}'''

NOUVEAU = '''.topbar-search input:focus {
  outline: none;
  border-color: var(--brand-gold);
  box-shadow: 0 0 0 3px rgba(201,152,46,0.18);
}

/* -------------------- TOPBAR ACTIONS (notifications, plein ecran) -------------------- */

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
}

.topbar-icon-btn {
  position: relative;
  width: 38px; height: 38px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: #fff;
  color: var(--brand-brown);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px;
  cursor: pointer;
  transition: background .15s var(--ease), border-color .15s var(--ease), transform .15s var(--ease);
}
.topbar-icon-btn:hover {
  background: var(--brand-cream);
  border-color: var(--brand-gold);
  transform: translateY(-1px);
}

.topbar-notif-badge {
  position: absolute;
  top: -4px; right: -4px;
  min-width: 17px; height: 17px;
  padding: 0 4px;
  border-radius: 999px;
  background: var(--danger);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  line-height: 1;
  box-shadow: 0 0 0 2px #fff;
}

.topbar-notif-panel {
  display: none;
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 300px;
  background: var(--brand-cream-white);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 40;
  overflow: hidden;
}
.topbar-notif-panel.open { display: block; }

.topbar-notif-panel-header {
  padding: 14px 16px;
  font-size: 12.5px;
  font-weight: 700;
  color: var(--brand-brown-dark);
  border-bottom: 1px solid var(--line);
}

.topbar-notif-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 16px;
  font-size: 13px;
  color: var(--ink);
  border-bottom: 1px solid var(--line);
  transition: background .15s var(--ease);
}
.topbar-notif-item:last-child { border-bottom: none; }
.topbar-notif-item:hover { background: var(--brand-cream); }
.topbar-notif-item .count {
  font-size: 11px;
  font-weight: 700;
  background: var(--danger-bg);
  color: var(--danger);
  padding: 2px 9px;
  border-radius: 999px;
}

.topbar-notif-empty {
  padding: 22px 16px;
  text-align: center;
  font-size: 12.5px;
  color: var(--ink-faint);
}

@media (max-width: 900px) {
  .topbar-search { display: none; }
}'''

if '.topbar-actions {' in contenu:
    pass
elif ANCIEN not in contenu:
    erreurs.append("ancre introuvable (.topbar-search input:focus)")
else:
    contenu = contenu.replace(ANCIEN, NOUVEAU, 1)
    remplacements_ok += 1

if erreurs:
    print("ERREUR(S) : rien n'a ete ecrit sur le disque.")
    for e in erreurs:
        print(" -", e)
else:
    with open(CHEMIN, "w", encoding="utf-8") as f:
        f.write(contenu)
    print(f"OK : {remplacements_ok} modification(s) appliquee(s) (ou deja presente).")