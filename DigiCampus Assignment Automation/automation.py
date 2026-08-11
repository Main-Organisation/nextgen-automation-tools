import json
import os
import time
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

CLASS_ID = 14880

EXCEL_FILE = Path(
    r"D:\Projects\Diggi_Automate\assignments.xlsx"
)

MAX_ASSIGNMENTS = 5


# ============================================================
# 1. START CHROME
# ============================================================

def start_browser():

    options = webdriver.ChromeOptions()

    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    # Capture network requests so we can obtain
    # the actual DigiCampus auth-token after login.
    options.set_capability(
        "goog:loggingPrefs",
        {
            "performance": "ALL"
        }
    )

    driver = webdriver.Chrome(
        options=options
    )

    return driver


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

    # --------------------------------------------------------
    # Try to find "Sign in with Google"
    # --------------------------------------------------------

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
                    (
                        By.XPATH,
                        selector
                    )
                )
            )

            break

        except Exception:

            continue

    if google_button:

        print(
            "Sign in with Google button found."
        )

        try:

            google_button.click()

        except Exception:

            driver.execute_script(
                "arguments[0].click();",
                google_button
            )

        print(
            "Google sign-in clicked."
        )

    else:

        print(
            "Google button automatically detect nahi hua."
        )

        print(
            "Browser mein login manually complete karo."
        )

    # --------------------------------------------------------
    # Wait for login
    # --------------------------------------------------------

    print(
        "\nGoogle/Cloudflare verification agar aaye "
        "to manually complete karo."
    )

    print(
        "ERP login complete hone ka wait kar raha hoon..."
    )

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

            or

            "/classroom" in current_url

            or

            "course work" in body_text

            or

            "asst. prof." in body_text
        )

        if logged_in:

            print(
                "\nLOGIN SUCCESSFUL."
            )

            print(
                "Logged-in URL:",
                driver.current_url
            )

            return

        # ----------------------------------------------------
        # 3 minute safety timeout
        # ----------------------------------------------------

        if time.time() - start_time > 180:

            print(
                "\nAutomatic login detection timeout."
            )

            input(
                "ERP login complete hone ke baad "
                "ENTER dabao..."
            )

            return

        time.sleep(2)


# ============================================================
# 3. OPEN CLASSROOM
# ============================================================

def open_classroom(driver):

    print(
        "\n=========================================="
    )

    print(
        "OPENING CLASSROOM"
    )

    print(
        "=========================================="
    )

    driver.get(
        f"{BASE_URL}/V2/#/classroom/"
        f"{CLASS_ID}/resources"
    )

    WebDriverWait(
        driver,
        30
    ).until(
        EC.presence_of_element_located(
            (
                By.ID,
                "root"
            )
        )
    )

    WebDriverWait(
        driver,
        30
    ).until(
        lambda d:
        len(
            d.find_element(
                By.TAG_NAME,
                "body"
            ).text.strip()
        ) > 100
    )

    print(
        "ERP classroom loaded."
    )


# ============================================================
# 4. CAPTURE AUTH TOKEN
# ============================================================

def capture_auth_token(driver):

    print(
        "\n=========================================="
    )

    print(
        "CAPTURING AUTH-TOKEN"
    )

    print(
        "=========================================="
    )

    auth_token = None

    logs = driver.get_log(
        "performance"
    )

    for entry in logs:

        try:

            message = json.loads(
                entry["message"]
            )["message"]

            if message["method"] != (
                "Network.requestWillBeSent"
            ):
                continue

            request = message[
                "params"
            ][
                "request"
            ]

            request_headers = request.get(
                "headers",
                {}
            )

            for name, value in request_headers.items():

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

    print(
        "Auth-token captured successfully."
    )

    print(
        "Token value display nahi kiya ja raha."
    )

    return auth_token

from datetime import datetime


def convert_date(date_value):

    # Excel se aane wali date:
    # 30 Aug 2026 10:00

    date_text = str(date_value).strip()

    dt = datetime.strptime(
        date_text,
        "%d %b %Y %H:%M"
    )

    # DigiCampus API format:
    # 2026-08-30 10:00:00

    return dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
# ============================================================
# 5. CREATE REQUESTS SESSION
# ============================================================

def create_session(
    driver,
    auth_token
):

    session = requests.Session()

    cookies = driver.get_cookies()

    for cookie in cookies:

        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get(
                "domain"
            ),
            path=cookie.get(
                "path",
                "/"
            )
        )

    headers = {

        "Accept":
            "application/json, text/plain, */*",

        "Origin":
            BASE_URL,

        "Referer":
            f"{BASE_URL}/V2/",

        "auth-token":
            auth_token
    }

    return session, headers


# ============================================================
# 6. READ EXCEL
# ============================================================

def load_excel():

    print(
        "\n=========================================="
    )

    print(
        "READING EXCEL"
    )

    print(
        "=========================================="
    )

    if not EXCEL_FILE.exists():

        raise FileNotFoundError(
            f"Excel file not found:\n"
            f"{EXCEL_FILE}"
        )

    df = pd.read_excel(
        EXCEL_FILE
    )

    required_columns = [

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

    # Remove completely empty rows
    df = df.dropna(
        subset=required_columns
    )

    # First 5 only
    df = df.head(
        MAX_ASSIGNMENTS
    )

    print(
        "Assignments found:",
        len(df)
    )

    return df


# ============================================================
# 7. GENERATE SIGNED URL
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

        "fileName":
            file_name,

        "contentLength":
            file_size,

        "contentType":
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document",

        "feature":
            "ASSIGNMENT_RESOURCE"
    }

    request_headers = headers.copy()

    request_headers[
        "Content-Type"
    ] = "application/json"
    print("\n========== ASSIGNMENT PAYLOAD ==========")

    import json

    print(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False
        )
    )

    print("========================================")
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

    media_id = media.get(
        "id"
    )

    document_id = media.get(
        "documentId"
    )

    signed_url = data.get(
        "signedUrl"
    )

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
# 8. UPLOAD DOCX TO S3
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
# 9. CREATE ASSIGNMENT DRAFT
# ============================================================

def create_assignment(

    session,
    headers,

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
        f"?classId={CLASS_ID}"
    )

    payload = {

        "name":
            title,

        "description":
            description,

        "assignmentType":
            "CLASS",

        "assignmentCourseOutcome":
            [],

        "clone":
            False,

        "draft":
            1,

        "dueDate":
            due_date,

        "group_submission_type":
            "INDIVIDUAL",

        "groups":
            [],

        "maximumMarks":
            "",

        "minimumMarks":
            "",

        "resources":
            [
                {
                    "mediaId":
                        media_id,

                    "documentId":
                        document_id,

                    "message":
                        "UPLOADED"
                }
            ],

        "rubricCriterias":
            [],

        "rubricGrading":
            False,

        "rubricLevels":
            [],

        "startDate":
            start_date,

        "submissionType":
            "upload",

        "topicLevelOutcomesList":
            [],

        "turnitinEnabled":
            False
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
# 10. MAIN AUTOMATION
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

        login(
            driver
        )

        # ----------------------------------------------------
        # CLASSROOM
        # ----------------------------------------------------

        open_classroom(
            driver
        )

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
        # EXCEL
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

            title = str(
                row["Title"]
            )

            description = str(
                row["Description"]
            )

            start_date = str(
                row["StartDate"]
            )

            due_date = str(
                row["DueDate"]
            )

            docx_path = Path(
                str(
                    row["DocxPath"]
                )
            )

            # ------------------------------------------------
            # Relative DOCX path
            # ------------------------------------------------

            if not docx_path.is_absolute():

                docx_path = (
                    EXCEL_FILE.parent
                    / docx_path
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

            # ------------------------------------------------
            # Check DOCX
            # ------------------------------------------------

            if not docx_path.exists():

                print(
                    "ERROR: DOCX file not found."
                )

                continue

            try:

                # ------------------------------------------------
                # SIGNED URL
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
                # ASSIGNMENT
                # ------------------------------------------------

                print(
                    "Creating assignment draft..."
                )

                assignment_result = (
                    create_assignment(

                        session,
                        headers,

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