# TODO CRUD
This project is a authenticated and authorized Todo CRUD(create, read, update, and delete) backend, which means that a user is required to login before accessing main CRUD operations and one user cannot interrupt or see the tasks of other user. Developed with the help of FastAPI(Backend Framework for python), Supabase for Auth, PostgreSQL for data storage, SQLModel for ORM and Docker to containerize the stack.

## Setup:
Since this backend is setup using docker, so we will use docker and eliminate "It works on my pc" error for good.

1. After cloning using `git clone`, open project directory by `cd Todo-CRUD`.
2. Create a .env file by using .env.example and replace the generic secrets to your own choice.
3. After setting up secrets, use `docker compose up` to start your containers.
4. Open browser or curl localhost:8000


## Endpoints: 

| Method | Endpoint | Purpose |
| :--- | :---  | :--- |
| **Get** | "/" | Root endpoint to provide information on versions and available endpoints |
| **GET** | "/health" | Returns the status of server |
| **GET** | "/tasks" | Fetches All tasks with filters. |
| **GET** | "/tasks/{id}" | Fetches a specific tasks with provided ID. |
| **POST** | "/tasks" | Creates a new task. |
| **PUT** | "/tasks/{id}" | Updates the whole body of the provided ID task. |
| **PATCH** | "/tasks/{id}" | Updates either one or all attributes of task body |
| **DELETE** | "/tasks/{id}" | Deltes the task with provided ID. |
| **GET** | "/tasks/stats" | Compute the statistics of tasks in tasks list. |
| **POST** | "/auth/signup" | Registers User in db |
| **POST** | "/auth/login" | Registers Session for user in db and returns an access token |
| **POST** | "/auth/logout" | Removes  |

Checkout Swagger UI on `http://localhost:8000/docs` for more details about endpoints.

---
### Swagger Screenshot:

![Swagger UI Screenshot](./swagger_screenshot.png)

---
### CURL Command Output:
Here is curl command for health:
```
curl -i http://localhost:8000/health
```

and here is its output if running:
`{"status":"ok"}`

---
### Database:
For saving the tasks, this CRUD backend uses PostgreSQL inside a container using official PostgreSQL 18+ image which saves its data inside a volume so that data is not lost when we do `docker compose down`.

#### DB Container Screenshot of Data:

![DB Viewer Database Screenshot](./pg-container-screenshot.png)

---
