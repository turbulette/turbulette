query_get_jwt = """
    query getJWT($username: String! $password: String!) {
        getJWT(username: $username, password: $password){
            accessToken
            refreshToken
            errors
        }
    }
"""

query_books = """
        query books {
            books {
                books {
                    title
                }
                errors
            }
        }
"""

query_book = """
    query book($id: ID!) {
        book(id: $id) {
            book {
                title
                author
                publicationDate
                profile {
                    genre
                    awards
                }
            }
        }
    }
"""

query_borrowings = """
    query book($id: ID!) {
        book(id: $id) {
            book {
                borrowings
            }
        }
    }
"""

query_exclusive_books = """
    query exclusiveBooks {
        exclusiveBooks {
            books {
                title
                author
            }
            errors
        }
    }
"""

query_refresh_jwt = """
    query refreshJWT {
        refreshJWT{
            accessToken
            errors
        }
    }
"""

mutation_create_user = """
    mutation createUser(
        $username: String!
        $firstName: String!
        $lastName: String!
        $email:  String!
        $passwordOne: String!
        $passwordTwo: String!
    ) {
        createUser(input: {
            username: $username
            firstName: $firstName
            lastName: $lastName
            email: $email
            passwordOne: $passwordOne
            passwordTwo: $passwordTwo
        }) {
            user {
                id
                username
                firstName
                lastName
                email
            }
            token
            errors
        }
    }
"""

mutation_borrow_book = """
    mutation borrowBook(
        $id: ID!
    ) {
        borrowBook(
            id: $id
        ) {
            success
            errors
        }
    }
"""

mutation_add_book = """
    mutation addBook {
        addBook {
            success
            errors
        }
    }
"""

mutation_create_book = """
    mutation createBook(
        $title: String!
        $author: String!
        $publicationDate: DateTime!
        $profile: JSON
    ) {
        createBook(
            input: {
                title: $title
                author: $author
                publicationDate: $publicationDate
                profile: $profile
            }
        ) {
            book {
                id
                title
                author
                publicationDate
                profile {
                    genre
                    awards
                }
            }
        }
    }
"""


mutation_update_password = """
    mutation updatePassword(
        $password: String!
    ) {
        updatePassword(
            password: $password
        ) {
            success
            errors
        }
    }
"""

mutation_create_comic = """
    mutation createComic(
        $title: String!
        $author: String!
        $artist: String!
        $publicationDate: DateTime!
        $profile: JSON
    ) {
        createComic(
            input: {
                title: $title
                author: $author
                artist: $artist
                publicationDate: $publicationDate
                profile: $profile
            }
        ) {
            comic {
                id
                title
                author
                artist
                publicationDate
                profile {
                    genre
                    awards
                }
            }
        }
    }
"""

mutation_borrow_unlimited = """
    mutation borrowUnlimitedBooks {
        borrowUnlimitedBooks {
            success
            errors
        }
    }
"""

mutation_destroy_library = """
mutation destroyLibrary {
    destroyLibrary {
        success
    }
}
"""
