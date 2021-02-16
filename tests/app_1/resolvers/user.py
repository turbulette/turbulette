"""GraphQL resolvers for user operations."""

import logging

from ariadne import convert_kwargs_to_snake_case

from tests.app_1.models import Book, Comics
from tests.app_1.pyd_models import CreateBook, CreateComics
from turbulette import mutation, query
from turbulette.apps.auth import get_token_from_user, user_model
from turbulette.apps.auth.pyd_models import BaseUserCreate
from turbulette.errors import ErrorField
from turbulette.validation.decorators import validate


@mutation.field("createUser")
@convert_kwargs_to_snake_case
@validate(BaseUserCreate)
async def resolve_user_create(*_, **kwargs) -> dict:
    valid_input = kwargs["valid_input"]
    user = await user_model.query.where(
        user_model.username == valid_input["username"]
    ).gino.first()

    if user:
        message = f"User {valid_input['username']} already exists"

        # Make sure to call __str__ on BaseError
        out = str(ErrorField(message))
        logging.info(out)

        return ErrorField(message).dict()

    new_user = await user_model.create(**valid_input)
    auth_token = await get_token_from_user(new_user)
    return {
        "user": {**new_user.to_dict()},
        "token": auth_token,
    }


@query.field("books")
async def resolve_books(*_, **kwargs):
    return {
        "books": [
            {
                "title": "Harry Potter",
                "author": "J.K Rowling",
                "borrowings": 1345,
                "price_bought": 15.5,
            },
            {
                "title": "The Lord of the Rings",
                "author": "J.R.R Tolkien",
                "borrowings": 2145,
                "price_bought": 23.89,
            },
        ]
    }


@mutation.field("addBook")
async def add_books(*_, **kwargs):
    return {"success": True}


@mutation.field("borrowBook")
async def borrow_book(*_, **kwargs):
    book = await Book.get(int(kwargs["id"]))
    await book.update(borrowings=book.borrowings + 1).apply()
    return {"success": True}


@query.field("exclusiveBooks")
async def is_logged(*_, **kwargs):
    return {
        "books": [
            {"title": "Game Of Thrones", "author": "G.R.R Martin"},
        ]
    }


@query.field("book")
async def resolve_book(*_, **kwargs):
    book = await Book.query.where(Book.id == int(kwargs["id"])).gino.first()
    return {"book": book.to_dict()}


@mutation.field("createBook")
@convert_kwargs_to_snake_case
@validate(CreateBook)
async def create_book(*_, **kwargs):
    book = await Book.create(**kwargs["valid_input"])
    return {"book": book.to_dict()}


@mutation.field("updatePassword")
async def update_password(*_, **kwargs):
    await user_model.set_password(kwargs["claims"]["sub"], kwargs["password"])
    return {"success": True}


@mutation.field("createComic")
@convert_kwargs_to_snake_case
@validate(CreateComics)
async def create_cartoon(*_, **kwargs):
    """Validate input data against multiple models.
    This can be useful to add entries in multiple tables linked
    with a foreign key
    """
    valid_input = kwargs["valid_input"]
    book_input, comics_input = valid_input.pop("book"), valid_input
    book = await Book.create(**book_input)
    comic = await Comics.create(**comics_input, book=book.id)
    return {"comic": {**book.to_dict(), **comic.to_dict()}}


@mutation.field("borrowUnlimitedBooks")
async def borrow_unlimited(*_):
    return {"success": True}


@mutation.field("destroyLibrary")
async def destroy_library(*_, **kwargs):
    return {"sucess": True}


@query.field("comics")
async def resolve_comics(*_):
    return {
        "comics": [
            {"title": "The Blue Lotus", "author": "Hergé", "artist": "Hergé"},
            {
                "title": "Asterix and Cleopatra",
                "author": "René Goscinny",
                "artist": "Albert Uderzo",
            },
        ]
    }
