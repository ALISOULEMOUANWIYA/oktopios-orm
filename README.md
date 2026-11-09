# oktopios-orm 🐙🗄️

ORM pour le langage **[Oktopios](https://pypi.org/project/oktopios/)** — dans
l'esprit de **Doctrine** (Symfony) et de l'**ORM de Django** : modèles déclarés
par décorateurs, migrations automatiques, dépôt générique et query-builder.

Deuxième couche de l'écosystème :
**langage `oktopios` → `oktopios-orm` → `oktopios-framework`**.

## Installation

```bash
pip install oktopios-orm
```

Cela installe aussi le langage `oktopios` (dépendance). Comme Django a besoin de
Python et Doctrine de PHP, `oktopios-orm` a besoin de l'interpréteur `oktopios`.

## Utilisation

Dans un fichier `.okp` :

```okp
use "oktopios_orm/orm.okp"     // résolu depuis le paquet installé
inject Type

@Entity("articles")
class Article {
    @Id
    var id: int
    @Column("titre")
    var title: string
    var vues: int
    fun __construct(title: string, vues: int) {
        this.title = title
        this.vues = vues
    }
}

var schema = new Schema()
var sample = new Article("", 0)
schema.migrate("blog.db", sample)   // CREATE TABLE articles (id INTEGER PRIMARY KEY, titre TEXT, vues INTEGER)

var repo = new Repo("blog.db", sample)
var a = new Article("Bonjour", 100)
Type.set(a, "id", 1)
repo.save(a)

for (x in repo.all()) { print(x.title) }

var q = new Query("blog.db", "articles")
print(q.select("id, titre, vues").where("vues", ">", 50).orderBy("vues", "DESC").get())
```

Exécuter : `okp examples/blog.okp`

## Contenu (`oktopios_orm/orm.okp`)

- **`Schema`** — migrations : génère le schéma SQL depuis les modèles décorés
  (`@Entity`, `@Id`, `@Column`) ; mapping des types (`int→INTEGER`, `string→TEXT`,
  `float→REAL`, `bool→INTEGER`).
- **`Repo`** — dépôt générique : `save`, `all`, `findBy`, `remove`, hydratation
  ligne → objet typé (par réflexion).
- **`Query`** — constructeur de requêtes fluide : `select().where().orderBy().get()`,
  paramétré (anti-injection).

## Relations `@ManyToOne` 🔗

```okp
@Entity("auteurs")
class Auteur { @Id var id: int  @Column("nom") var nom: string }

@Entity("articles")
class Article {
    @Id var id: int
    @Column("titre") var titre: string
    @ManyToOne("Auteur") var auteur: any      // colonne FK : auteur_id
}

var repoA = new Repo(db, new Auteur())
var a = new Auteur(); a.nom = "Awa"; repoA.save(a)   // save réaffecte a.id

var repoArt = new Repo(db, new Article())
var art = new Article(); art.titre = "Hello"; art.auteur = a
repoArt.save(art)                                    // écrit auteur_id = a.id

var trouve = repoArt.find(1)
print(trouve.auteur.nom)                             // -> "Awa" (objet lié chargé)
```

`@ManyToOne("Classe")` crée une colonne de clé étrangère `<champ>_id` (ou le 2ᵉ
argument), écrite par `save` et chargée par `find`/`findBy` (un niveau).

### Collections : `@OneToMany` et `@ManyToMany`

```okp
@Entity("auteurs")
class Auteur {
    @Id var id: int
    @Column("nom") var nom: string
    @OneToMany("Article", "auteur_id") var articles: any     // inverse de @ManyToOne
}

@Entity("articles")
class Article {
    @Id var id: int
    @Column("titre") var titre: string
    @ManyToOne("Auteur") var auteur: any
    @ManyToMany("Tag", "article_tag", "article_id", "tag_id") var tags: any
}

var auteur = repoAuteur.find(1)
for (a in auteur.articles) { print(a.titre) }      // @OneToMany chargé

repoArt.attach(article, "tags", tag)                // lie via la table de jointure
var art = repoArt.find(1)
for (t in art.tags) { print(t.libelle) }           // @ManyToMany chargé
```

`@ManyToMany` crée la **table de jointure** à la migration ; `Repo.attach` y
insère les liens. Les collections sont chargées sur un niveau (pas de récursion).

## Pagination 📄

```okp
print(repoArt.count())            // nombre total de lignes
for (x in repoArt.page(10, 2)) {  // page 2, 10 par page (entités hydratées)
    print(x.titre)
}
// Bas niveau : Query.limit(n).offset(d) + Query.count()
```

## Query enrichi 🔎

```okp
// constructeur fluide, puis hydratation en entités
var actifs = repo.hydrateRows(
    repo.query()
        .where("age", ">", 18)
        .orWhere("role", "=", "admin")
        .orderBy("nom", "ASC")
        .limit(20)
        .get()
)

repo.query().whereIn("id", [1, 2, 3]).count()        // IN (…)
repo.query().like("titre", "%okp%").first()          // LIKE, 1re ligne | null
repo.query().join("auteurs a", "a.id = articles.auteur_id").get()
```

## Migrations incrémentales (façon Alembic) 🧬

Suit les migrations déjà appliquées (table `oktopios_migrations`) et n'exécute
que les nouvelles, dans l'ordre — **idempotent** :

```okp
var mig = new Migrator("app.db")
var n = mig.migrer([
    { "nom": "001_users",  "sql": "CREATE TABLE users (id INTEGER PRIMARY KEY, nom TEXT)" },
    { "nom": "002_ville",  "sql": "ALTER TABLE users ADD COLUMN ville TEXT" }
])
print(n)                    // nb réellement appliquées (0 au 2e lancement)
print(mig.appliquees())    // ["001_users", "002_ville"]
```

## Décorateurs reconnus

| Décorateur | Cible | Effet |
|---|---|---|
| `@Entity("table")` | classe | nom de la table |
| `@Column("colonne")` | champ | nom de la colonne |
| `@Id` | champ | clé primaire (auto-générée, réaffectée par `save`) |
| `@ManyToOne("Classe", "fk"?)` | champ | relation N-1 (colonne FK ici) |
| `@OneToMany("Enfant", "fk")` | champ | collection inverse (1-N) |
| `@ManyToMany("Autre", "jointure", "fk_ici", "fk_autre")` | champ | relation N-N (table de jointure) |

## Licence

MIT © Mouanwiya Ali Soule
