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
                    author
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

mutation_borrow_books = """
    mutation borrowBook {
        borrowBook {
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
        $username: String!
        $password: String!
    ) {
        updatePassword(
            username: $username
            password: $password
        ) {
            success
            errors
        }
    }
"""
