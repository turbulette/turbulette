import logging
from ariadne import convert_kwargs_to_snake_case
from turbulette import mutation, query
from turbulette.apps.auth import user_model, get_token_from_user
from turbulette.apps.auth.pyd_models import BaseUserCreate
from turbulette.core.errors import ErrorField
from turbulette.core.validation.decorators import validate
from ..models import Book, Comics
from ..pyd_models import CreateBook, CreateComics


@mutation.field("createUser")
@convert_kwargs_to_snake_case
@validate(BaseUserCreate)
async def resolve_user_create(obj, info, valid_input, **kwargs) -> dict:
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
    auth_token = get_token_from_user(new_user)
    return {
        "user": {**new_user.to_dict()},
        "token": auth_token,
    }


@query.field("books")
async def resolve_books(_, info, user, **kwargs):
    return {
        "books": [
            {"title": "Harry Potter", "author": "J.K Rowling"},
            {"title": "The Lord of the Rings", "author": "J.R.R Tolkien"},
        ]
    }


@mutation.field("addBook")
async def add_books(_, __, user, **kwargs):
    return {"success": True}


@mutation.field("borrowBook")
async def borrow_book(_, __, user, **kwargs):
    return {"success": True}


@query.field("exclusiveBooks")
async def is_logged(_, __, claims, **kwargs):
    return {
        "books": [
            {"title": "Game Of Thrones", "author": "G.R.R Martin"},
        ]
    }


@query.field("book")
async def book(_, __, id):
    book = await Book.query.where(Book.id == int(id)).gino.first()
    return {"book": book.to_dict()}


@mutation.field("createBook")
@convert_kwargs_to_snake_case
@validate(CreateBook)
async def create_book(_, __, valid_input, **kwargs):
    book = await Book.create(**valid_input)
    return {"book": book.to_dict()}


@mutation.field("updatePassword")
async def change_password(_, __, claims, **kwargs):
    return {"success": True}


@mutation.field("createComic")
@convert_kwargs_to_snake_case
@validate(models=[CreateBook, CreateComics])
async def create_cartoon(_, __, valid_input, **kwargs):
    """Validate input data against multiple models.
    This can be useful to add entries in multiple tables linked
    with a foreign key
    """
    book_input, comics_input = valid_input[0], valid_input[1]
    book = await Book.create(**book_input)
    comic = await Comics.create(**comics_input, book=book.id)
    return {"comic": {**book.to_dict(), **comic.to_dict()}}
