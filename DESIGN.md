## Schéma logique

La base de données repose sur **5 tables principales** :

- **Organisations** : regroupent clients, techniciens, interventions et événements.
- **Clients** : associés à une organisation et liés à leurs interventions.
- **Techniciens** : employés d’une organisation, pouvant créer ou réaliser des interventions.
- **Interventions** : réalisées par un technicien pour un client.
- **Événements** : étapes ou suivis liés à une intervention.

## Choix clés de modélisation

- Ajout d’un champ **created_by** dans la table _Event_ pour tracer l’auteur (technicien).
- Relations hiérarchiques claires : une organisation est l’entité racine, et toutes les autres tables y sont reliées.
- Gestion explicite des dépendances avec des règles de suppression adaptées aux besoins métier.

## Règles de transitions (on delete)

- **CASCADE** :
- Organisation → Techniciens, Clients, Interventions, Events
- Client → Interventions
- Intervention → Events

  > Permet la suppression automatique des entités dépendantes.

- **RESTRICT** :
- Technicien → Interventions

  > Empêche de supprimer un technicien tant que des interventions lui sont associées.

- **SET NULL** :
- Event.created_by → Technician
  > Un événement peut subsister même si son créateur est supprimé.

## Compromis

- **Simplicité vs intégrité** : la stratégie _CASCADE_ facilite la gestion globale en cas de suppression d’une organisation, mais implique la perte de toutes les données liées.
- **Traçabilité** : le champ _created_by_ améliore le suivi des actions, au prix d’une relation optionnelle (_SET NULL_).
- **Cohérence métier** : l’usage de _RESTRICT_ pour les techniciens garantit qu’aucune intervention ne reste sans responsable actif.

Ce design permet à la fois **flexibilité**, **traçabilité** et **cohérence** métier, tout en assurant une bonne maintenance grâce à l’ORM et à la gestion des migrations (Alembic).
