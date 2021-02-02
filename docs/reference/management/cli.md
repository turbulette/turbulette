Turbulette has a built-in CLI that helps you to create projects/apps,
manage alembic revisions and can generates JSON Web Keys (JWK), to use as a `SECRET_KEY`.

## `project`

Creates a Turbulette project with the following default structure :

```console
.
└── 📁 project_name
    ├── 📁 alembic
    │   ├── 📄 env.py
    │   └── 📄 script.py.mako
    ├── 📄 .env
    ├── 📄 alembic.ini
    ├── 📄 app.py
    └── 📄 settings.py
```

## `app`

Creates a Turbulette application with the following default structure :

```console
.
└── 📁 project_name
    ...
    |
    └── 📁 app_name
        ├── 📁 graphql
        ├── 📁 migrations
        │   └── 📄 20200926_1508_auto_ef7704f9741f_initial.py
        ├── 📁 resolvers
        └── 📄 models.py
```

The command also creates a dedicated
[alembic branch](https://alembic.sqlalchemy.org/en/latest/branches.html) for the app, this allows
to generate/apply revisions for a *specific* Turbulette app. This is precisely what does the initial
migration:

```python
# 20200926_1508_auto_ef7704f9741f_initial.py

"""create app_name branch

Revision ID: 69604d4ceebf
Revises:
Create Date: 2020-09-26 15:08:06.530681

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "69604d4ceebf"
down_revision = None
branch_labels = ("app_name",)
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
```

This revision will result in a new table called `alembic_version`, that will store ids of the different alembic branches
corresponding to your Turbulette applications.


## `autogenerate`

Auto-generates alembic revisions. This is basically a shortcut to :
`alembic revision --autogenerate --head=<app>@head` that generate a revision
for the `app` branch.

## `upgrade`

Applies alembic revisions. If an app name is given, upgrade to the latest
revision for this app only. If no app is given, upgrade to the latest
revision for all apps in the current project

## `jwk`

Generates a [JSON Web Key](https://tools.ietf.org/html/rfc7517)
to put in your settings module or `.env` file.
