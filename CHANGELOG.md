# Changelog

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
