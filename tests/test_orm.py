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
