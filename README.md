# FlaskArticlesApp
FlaskArticlesApp is a simple user project to add articles to CRUD and MySQL tables with Python Flask framework

## Database schemas
### articles Table

| Column name  | Data Type     | Explanation           |
|--------------|---------------|-----------------------|
| id           | INT           | article ID            |
| title        | TEXT          | article title         |
| author       | TEXT          | article writer        |
| content      | TEXT          | article content       |
| created_date | TIMESTAMP     | article creation date |

### users Table

| Column name  | Data Type     | Explanation           |
|--------------|---------------|-----------------------|
| id           | INT           | user ID               |
| name         | TEXT          | user name             |
| email        | TEXT          | user email            |
| username     | TEXT          | person username       |
| password     | TEXT          | user password         |

### comments Table

| Column name   | Data Type     | Explanation                  |
|---------------|---------------|------------------------------|
| id            | INT           | comment ID                   |
| user          | TEXT          | User ID who made the comment |
| article_id    | INT           | commented article id         |
| comment       | TEXT          | comment content              |
| comment_title | TEXT          | comment title                |
| comment_date  | TIMESTAMP     | comment date                 |


