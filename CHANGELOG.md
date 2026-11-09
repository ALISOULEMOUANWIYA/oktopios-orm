# Changelog

## [0.5.0] — Query enrichi + migrations incrémentales

### Ajouté
- **`Query`** : `orWhere`, `whereIn(col, liste)`, `like(col, motif)`,
  `join(table, on)`, `first()` (en plus de `where`/`orderBy`/`limit`/`offset`/
  `count`/`get`). `Repo.query()` crée une requête liée à la table, et
  `Repo.hydrateRows(lignes)` transforme des lignes en entités :
  ```okp
  repo.hydrateRows(repo.query().where("age", ">", 18).orderBy("nom", "ASC").get())
  ```
- **`Migrator`** — migrations incrémentales façon Alembic : suit les migrations
  appliquées dans une table `oktopios_migrations`, n'exécute que les nouvelles,
  dans l'ordre. `appliquer(nom, sql)`, `migrer(liste)` (idempotent),
  `estApplique(nom)`, `appliquees()`.

## [0.4.0] — Relations `@OneToMany` et `@ManyToMany`

### Ajouté
- **`@OneToMany("ClasseEnfant", "fk_dans_enfant")`** — collection inverse d'un
  `@ManyToOne` : `find`/`hydrate` charge la liste des enfants
  (ex. `auteur.articles`).
- **`@ManyToMany("Autre", "table_jointure", "fk_ici", "fk_autre")`** — relation
  N-N via une table de jointure :
  - `Schema.migrate` crée automatiquement la table de jointure ;
  - `Repo.attach(entity, champ, lie)` insère un lien ;
  - `find`/`hydrate` charge la collection liée par jointure (ex. `article.tags`).
- Les collections (`@OneToMany`/`@ManyToMany`) ne créent pas de colonne sur la
  table de l'entité et sont ignorées par `save` ; chargées un seul niveau
  (pas de récursion).

## [0.3.0] — Relations `@ManyToOne` + pagination

### Ajouté
- **Relations `@ManyToOne("ClasseLiee", "colonne_fk"?)`** sur un champ :
  - `Schema.migrate` crée la colonne de clé étrangère (`<champ>_id` par défaut) ;
  - `Repo.save` écrit la clé étrangère (id de l'objet lié) ;
  - `Repo.hydrate` / `Repo.find(id)` chargent l'objet lié (un niveau de
    profondeur, sans récursion) → `article.auteur.nom` fonctionne.
- **Pagination** : `Repo.count()` et `Repo.page(perPage, page)` (entités
  hydratées) ; `Query.limit(n)`, `Query.offset(d)` et `Query.count()`.
- `Repo.save` **réaffecte la clé primaire générée** sur l'entité (comme
  Django/Doctrine) — nécessaire pour écrire les relations juste après.

### Changé
- Dépendance relevée à **`oktopios>=0.16.0`** (listes concaténées indexables,
  requises par l'hydratation).

## [0.2.0] — `save` : clé primaire auto-générée + nouvel id

### Corrigé / Changé
- `Repo.save(entity)` **omet désormais le champ `@Id`** à l'insertion : la base
  auto-génère la clé primaire (avant, un `@Id` de type `int` non initialisé
  valait `0` et provoquait `UNIQUE constraint failed` dès la 2ᵉ insertion).
- `save` renvoie maintenant l'**identifiant de la ligne créée** (grâce à
  `execSQL` qui renvoie `lastrowid` sur INSERT).
- Dépendance relevée à **`oktopios>=0.15.0`**.

## [0.1.0] — ORM initial
- `Schema` (migrations), `Repo` (CRUD + hydratation), `Query` (constructeur fluide).
- Décorateurs `@Entity`, `@Column`, `@Id`.
