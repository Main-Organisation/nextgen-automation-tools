import json
import os
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://vgu.digiicampus.com"

EXCEL_FILE = Path(
    r"D:\Projects\Diggi_Automate\assignments.xlsx"
)

MAX_ASSIGNMENTS = 5

LOGIN_TIMEOUT = 600  # 10 minutes


# ============================================================
# 1. START CHROME
# ============================================================

def start_browser():
    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    # Capture browser network traffic so the authenticated
    # DigiCampus auth-token can be obtained after login.
    options.set_capability(
        "goog:loggingPrefs",
        {"performance": "ALL"}
    )

    return webdriver.Chrome(options=options)


# ============================================================
# 2. LOGIN
# ============================================================

def login(driver):
    print("\n==========================================")
    print("DIGICAMPUS LOGIN")
    print("==========================================")

    driver.get(
        f"{BASE_URL}/V2/#/home"
    )

    print("DigiCampus login page opened.")
    print()
    print("Please login manually.")
    print("Google/Cloudflare verification agar aaye to complete karo.")
    print("Login successful hote hi automation automatically continue karegi.")
    print("ENTER press karne ki zarurat nahi hai.")

    # Optional: click Google button when it is directly detectable.
    google_button = None

    selectors = [
        "//button[contains("
        "translate(., "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
        "'abcdefghijklmnopqrstuvwxyz'), "
        "'google'"
        ")]",

        "//*[contains("
        "translate(., "
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
        "'abcdefghijklmnopqrstuvwxyz'), "
        "'sign in with google'"
        ")]"
    ]

    for selector in selectors:
        try:
            google_button = WebDriverWait(
                driver,
                5
            ).until(
                EC.element_to_be_clickable(
                    (By.XPATH, selector)
                )
            )
            break
        except Exception:
            continue

    if google_button:
        try:
            google_button.click()
        except Exception:
            driver.execute_script(
                "arguments[0].click();",
                google_button
            )

        print("Google sign-in clicked.")
    else:
        print("Google button automatically detect nahi hua.")
        print("Browser mein login manually complete karo.")

    start_time = time.time()

    while True:
        current_url = driver.current_url.lower()

        body_text = ""
        try:
            body_text = driver.find_element(
                By.TAG_NAME,
                "body"
            ).text.lower()
        except Exception:
            pass

        logged_in = (
            "/feed" in current_url
            or "/classroom" in current_url
            or "course work" in body_text
            or "asst. prof." in body_text
        )

        if logged_in:
            print("\n==========================================")
            print("LOGIN SUCCESSFUL")
            print("==========================================")
            print("Logged-in URL:", driver.current_url)
            return

        if time.time() - start_time > LOGIN_TIMEOUT:
            raise TimeoutError(
                "Login timeout: 10 minutes ke andar "
                "DigiCampus login detect nahi hua."
            )

        time.sleep(2)


# ============================================================
# 3. CAPTURE AUTH TOKEN
# ============================================================

def capture_auth_token(driver):
    print("\n==========================================")
    print("CAPTURING AUTH-TOKEN")
    print("==========================================")

    auth_token = None

    for entry in driver.get_log("performance"):
        try:
            message = json.loads(
                entry["message"]
            )["message"]

            if message["method"] != "Network.requestWillBeSent":
                continue

            request = message["params"]["request"]

            for name, value in request.get(
                "headers", {}
            ).items():

                if name.lower() == "auth-token":
                    auth_token = value
                    break

            if auth_token:
                break

        except Exception:
            continue

    if not auth_token:
        raise RuntimeError(
            "Actual auth-token capture nahi hua."
        )

    print("Auth-token captured successfully.")
    print("Token value display nahi kiya ja raha.")

    return auth_token


# ============================================================
# 4. CREATE REQUESTS SESSION
# ============================================================

def create_session(driver, auth_token):
    session = requests.Session()

    for cookie in driver.get_cookies():
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain"),
            path=cookie.get("path", "/")
        )

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/V2/",
        "auth-token": auth_token
    }

    return session, headers


# ============================================================
# 5. FETCH LOGGED-IN FACULTY CLASSROOMS
# ============================================================

def fetch_classrooms(session, headers):
    print("\n==========================================")
    print("FETCHING FACULTY CLASSROOMS")
    print("==========================================")

    url = (
        f"{BASE_URL}/"
        "rest/classes/v1/classroom"
    )

    response = session.get(
        url,
        headers=headers,
        timeout=30
    )

    print(
        "Classroom API:",
        response.status_code
    )

    if not response.ok:
        raise RuntimeError(
            "Faculty classroom API failed:\n"
            + response.text[:2000]
        )

    classrooms = response.json()

    if not isinstance(classrooms, list):
        raise RuntimeError(
            "Unexpected classroom API response."
        )

    print(
        "Mapped classrooms found:",
        len(classrooms)
    )

    print("\nMapped classes:")

    for classroom in classrooms:
        print(
            f"- {classroom.get('courseCode')} | "
            f"{classroom.get('courseComponentTypeName')} | "
            f"{classroom.get('className')} | "
            f"ID={classroom.get('id')}"
        )

    return classrooms


# ============================================================
# 6. MATCH EXACT CLASSROOM
# ============================================================

def normalize(value):
    return " ".join(
        str(value)
        .strip()
        .upper()
        .split()
    )


def find_classroom(
    classrooms,
    course_code,
    component_type,
    class_name
):
    target_code = normalize(course_code)
    target_component = normalize(component_type)
    target_class = normalize(class_name)

    matches = []

    for classroom in classrooms:
        api_code = normalize(
            classroom.get("courseCode", "")
        )

        api_component = normalize(
            classroom.get(
                "courseComponentTypeName",
                ""
            )
        )

        api_class = normalize(
            classroom.get("className", "")
        )

        if (
            api_code == target_code
            and api_component == target_component
            and api_class == target_class
        ):
            matches.append(classroom)

    if not matches:
        # Show possible candidates for easier troubleshooting.
        candidates = []

        for classroom in classrooms:
            if normalize(
                classroom.get("courseCode", "")
            ) == target_code:
                candidates.append(
                    f"ID={classroom.get('id')} | "
                    f"{classroom.get('courseComponentTypeName')} | "
                    f"{classroom.get('className')}"
                )

        candidate_text = (
            "\n".join(candidates)
            if candidates
            else "No classroom with this CourseCode found."
        )

        raise RuntimeError(
            "No exact mapped classroom found.\n"
            f"CourseCode: {course_code}\n"
            f"ComponentType: {component_type}\n"
            f"ClassName: {class_name}\n\n"
            f"Available candidates:\n{candidate_text}"
        )

    if len(matches) > 1:
        raise RuntimeError(
            "More than one exact classroom matched. "
            "Please verify ClassName."
        )

    selected = matches[0]

    print("\nSelected classroom:")
    print("Course:", selected.get("courseName"))
    print("Course Code:", selected.get("courseCode"))
    print(
        "Component:",
        selected.get("courseComponentTypeName")
    )
    print("Class:", selected.get("className"))
    print("Faculty:", selected.get("faculty"))
    print("Class ID:", selected.get("id"))

    return selected


# ============================================================
# 7. READ EXCEL
# ============================================================

def load_excel():
    print("\n==========================================")
    print("READING EXCEL")
    print("==========================================")

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"Excel file not found:\n{EXCEL_FILE}"
        )

    df = pd.read_excel(EXCEL_FILE)

    required_columns = [
        "CourseCode",
        "ComponentType",
        "ClassName",
        "Title",
        "Description",
        "StartDate",
        "DueDate",
        "DocxPath"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Excel mein ye columns missing hain: "
            f"{missing_columns}"
        )

    df = df.dropna(
        subset=required_columns
    )

    df = df.head(
        MAX_ASSIGNMENTS
    )

    print(
        "Assignments found:",
        len(df)
    )

    return df


# ============================================================
# 8. CONVERT DATE
# ============================================================

def convert_date(date_value):
    if isinstance(
        date_value,
        datetime
    ):
        return date_value.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    date_text = str(
        date_value
    ).strip()

    formats = [
        "%d %b %Y %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(
                date_text,
                fmt
            )

            return dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        except ValueError:
            continue

    raise ValueError(
        f"Unsupported date format: {date_text}"
    )


# ============================================================
# 9. GENERATE SIGNED URL
# ============================================================

def generate_signed_url(
    session,
    headers,
    docx_path
):
    file_size = os.path.getsize(
        docx_path
    )

    file_name = os.path.basename(
        docx_path
    )

    url = (
        f"{BASE_URL}/"
        "rest/attachment/"
        "generatePutSignedUrl"
    )

    payload = {
        "fileName": file_name,
        "contentLength": file_size,
        "contentType":
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document",
        "feature": "ASSIGNMENT_RESOURCE"
    }

    request_headers = headers.copy()

    request_headers[
        "Content-Type"
    ] = "application/json"

    response = session.post(
        url,
        headers=request_headers,
        json=payload,
        timeout=30
    )

    print(
        "Signed URL API:",
        response.status_code
    )

    if not response.ok:
        raise RuntimeError(
            "Signed URL generation failed:\n"
            + response.text[:2000]
        )

    data = response.json()

    media = data.get(
        "media",
        {}
    )

    media_id = media.get("id")
    document_id = media.get("documentId")
    signed_url = data.get("signedUrl")

    if not signed_url:
        raise RuntimeError(
            "signedUrl response mein nahi mila."
        )

    return (
        media_id,
        document_id,
        signed_url
    )


# ============================================================
# 10. UPLOAD DOCX TO S3
# ============================================================

def upload_to_s3(
    signed_url,
    docx_path
):
    print(
        "Uploading DOCX to S3..."
    )

    with open(
        docx_path,
        "rb"
    ) as file:

        response = requests.put(
            signed_url,
            data=file,
            headers={
                "Content-Type":
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
            },
            timeout=120
        )

    print(
        "S3 Status:",
        response.status_code
    )

    if response.status_code != 200:
        raise RuntimeError(
            "S3 upload failed:\n"
            + response.text[:1000]
        )

    print(
        "S3 upload successful."
    )


# ============================================================
# 11. CREATE ASSIGNMENT DRAFT
# ============================================================

def create_assignment(
    session,
    headers,
    class_id,
    title,
    description,
    start_date,
    due_date,
    media_id,
    document_id
):
    url = (
        f"{BASE_URL}/"
        "rest/assignments/v1/"
        f"?classId={class_id}"
    )

    payload = {
        "name": title,
        "description": description,
        "assignmentType": "CLASS",
        "assignmentCourseOutcome": [],
        "clone": False,
        "draft": 1,
        "dueDate": due_date,
        "group_submission_type": "INDIVIDUAL",
        "groups": [],
        "maximumMarks": "",
        "minimumMarks": "",
        "resources": [
            {
                "mediaId": media_id,
                "documentId": document_id,
                "message": "UPLOADED"
            }
        ],
        "rubricCriterias": [],
        "rubricGrading": False,
        "rubricLevels": [],
        "startDate": start_date,
        "submissionType": "upload",
        "topicLevelOutcomesList": [],
        "turnitinEnabled": False
    }

    request_headers = headers.copy()

    request_headers[
        "Content-Type"
    ] = "application/json"

    response = session.post(
        url,
        headers=request_headers,
        json=payload,
        timeout=30
    )

    print(
        "Assignment API:",
        response.status_code
    )

    if response.status_code not in [
        200,
        201
    ]:
        raise RuntimeError(
            "Assignment creation failed:\n"
            + response.text[:2000]
        )

    return response.text.strip()


# ============================================================
# 12. MAIN AUTOMATION
# ============================================================

def main():
    print(
        "\n=========================================="
    )

    print(
        "DIGICAMPUS ASSIGNMENT AUTOMATION"
    )

    print(
        "=========================================="
    )

    driver = start_browser()

    try:
        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        login(driver)

        # ----------------------------------------------------
        # AUTH TOKEN
        # ----------------------------------------------------

        auth_token = capture_auth_token(
            driver
        )

        # ----------------------------------------------------
        # REQUEST SESSION
        # ----------------------------------------------------

        session, headers = create_session(
            driver,
            auth_token
        )

        # ----------------------------------------------------
        # FETCH FACULTY CLASSES
        # ----------------------------------------------------

        classrooms = fetch_classrooms(
            session,
            headers
        )

        # ----------------------------------------------------
        # READ EXCEL
        # ----------------------------------------------------

        df = load_excel()

        if len(df) == 0:
            print(
                "Excel mein koi assignment row nahi hai."
            )
            return

        print(
            "\n=========================================="
        )

        print(
            "STARTING AUTOMATION"
        )

        print(
            "=========================================="
        )

        successful = 0

        # ----------------------------------------------------
        # PROCESS ASSIGNMENTS
        # ----------------------------------------------------

        for position, (_, row) in enumerate(
            df.iterrows(),
            start=1
        ):
            print(
                "\n------------------------------------------"
            )

            print(
                f"ASSIGNMENT {position}/{len(df)}"
            )

            print(
                "------------------------------------------"
            )

            course_code = str(
                row["CourseCode"]
            ).strip()

            component_type = str(
                row["ComponentType"]
            ).strip()

            class_name = str(
                row["ClassName"]
            ).strip()

            title = str(
                row["Title"]
            )

            description = str(
                row["Description"]
            )

            start_date = convert_date(
                row["StartDate"]
            )

            due_date = convert_date(
                row["DueDate"]
            )

            docx_path = Path(
                str(
                    row["DocxPath"]
                )
            )

            if not docx_path.is_absolute():
                docx_path = (
                    EXCEL_FILE.parent
                    / docx_path
                )

            print(
                "Course Code:",
                course_code
            )

            print(
                "Component:",
                component_type
            )

            print(
                "Class Name:",
                class_name
            )

            print(
                "Title:",
                title
            )

            print(
                "Start:",
                start_date
            )

            print(
                "Due:",
                due_date
            )

            print(
                "DOCX:",
                docx_path
            )

            if not docx_path.exists():
                print(
                    "ERROR: DOCX file not found."
                )
                continue

            try:
                # ------------------------------------------------
                # MATCH FACULTY CLASS FIRST
                # ------------------------------------------------

                classroom = find_classroom(
                    classrooms,
                    course_code,
                    component_type,
                    class_name
                )

                class_id = classroom.get(
                    "id"
                )

                # ------------------------------------------------
                # ONLY AFTER A VALID CLASS MATCH:
                # GENERATE SIGNED URL
                # ------------------------------------------------

                (
                    media_id,
                    document_id,
                    signed_url
                ) = generate_signed_url(
                    session,
                    headers,
                    docx_path
                )

                print(
                    "Media ID:",
                    media_id
                )

                print(
                    "Document ID:",
                    document_id
                )

                # ------------------------------------------------
                # S3 UPLOAD
                # ------------------------------------------------

                upload_to_s3(
                    signed_url,
                    docx_path
                )

                # ------------------------------------------------
                # CREATE ASSIGNMENT DRAFT
                # ------------------------------------------------

                print(
                    "Creating assignment draft..."
                )

                assignment_result = (
                    create_assignment(
                        session,
                        headers,
                        class_id,
                        title,
                        description,
                        start_date,
                        due_date,
                        media_id,
                        document_id
                    )
                )

                print(
                    "Assignment created successfully."
                )

                print(
                    "ERP Response:",
                    assignment_result
                )

                successful += 1

            except Exception as error:
                print(
                    "\nERROR while processing "
                    "this assignment:"
                )

                print(
                    error
                )

        # ----------------------------------------------------
        # FINAL
        # ----------------------------------------------------

        print(
            "\n=========================================="
        )

        print(
            "AUTOMATION COMPLETE"
        )

        print(
            "=========================================="
        )

        print(
            "Successful:",
            successful,
            "/",
            len(df)
        )

        print(
            "\nIMPORTANT:"
        )

        print(
            "Publish API was NOT called."
        )

        print(
            "Successful assignments remain DRAFTS."
        )

    finally:
        print(
            "\nClosing Chrome..."
        )

        driver.quit()

        print(
            "Chrome closed."
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
