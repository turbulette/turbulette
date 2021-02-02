# Introduction

The quick start demonstrates a quick and simple Turbulette API setup, without any database involved.  Almost too easy.

The purpose of this user guide is to show you how to structure a Turbulette project and make use of the different libraries included to build efficient and beautiful GraphQL APIs ❤️.

## What's in the box?

That being said, which tools are actually included in Turbulette and what are they used for?

In order to build a fully-featured GraphQL API, one would probably need the following:

- An ASGI framework

- Library to bind GraphQL schema to resolvers

- Validate some input data

- Make queries to a database

- Deals with changes in the database schema (database migrations)

The good news is that Turbulette covers you for each of these prerequisites:

|                    |                                                      |
| :------------------: | :----------------------------------------------------: |
| ASGI framework     | [Starlette](https://www.starlette.io/)               |
| GraphQL library    | [Ariadne](https://ariadnegraphql.org/)               |
| Data validation    | [Pydantic](https://pydantic-docs.helpmanual.io/)     |
| ORM                | [GINO](https://python-gino.org/docs/en/1.0/)         |
| Database migration | [Alembic](https://alembic.sqlalchemy.org/en/latest/) |

Well, there is something even better: all of this works in an *asynchronous* fashion.

Asynchronous programming is a type of parallel programming, that is, a way to do multiple tasks *at the same time*. For example, an asynchronous server can start another task when the current one is waiting to complete (ex: when a db query is being processed).

This is a good thing because most of the time, web APIs are concerned with I/O operations (waiting for a database query to finish, writing files on the disk, call another microservice, etc). Having a fully async API makes it more efficient as it takes advantage of that waiting time to start/continue/end other tasks.

Libraries included in Turbulette have been chosen because they are lightweight, fast, and asynchronous context can be kept in the whole stack.

All Turbulette does, is to make these tools working seamlessly together as if you were using a big framework. There is no abstraction on top of them (just some *glue* in between), so once you get use to them, you are good to go.
