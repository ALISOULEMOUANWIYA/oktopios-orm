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

## Pagination 📄

```okp
print(repoArt.count())            // nombre total de lignes
for (x in repoArt.page(10, 2)) {  // page 2, 10 par page (entités hydratées)
    print(x.titre)
}
// Bas niveau : Query.limit(n).offset(d) + Query.count()
```

## Décorateurs reconnus

| Décorateur | Cible | Effet |
|---|---|---|
| `@Entity("table")` | classe | nom de la table |
| `@Column("colonne")` | champ | nom de la colonne |
| `@Id` | champ | clé primaire (auto-générée, réaffectée par `save`) |
| `@ManyToOne("Classe", "fk"?)` | champ | relation vers une autre entité |

## Licence

MIT © Mouanwiya Ali Soule
