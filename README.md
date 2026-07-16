# TODO CRUD
It is a todo CRUD(create, read, update, and delete) backend, which is developed with the help of FastAPI(Backend Framework for python). For simplicity and learning phase of a framework it utilizes python list which is in memory and disappears when program ended.

## Setup:
Since this assignment was setup with the help of **uv** so we rely on uv package manager.

1. After cloning using `git clone`, open project directory by `cd Todo-CRUD`.
2. To install dependencies in order to run the backend, Use `uv sync`.
3. Start the server, by `uv run fastapi dev` command.


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
| **POST** | "/tasks/reset" | Resets the task list into its original state with 3 testing tasks. |
| **GET** | "/tasks/stats" | Compute the statistics of tasks in tasks list. |

Checkout Swagger UI on `http://localhost:8000/docs` for more details about endpoints.

---

### Mortality Experiment
When I created some tasks, updated them and even deleted some. The get api was showing me all changes but as soon as I restart the server, all changes were gone. It happened because my changes were saving in RAM in the form of list in my pyhton program. To store it permanently so that I can access it even after program ends, I have to store it in my disk drive in the form of file. 
