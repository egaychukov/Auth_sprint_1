desc = {
    'films': {
        'search_films': 'Conducts a full-text search of films by their title and description',
        'get_film_details': 'Fetches a film by its id',
        'get_film_list': 'Extracts a list of films. Optionally, films can be sorted by rating or name. Furthermore, films can be filtered by a genre'
    },
    'genres': {
        'get_genre_by_id': 'Fetches a genre by its id',
        'get_genres': 'Extracts a list of genres'
    },
    'persons': {
        'search_persons': 'Conducts a full-text search of people by their full names',
        'get_person_films': 'Gets films of the person specified by their id',
        'get_person_by_id': 'Fetches a person by their id'
    }
}

app_desc = '''
The movies API enables fetching all main entities by their ids. Some endpoints leverage **full-text** search, while others use **exact** matches.<br>
The API consists of three endpoint groups:
- films
- genres
- persons
'''