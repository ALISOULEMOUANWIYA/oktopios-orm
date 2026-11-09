"""
Tests d'intégration de l'ORM (oktopios-orm).

Exécute un vrai programme Oktopios qui migre une base SQLite temporaire, insère
des entités via `Repo.save`, puis relit via `all` / `findBy`. Vérifie :
  - la clé primaire est auto-générée (ids 1 et 2) ;
  - `save` renvoie le nouvel id ;
  - l'hydratation reconstruit des objets indexables (`findBy(...)[0]`).

En dev (dépôts frères côte à côte) les sources de `oktopios` (../version.0.0.1)
sont ajoutées au PYTHONPATH ; en CI on compte sur les paquets installés.
"""
import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _child_env():
    env = dict(os.environ)
    extra = [REPO_ROOT]  # pour que `use "oktopios_orm/orm.okp"` résolve via cwd
    parent = os.path.dirname(REPO_ROOT)
    lang = os.path.join(parent, "version.0.0.1")
    if os.path.isdir(lang):
        extra.append(lang)
    env["PYTHONPATH"] = os.pathsep.join(extra + [env.get("PYTHONPATH", "")])
    env["PYTHONIOENCODING"] = "utf-8"
    return env


PROG = '''use "oktopios_orm/orm.okp"

@Entity("articles")
class Article {{
    @Id
    var id: int
    @Column("titre")
    var titre: string
    @Column("contenu")
    var contenu: string
}}

var db = "{db}"
var schema = new Schema()
schema.migrate(db, new Article())
var repo = new Repo(db, new Article())

var a = new Article()
a.titre = "Bonjour"
a.contenu = "Premier"
print("save1=" + repo.save(a))

var b = new Article()
b.titre = "Oktopios"
b.contenu = "Deuxieme"
print("save2=" + repo.save(b))

var tous = repo.all()
var n = 0
for (x in tous) {{ n = n + 1 }}
print("count=" + n)

var trouves = repo.findBy("titre", "Oktopios")
print("found=" + trouves[0].contenu)
'''


def _run_okp(source, tmp_path):
    app = tmp_path / "prog.okp"
    app.write_text(source, encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-m", "vm.main", str(app)],
        cwd=REPO_ROOT, env=_child_env(),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60,
    )
    return proc.stdout.decode("utf-8", "replace")


def test_orm_crud_and_autoincrement(tmp_path):
    db = str(tmp_path / "t.db").replace("\\", "/")
    out = _run_okp(PROG.format(db=db), tmp_path)
    assert "save1=1" in out, out
    assert "save2=2" in out, out      # clé primaire auto-générée
    assert "count=2" in out, out
    assert "found=Deuxieme" in out, out   # hydratation + findBy(...)[0] indexable


PROG_REL = '''use "oktopios_orm/orm.okp"

@Entity("auteurs")
class Auteur {{
    @Id
    var id: int
    @Column("nom")
    var nom: string
}}

@Entity("articles")
class Article {{
    @Id
    var id: int
    @Column("titre")
    var titre: string
    @ManyToOne("Auteur")
    var auteur: any
}}

var db = "{db}"
var schema = new Schema()
schema.migrate(db, new Auteur())
schema.migrate(db, new Article())

var repoA = new Repo(db, new Auteur())
var a1 = new Auteur()
a1.nom = "Awa"
repoA.save(a1)
print("auteurId=" + a1.id)

var repoArt = new Repo(db, new Article())
var art1 = new Article()
art1.titre = "Premier"
art1.auteur = a1
repoArt.save(art1)
var art2 = new Article()
art2.titre = "Deuxieme"
art2.auteur = a1
repoArt.save(art2)
var art3 = new Article()
art3.titre = "Troisieme"
art3.auteur = a1
repoArt.save(art3)

var trouve = repoArt.find(1)
print("rel=" + trouve.titre + "/" + trouve.auteur.nom)
print("count=" + repoArt.count())

var p1 = repoArt.page(2, 1)
var n1 = 0
for (x in p1) {{ n1 = n1 + 1 }}
print("page1=" + n1)
var p2 = repoArt.page(2, 2)
var n2 = 0
for (x in p2) {{ n2 = n2 + 1 }}
print("page2=" + n2)
'''


def test_orm_relations_and_pagination(tmp_path):
    db = str(tmp_path / "r.db").replace("\\", "/")
    out = _run_okp(PROG_REL.format(db=db), tmp_path)
    assert "auteurId=1" in out, out          # save réaffecte l'@Id
    assert "rel=Premier/Awa" in out, out     # @ManyToOne hydraté
    assert "count=3" in out, out
    assert "page1=2" in out, out             # pagination LIMIT/OFFSET
    assert "page2=1" in out, out


PROG_COLL = '''use "oktopios_orm/orm.okp"

@Entity("auteurs")
class Auteur {{
    @Id var id: int
    @Column("nom") var nom: string
    @OneToMany("Article", "auteur_id") var articles: any
}}
@Entity("tags")
class Tag {{
    @Id var id: int
    @Column("libelle") var libelle: string
}}
@Entity("articles")
class Article {{
    @Id var id: int
    @Column("titre") var titre: string
    @ManyToOne("Auteur") var auteur: any
    @ManyToMany("Tag", "article_tag", "article_id", "tag_id") var tags: any
}}

var db = "{db}"
var schema = new Schema()
schema.migrate(db, new Auteur())
schema.migrate(db, new Tag())
schema.migrate(db, new Article())

var repoAut = new Repo(db, new Auteur())
var awa = new Auteur()
awa.nom = "Awa"
repoAut.save(awa)

var repoTag = new Repo(db, new Tag())
var t1 = new Tag()
t1.libelle = "news"
repoTag.save(t1)
var t2 = new Tag()
t2.libelle = "tech"
repoTag.save(t2)

var repoArt = new Repo(db, new Article())
for (k in [1, 2, 3]) {{
    var a = new Article()
    a.titre = "Article " + k
    a.auteur = awa
    repoArt.save(a)
}}
var art1 = repoArt.find(1)
repoArt.attach(art1, "tags", t1)
repoArt.attach(art1, "tags", t2)

var auteurCharge = repoAut.find(1)
var c = 0
for (x in auteurCharge.articles) {{ c = c + 1 }}
print("o2m=" + c)

var artCharge = repoArt.find(1)
var libelles = ""
for (t in artCharge.tags) {{ libelles = libelles + t.libelle + "," }}
print("m2m=" + libelles)
'''


def test_orm_one_to_many_and_many_to_many(tmp_path):
    db = str(tmp_path / "c.db").replace("\\", "/")
    out = _run_okp(PROG_COLL.format(db=db), tmp_path)
    assert "o2m=3" in out, out               # @OneToMany : 3 articles de l'auteur
    assert "m2m=news,tech," in out, out      # @ManyToMany via table de jointure


PROG_QM = '''use "oktopios_orm/orm.okp"

@Entity("users")
class User {{
    @Id var id: int
    @Column("nom") var nom: string
    @Column("age") var age: int
}}

var db = "{db}"

var mig = new Migrator(db)
var migrations = [
    {{ "nom": "001_users", "sql": "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, nom TEXT, age INTEGER)" }},
    {{ "nom": "002_ville", "sql": "ALTER TABLE users ADD COLUMN ville TEXT" }}
]
print("mig1=" + mig.migrer(migrations))
print("mig2=" + mig.migrer(migrations))

var repo = new Repo(db, new User())
var noms = ["Awa", "Ben", "Cid", "Dot"]
var ages = [25, 30, 15, 65]
var i = 0
for (nom in noms) {{
    var u = new User()
    u.nom = nom
    u.age = ages[i]
    repo.save(u)
    i = i + 1
}}

var ents = repo.hydrateRows(repo.query().where("age", ">", 18).orderBy("age", "ASC").get())
var ordre = ""
for (u in ents) {{ ordre = ordre + u.nom + "," }}
print("where=" + ordre)
print("in=" + repo.query().whereIn("nom", ["Awa", "Ben"]).count())
var prem = repo.query().like("nom", "A%").first()
print("like=" + prem["nom"])
print("or=" + repo.query().where("age", "<", 18).orWhere("age", ">", 60).count())
'''


def test_orm_migrator_and_rich_query(tmp_path):
    db = str(tmp_path / "qm.db").replace("\\", "/")
    out = _run_okp(PROG_QM.format(db=db), tmp_path)
    assert "mig1=2" in out, out                   # 2 migrations appliquées
    assert "mig2=0" in out, out                   # idempotent (rien de nouveau)
    assert "where=Awa,Ben,Dot," in out, out       # where + orderBy ASC
    assert "in=2" in out, out                     # whereIn
    assert "like=Awa" in out, out                 # like + first
    assert "or=2" in out, out                     # orWhere


PROG_CASCADE = '''use "oktopios_orm/orm.okp"

@Entity("auteurs")
class Auteur {{
    @Id var id: int
    @Column("nom") var nom: string
    @OneToMany("Article") var articles: any
}}
@Entity("articles")
class Article {{
    @Id var id: int
    @Column("titre") var titre: string
    @ManyToOne("Auteur") var auteur: any
}}

var db = "{db}"
var schema = new Schema()
schema.migrate(db, new Auteur())
schema.migrate(db, new Article())

var exA = new Auteur()
print("fk=" + schema.o2mFk(exA, "articles"))

var repoAut = new Repo(db, new Auteur())
var a = new Auteur()
a.nom = "Awa"
var t1 = new Article()
t1.titre = "T1"
var t2 = new Article()
t2.titre = "T2"
a.articles = [t1, t2]
repoAut.saveCascade(a)

var charge = repoAut.find(a.id)
var c = 0
for (x in charge.articles) {{ c = c + 1 }}
print("cascade=" + c)

var lazy = repoAut.findLazy(a.id)
if (lazy.articles == null) {{ print("lazy=null") }}
'''


def test_orm_cascade_inferred_fk_and_lazy(tmp_path):
    db = str(tmp_path / "cs.db").replace("\\", "/")
    out = _run_okp(PROG_CASCADE.format(db=db), tmp_path)
    assert "fk=auteur_id" in out, out        # FK @OneToMany inférée (inverse auto)
    assert "cascade=2" in out, out           # saveCascade a enregistré les 2 enfants
    assert "lazy=null" in out, out           # findLazy ne charge pas les relations


PROG_ROLLBACK = '''use "oktopios_orm/orm.okp"
inject DataImport

var db = "{db}"
var mig = new Migrator(db)
var migrations = [
    {{ "nom": "001_t", "sql": "CREATE TABLE t (id INTEGER PRIMARY KEY)", "down": "DROP TABLE t" }},
    {{ "nom": "002_u", "sql": "CREATE TABLE u (id INTEGER PRIMARY KEY)", "down": "DROP TABLE u" }}
]
print("mig=" + mig.migrer(migrations))
print("last=" + mig.rollbackLast())
print("etat=" + mig.appliquees())
var ex = DataImport.execSQL(db, "SELECT name FROM sqlite_master WHERE type='table' AND name='u'", [])
var n = 0
for (r in ex) {{ n = n + 1 }}
print("u=" + n)
'''


def test_orm_migration_rollback(tmp_path):
    db = str(tmp_path / "rb.db").replace("\\", "/")
    out = _run_okp(PROG_ROLLBACK.format(db=db), tmp_path)
    assert "mig=2" in out, out
    assert "last=002_u" in out, out          # rollbackLast renvoie la dernière
    assert "etat=['001_t']" in out, out      # 002 retirée du suivi
    assert "u=0" in out, out                 # table u supprimée par le `down`
