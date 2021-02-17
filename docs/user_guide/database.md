## Connect to the database

Connecting with a database in Turbulette is pretty straightforward and just requires to set necessary settings.

!!! info
    As Turbulette use GINO ORM, so it's only compatible with postgres (mysql support [coming soon](https://github.com/python-gino/gino/pull/685))

For local development, an easy way is to start a postgres instance in a docker container:

```console
docker run --name postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```

Once it's running, just ensure that the following settings are correctly set:

```python
DB_DRIVER=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=<mysecretpassword>
DB_DATABASE=<database>
```

If connection settings are correct, GINO will connect with to database when starting the server.

## Models

Models have to be defined in the `models` module of your Turbulette application:

```python
# models.py

from sqlalchemy import Column, Integer
from turbulette.db import Model

class Fruit(Model):
    id = Column(Integer, primary_key=True)
```

Note two things:

- All your models must inherit `Model` class from `#!python turbulette.db`, which is itself a subclass of GINO's `Model`.

- If you already used GINO or SQLAlchemy, you might noticed that we didn't specified the `__tablename__` class attribute to indicates the table name. There is no need to do so because Turbulette automatically generates it using by concatenating the application and model name in camel case.

  If our `Fruit` model would lives in an application named `grocery`, the table would be `grocery_fruit` .

GINO is built on top of SQLAlchemy Core, to see the [Data type](https://docs.sqlalchemy.org/en/13/core/type_basics.html) and [constraints](https://docs.sqlalchemy.org/en/13/core/constraints.html) documentations for more details on how to define your models.

For example, here is the models definitions matching tables from the SQLAlchamy [tutorial](https://docs.sqlalchemy.org/en/14/core/tutorial.html):

```python
# models.py

from sqlalchemy import Column, Integer, String, ForeignKey
from turbulette.db import Model

class User(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)

class Car(Model):
    id = Column(Integer, primary_key=True)
    user = Column(Integer, ForeignKey("grocery_users.id"))
    model = Column(String, nullable=False)
    max_speed = Column(Integer, nullable=False)
```

Look at the user `ForeignKey` in the `Car` model: the reference point to the table name, hence the `grocery_users` (assuming that we are still in the grocery application).

## Migrations

Writing GINO models does not mean that your actual SQL table exist, for that you need to generate a migration, that is, a script that will reflect model changes on the database schema.

Turbulette comes with [Alembic](https://alembic.sqlalchemy.org/en/latest/) integrated, a database migration tools designed to work with SQLAlchemy.  The `turb` CLI wrap some alembic commands to make it easier to generate/apply migrations.

### Branch

Since version 0.7.0, alembic has the concept of branch. Turbulette uses this feature to independently manage different series of migrations (each Turbulette app has its own set of migrations), starting at the root (since the project creation). This allows you to generate or apply per-app migrations, making them *reusable*.

When creating an application with the CLI, you can see that the `📁 migrations` folder is not empty as there is an "initial" revision inside. In fact, this migration contains the creation of the application's alembic branch.

### Auto generating revisions

Alembic is able to find difference between the database schema and models, and can automatically generate a migration to make the schema up-to-date with models:


<div class="termy">
``` console
$ turb makerevision grocery
```
</div>

Again, `makerevision` is just a convenient frontend to alembic, the above is equivalent to:

```console
alembic revision --autogenerate --head=grocery@head
```

### Applying revisions

Once you have generated your revisions, apply them to update the database schema:

<div class="termy">
``` console
$ turb upgrade grocery
```
</div>

Alembic equivalent:

```console
alembic upgrade grocery@head
```

You can also apply revisions from all apps at once by omitting app name:

<div class="termy">
``` console
$ turb upgrade
```
</div>
