
from pathlib import Path
from getpass import getpass

import requests

from encryption import encrypt_file, decrypt_file


SERVER_URL = "http://127.0.0.1:8000"

DOWNLOAD_DIR = Path(__file__).resolve().parent / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

access_token = None
current_username = None


def get_auth_headers():
    return {
        "Authorization": f"Bearer {access_token}"
    }


def show_error(response):
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        detail = response.text

    print(f"Error ({response.status_code}): {detail}")


def register():
    print("\n===== REGISTER =====")

    username = input("Enter username: ").strip()
    password = getpass("Enter password: ")
    confirm_password = getpass("Confirm password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return

    try:
        response = requests.post(
            f"{SERVER_URL}/register",
            json={
                "username": username,
                "password": password
            },
            timeout=15
        )

        if response.status_code == 201:
            print("Registration successful! You can now log in.")
        else:
            show_error(response)

    except requests.RequestException as error:
        print("Registration failed:", error)


def login():
    global access_token, current_username

    print("\n===== LOGIN =====")

    username = input("Enter username: ").strip()
    password = getpass("Enter password: ")

    try:
        response = requests.post(
            f"{SERVER_URL}/login",
            json={
                "username": username,
                "password": password
            },
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()

            access_token = result["access_token"]
            current_username = username

            print(f"\nWelcome, {current_username}!")
            print("Login successful.")

        else:
            show_error(response)

    except (requests.RequestException, ValueError, KeyError) as error:
        print("Login failed:", error)


def logout():
    global access_token, current_username

    access_token = None
    current_username = None

    print("\nLogged out successfully.")


def get_unique_filename(filename):
    original_path = DOWNLOAD_DIR / filename

    if not original_path.exists():
        return original_path

    stem = original_path.stem
    suffix = original_path.suffix

    counter = 1

    while True:
        new_path = DOWNLOAD_DIR / f"{stem}_{counter}{suffix}"

        if not new_path.exists():
            return new_path

        counter += 1


def upload_file():
    file_path = Path(
        input("Enter file path: ").strip()
    ).expanduser()

    if not file_path.is_file():
        print("File not found.")
        return

    try:
        encrypted_data = encrypt_file(file_path)

        response = requests.post(
            f"{SERVER_URL}/upload",
            headers=get_auth_headers(),
            files={
                "file": (
                    file_path.name + ".enc",
                    encrypted_data,
                    "application/octet-stream"
                )
            },
            data={
                "original_name": file_path.name
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()

            print("\nFile encrypted and uploaded successfully!")
            print("File ID:", result["file_id"])
            print("Original filename:", file_path.name)

        else:
            show_error(response)

    except (OSError, ValueError, requests.RequestException) as error:
        print("Upload failed:", error)


def list_files():
    try:
        response = requests.get(
            f"{SERVER_URL}/files",
            headers=get_auth_headers(),
            timeout=10
        )

        if response.status_code != 200:
            show_error(response)
            return []

        files = response.json()["files"]

        if not files:
            print("\nNo files stored in your account.")
            return []

        print("\n===== MY STORED FILES =====")

        for index, file in enumerate(files, start=1):
            print(
                f"{index}. {file['filename']} "
                f"| ID: {file['file_id']} "
                f"| Size: {file['size']} bytes"
            )

        return files

    except (requests.RequestException, ValueError, KeyError) as error:
        print("Unable to list files:", error)
        return []


def download_file(file_id=None, file_info=None):
    if file_id is None:
        file_id = input("Enter file ID: ").strip()

    try:
        if file_info is None:
            response = requests.get(
                f"{SERVER_URL}/files",
                headers=get_auth_headers(),
                timeout=10
            )

            if response.status_code != 200:
                show_error(response)
                return

            files = response.json()["files"]

            file_info = next(
                (file for file in files if file["file_id"] == file_id),
                None
            )

        if file_info is None:
            print("File not found in your account.")
            return

        response = requests.get(
            f"{SERVER_URL}/download/{file_id}",
            headers=get_auth_headers(),
            timeout=60
        )

        if response.status_code != 200:
            show_error(response)
            return

        decrypted_data = decrypt_file(response.content)

        filename = Path(
            file_info["filename"].replace("\\", "/")
        ).name

        if filename in ("", ".", "..", "unknown"):
            filename = f"{file_id}.bin"

        while True:
            output_path = get_unique_filename(filename)

            try:
                with open(output_path, "xb") as output:
                    output.write(decrypted_data)
                break

            except FileExistsError:
                continue

        print("\nFile downloaded and decrypted!")
        print("Saved to:", output_path)

    except Exception as error:
        print("Download failed:", error)


def download_all():
    files = list_files()

    if not files:
        return

    print("\nDownloading all your files...")

    for file in files:
        download_file(
            file_id=file["file_id"],
            file_info=file
        )

    print("\nDownload process completed.")


def guest_menu():
    print("\n================================")
    print("      SECURE CLOUD STORAGE")
    print("================================")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

    return input("\nEnter your choice: ").strip()


def user_menu():
    print("\n================================")
    print(f"      WELCOME, {current_username}")
    print("================================")
    print("1. Upload a file")
    print("2. List my files")
    print("3. Download and decrypt a file")
    print("4. Download all my files")
    print("5. Logout")
    print("6. Exit")

    return input("\nEnter your choice: ").strip()


def main():
    while True:
        if access_token is None:
            choice = guest_menu()

            if choice == "1":
                register()

            elif choice == "2":
                login()

            elif choice == "3":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Try again.")

        else:
            choice = user_menu()

            if choice == "1":
                upload_file()

            elif choice == "2":
                list_files()

            elif choice == "3":
                download_file()

            elif choice == "4":
                download_all()

            elif choice == "5":
                logout()

            elif choice == "6":
                logout()
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
