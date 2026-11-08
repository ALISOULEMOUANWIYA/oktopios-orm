# Changelog

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
