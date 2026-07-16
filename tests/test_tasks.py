import unittest

from fastapi.testclient import TestClient

import main


class TaskApiTests(unittest.TestCase):
    def setUp(self) -> None:
        main.tasks.clear()
        main.tasks.extend([
            main.Task(id=1, title="Task 1", done=False),
            main.Task(id=2, title="Task 2", done=True),
        ])
        main.task_id_count = 2

    def test_create_task_assigns_next_id(self) -> None:
        client = TestClient(main.app)

        response = client.post("/tasks", json={"title": "New Task", "done": False})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["id"], 3)
        self.assertEqual(len(main.tasks), 3)


if __name__ == "__main__":
    unittest.main()
