import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException, Request, Response

import app


class TeacherAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.credentials_path = Path(self.temporary_directory.name) / "teachers.json"
        self.credentials_path.write_text(
            json.dumps({"teacher": app.hash_password("correct-horse-battery")}),
            encoding="utf-8",
        )
        self.file_patch = patch.object(app, "TEACHERS_FILE", self.credentials_path)
        self.secret_patch = patch.object(app, "SESSION_SECRET_BYTES", b"test-session-secret")
        self.file_patch.start()
        self.secret_patch.start()
        self.original_participants = list(app.activities["Chess Club"]["participants"])

    def tearDown(self):
        app.activities["Chess Club"]["participants"] = self.original_participants
        self.file_patch.stop()
        self.secret_patch.stop()
        self.temporary_directory.cleanup()

    def make_request(self, cookie=None):
        headers = []
        if cookie:
            headers.append((b"cookie", cookie.encode("ascii")))
        return Request(
            {
                "type": "http",
                "http_version": "1.1",
                "method": "GET",
                "scheme": "http",
                "path": "/",
                "query_string": b"",
                "headers": headers,
                "server": ("testserver", 80),
                "client": ("testclient", 50000),
            }
        )

    def test_guest_can_view_activities_but_cannot_change_enrollments(self):
        self.assertIn("Chess Club", app.get_activities())
        with self.assertRaises(HTTPException) as error:
            app.signup_for_activity("Chess Club", "new@mergington.edu", self.make_request())
        self.assertEqual(error.exception.status_code, 401)

        with self.assertRaises(HTTPException) as error:
            app.unregister_from_activity(
                "Chess Club", self.original_participants[0], self.make_request()
            )
        self.assertEqual(error.exception.status_code, 401)

    def test_teacher_login_allows_signup_and_unregister(self):
        response = Response()
        result = app.login(app.LoginRequest(username="teacher", password="correct-horse-battery"), response)
        cookie = response.headers["set-cookie"].split(";", 1)[0]
        request = self.make_request(cookie)

        self.assertEqual(result["username"], "teacher")
        self.assertTrue(app.get_session(request)["authenticated"])
        self.assertIn("new@mergington.edu", app.signup_for_activity(
            "Chess Club", "new@mergington.edu", request
        )["message"])
        self.assertIn("Unregistered", app.unregister_from_activity(
            "Chess Club", "new@mergington.edu", request
        )["message"])

    def test_invalid_credentials_are_rejected(self):
        with self.assertRaises(HTTPException) as error:
            app.login(
                app.LoginRequest(username="teacher", password="wrong-password"),
                Response(),
            )
        self.assertEqual(error.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()