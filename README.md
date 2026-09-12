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

## Décorateurs reconnus

| Décorateur | Cible | Effet |
|---|---|---|
| `@Entity("table")` | classe | nom de la table |
| `@Column("colonne")` | champ | nom de la colonne |
| `@Id` | champ | clé primaire |

## Licence

MIT © Mouanwiya Ali Soule
