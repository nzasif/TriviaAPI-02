# API DOCUMENTATION FOR TRIVIA API


`GET '/api/v1.0/categories'`
> get request
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

```json
{
  "1": "Science",
  "2": "Art",
  "3": "Geography",
  "4": "History",
  "5": "Entertainment",
  "6": "Sports"
}
```

`GET '/categories'`

- Fetches a dictionary of categories in which the keys are the ids and the value is the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains an object of id: category_string key:value pairs.

```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

---

`GET '/questions?page=${integer}'`

- Get a paginated set of questions, total number of questions, all categories and current category string.
- Request Arguments: `page` - integer
- Returns: An object with 10 paginated questions

```json
{
  "questions": [
    {
      "id": 1,
      "question": "PNS stands for ___ ?",
      "answer": "perepheral nerve system",
      "difficulty": 3,
      "category": 1
    }
  ],
  "totalQuestions": 100,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "currentCategory": "Science"
}
```

---

`GET '/categories/${id}/questions'`

- Fetches questions for a cateogry specified by id request argument
- Request Arguments: `id` - integer
- Returns: An object with questions for the specified category, total questions, and current category string

```json
{
  "questions": [
    {
      "id": 1,
      "question": "This is my question",
      "answer": "This is the answer of my question",
      "difficulty": 5,
      "category": 4
    }
  ],
  "totalQuestions": 100,
  "currentCategory": "History"
}
```

---

`DELETE '/questions/${id}'`

- Deletes a specified question using the id of the question
- Request Arguments: `id` - integer
- Returns: Does not need to return anything besides the appropriate HTTP status code.
---

`POST '/quizzes'`

- Sends a post request in order to get the next question
- Request Body:

```json
{
    "previous_questions": "[1, 4, 20, 15]",
    "quiz_category": "current category"
 }
```

- Returns: a single new question object

```json
{
  "question": {
    "id": 1,
    "question": "This is a question",
    "answer": "This is an answer",
    "difficulty": 5,
    "category": 4
  }
}
```

---

`POST '/questions'`

- Sends a post request for adding new question
- Request Body:

```json
{
  "question": "Heres a new question string",
  "answer": "Here is a new answer string",
  "difficulty": 1,
  "category": 3
}
```

- Returns: return updated questions

---

`POST '/search'`

- Sends a post request in order to search for a specific question by search term
- Request Body:

```json
{
  "searchTerm": "this is a search term"
}
```

- Returns: any array of questions, a number of totalQuestions that met the search term and the current category string

```json
{
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "difficulty": 5,
      "category": 5
    }
  ],
  "totalQuestions": 100,
  "currentCategory": "Entertainment"
}
```