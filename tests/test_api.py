import io

def test_signup_login(client):
    signupresponse = client.post(
        "/auth/signup", 
        json={"email": "test@email.com", "username": "testuser", "password": "testpass", "confirm_password": "testpass"}
        )
    assert signupresponse.status_code == 201
    assert signupresponse.json()["email"] == "test@email.com"
    assert signupresponse.json()["username"] == "testuser"
    loginresponse = client.post("/auth/login", 
        data={"email": "test@email.com", "username": "testuser", "password": "testpass"}
        )
    assert loginresponse.status_code == 200
    assert "access_token" in loginresponse.json()

def test_task_data_isolation(client):
    '''Verify that User B cannot see or manipulate User A's tasks. Ensure isolation of tasks.'''

    client.post("/auth/signup", json={"email": "testA@email.com", "username": "testuserA", "password": "testpwdA", "confirm_password": "testpwdA"})
    response_a = client.post("/auth/login", data={"email": "testA@email.com", "username": "testuserA", "password": "testpwdA"})
    assert response_a.status_code == 200, f"Login failed: {response_a.json()}"
    token_a = response_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    client.post("/auth/signup", json={"email": "testB@email.com", "username": "testuserB", "password": "testpwdB", "confirm_password": "testpwdB"})
    response_b = client.post("/auth/login", data={"email": "testB@email.com", "username": "testuserB", "password": "testpwdB"})
    assert response_b.status_code == 200, f"Login failed: {response_a.json()}"
    token_b = response_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    task_response = client.post("/tasks", json={"title": "Test Task", "description": "Test Description"}, headers=headers_a)
    assert task_response.status_code == 201
    task_id = task_response.json()["id"]

    get_response = client.get("/tasks/", headers=headers_b)
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

    delete_response = client.delete(f"/tasks/{task_id}", headers=headers_b)
    assert delete_response.status_code == 403 or 404

def test_file_upload_restrictions(client):
    '''Ensure invalid file formats are rejected by the file checker.'''

    client.post("/auth/signup", json={"email": "filetest@email.com", "username": "files", "password": "filespwd", "confirm_password": "filespwd"})
    response = client.post("/auth/login", data={"email": "filetest@email.com", "username": "files", "password": "filespwd"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_response = client.post("/tasks", json={"title": "File Task", "description": "File Description/Audio Jungle"}, headers=headers)
    assert task_response.status_code == 201, f"Task creation failed: {task_response.json()}"

    task_id = task_response.json()["id"]

    bad_file = {"file": ("test.txt", io.BytesIO(b"test file"), "text/plain")}

    upload_response = client.post(
        f"/tasks/{task_id}/upload", 
        files=bad_file, 
        headers=headers
    )

    print("API RESPONSE STATUS:", upload_response.status_code)
    print("API RESPONSE BODY:", upload_response.text)

    assert upload_response.status_code == 400, f"Expected 400 but got {upload_response.status_code}. Response message: {upload_response.text}"
    assert "Invalid file type" in upload_response.json()["detail"]