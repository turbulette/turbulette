# Turbulette

![test](https://github.com/python-turbulette/turbulette/workflows/test/badge.svg)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/e244bb031e044079af419dabd40bb7fc)](https://www.codacy.com/gh/python-turbulette/turbulette/dashboard?utm_source=github.com&utm_medium=referral&utm_content=python-turbulette/turbulette&utm_campaign=Badge_Coverage)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e244bb031e044079af419dabd40bb7fc)](https://www.codacy.com/gh/python-turbulette/turbulette/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=python-turbulette/turbulette&amp;utm_campaign=Badge_Grade)
![PyPI](https://img.shields.io/pypi/v/turbulette)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/turbulette)
![PyPI - License](https://img.shields.io/pypi/l/turbulette)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Generic badge](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Generic badge](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

<p align="center">Turbulette packages all you need to build great GraphQL APIs :</p>

<p align="center"><strong><em>ASGI framework, GraphQL library, ORM and data validation</em></strong></p>

---

Documentation : [https://python-turbulette.github.io/turbulette/](https://python-turbulette.github.io/turbulette/)

---

Features :

- Split your API in small, independent applications
- Generate Pydantic models from GraphQL types
- JWT authentication with refresh and fresh tokens
- Powerful and extendable policy-based access control (PBAC)
- Extendable auth user model with role management
- Async caching (provided by async-caches)
- Built-in CLI to manage project, apps, and DB migrations
- Built-in pytest plugin to quickly test your resolvers
- Settings management at project and app-level (thanks to simple-settings)
- CSRF middleware
- 100% test coverage
- 100% typed, your IDE will thank you ;)
- Handcrafted with ❤️, from 🇫🇷

## Requirements

Python 3.6+

👍 Turbulette makes use of great tools/frameworks and wouldn't exist without them :

- [Ariadne](https://ariadnegraphql.org/) - Schema-first GraphQL library
- [Starlette](https://www.starlette.io/) - The little ASGI framework that shines
- [GINO](https://python-gino.org/docs/en/master/index.html) - Lightweight, async ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Powerful data validation with type annotations
- [Alembic](https://alembic.sqlalchemy.org/en/latest/index.html) - Lightweight database migration tool
- [simple-settings](https://github.com/drgarcia1986/simple-settings) - A generic settings system inspired by Django's one
- [async-caches](https://github.com/rafalp/async-caches) - Async caching library
- [Click](https://palletsprojects.com/p/click/) - A "Command Line Interface Creation Kit"

## Installation

``` bash
pip install turbulette
```

You will also need an ASGI server, such as [uvicorn](https://www.uvicorn.org/) :

``` bash
pip install uvicorn
```

----

## 🚀  5 min Quick Start

Here is a short example that demonstrates a minimal project setup.

We will see how to scaffold a simple Turbulette project, create a Turbulette application, and write some GraphQL schema/resolver. It's advisable to start the project in a virtualenv to isolate your dependencies.
Here we will be using [poetry](https://python-poetry.org/) :

``` bash
poetry init
```

Then, install Turbulette from PyPI :

``` bash
poetry add turbulette
```

### 1: Create a project

First, create a `hello_world/` directory that will contain the whole project.

Now, inside this folder, create your Turbulette project using the `turb` CLI :

``` bash
turb project my-project
```

You should get with something like this :

```console
.
└── 📁 my-project
    ├── 📁 alembic
    │   ├── 📄 env.py
    │   └── 📄 script.py.mako
    ├── 📄 .env
    ├── 📄 alembic.ini
    ├── 📄 app.py
    └── 📄 settings.py
```

Let's break down the structure :

- `📁 my-project` : Here is the so-called *Turbulette project* folder, it will contain applications and project-level configuration files
- `📁 alembic` : Contains the [Alembic](https://alembic.sqlalchemy.org/en/latest/) scripts used when generating/applying DB migrations
  - `📄 env.py`
  - `📄 script.py.mako`
- `📄 .env` : The actual project settings live here
- `📄 app.py` : Your API entrypoint, it contains the ASGI app
- `📄 settings.py` : Will load settings from `.env` file


Why have both `.env` and `settings.py`?


You don't *have to*. You can also put all your settings in `settings.py`.
But Turbulette encourage you to follow the [twelve-factor methodology](https://12factor.net),
that recommend to separate settings from code because config varies substantially across deploys, *code does not*.
This way, you can untrack `.env` from version control and only keep tracking `settings.py`, which will load settings
from `.env` using Starlette's `Config` object.

### 2: Create the first app

Now it's time to create a Turbulette application!

Run this command under the project directory (`my-project`) :

```bash
turb app --name hello-world
```

!!! info
    You need to run `turb app` under the project dir because the CLI needs to access the `almebic.ini` file to create the initial database migration.

You should see your new app under the project folder :

```console
.
└── 📁 my-project
    ...
    |
    └── 📁 hello-world
        ├── 📁 graphql
        ├── 📁 migrations
        │   └── 📄 20200926_1508_auto_ef7704f9741f_initial.py
        ├── 📁 resolvers
        └── 📄 models.py
```

Details :

- `📁 graphql` : All the GraphQL schema will live here
- `📁 migrations` : Will contain database migrations generated by Alembic
- `📁 resolvers` : Python package where you will write resolvers binded to the schema
- `📄 models.py` : Will hold GINO models for this app

### 3: GraphQL schema

Now that we have our project scaffold, we can start writing actual schema/code.

Create a `schema.gql` file in the `📁 graphql` folder and add this base schema :

``` graphql
extend type Query {
    user: [User]
}

type User {
    id: ID!
    username: String!
    gender: String!
    isStaff: Boolean!
}
```

!!! info
    Note that we *extend* the type `Query` because Turbulette already defines it. The same goes for `Mutation` type

### 4: Add a resolver

The last missing piece is the resolver for our `user` query, to make the API returning something when querying for it.

As you may have guessed, we will create a new Python module in our `📁 resolvers` package. Let's call it `user.py` :

``` python
from turbulette import query


@query.field("user")
async def user(obj, info, **kwargs):
    return [
        {"id": 1, "username": "Gustave Eiffel", "gender": "male", "is_staff": False},
        {"id": 2, "username": "Marie Curie", "gender": "female", "is_staff": True},
    ]

```

### 5: Run it

Our `user` query is now binded to the schema, so let's test it.

Start the server :

```bash
poetry run uvicorn app:app --port 8000
```

Now, go to [http://localhost:8000/graphql](http://localhost:8000/graphql), you will see the [GraphQL Playground](https://github.com/graphql/graphql-playground) IDE.
Finally, run the user query, for example :

``` graphql
query {
  user {
    id
    username
    gender
    isStaff
  }
}
```

Should give you the following expected result :

``` json
{
  "data": {
    "user": [
      {
        "id": "1",
        "username": "Gustave Eiffel",
        "gender": "male",
        "isStaff": false
      },
      {
        "id": "2",
        "username": "Marie Curie",
        "gender": "female",
        "isStaff": true
      }
    ]
  }
}
```

Good job! That was a straightforward example, showing off the bare minimum needed to set up a Turbulette API. To get the most of it, follow the User Guide.

*[ASGI]: Asynchronous Server Gateway Interface
