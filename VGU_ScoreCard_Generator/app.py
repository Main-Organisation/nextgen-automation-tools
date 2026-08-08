import pandas as pd
import re
EXCEL_FILE = "input/MCA_Students_Scores_and_Ranks.xlsx"


def read_raw_sheet(sheet_name):
    return pd.read_excel(
        EXCEL_FILE,
        sheet_name=sheet_name,
        header=None
    )


def find_vgucet_header(df):
    """
    Find the actual table header for VGUCET data.
    """

    # First try to find a VGUCET section title
    for i in range(len(df)):

        row_text = " ".join(
            str(value).strip()
            for value in df.iloc[i].tolist()
            if pd.notna(value)
        ).upper()

        if "VGUCET" in row_text:

            # Search the next few rows for the actual header
            for j in range(i + 1, min(i + 5, len(df))):

                values = [
                    str(value).strip().lower()
                    for value in df.iloc[j].tolist()
                    if pd.notna(value)
                ]

                if "rank" in values and (
                    "full name" in values or "name" in values
                ):
                    return j

    # For sheets where VGUCET is already the main table,
    # find the first proper header.
    for i in range(len(df)):

        values = [
            str(value).strip().lower()
            for value in df.iloc[i].tolist()
            if pd.notna(value)
        ]

        if "rank" in values and (
            "full name" in values or "name" in values
        ):
            return i

    return None


def extract_vgucet_data(sheet_name):
    """
    Extract clean Name, Score and Rank records.
    """

    df = read_raw_sheet(sheet_name)

    header_row = find_vgucet_header(df)

    if header_row is None:
        print(f"❌ VGUCET header not found: {sheet_name}")
        return pd.DataFrame()

    print(f"\n{sheet_name}")
    print(f"VGUCET header found at row: {header_row}")

    # Get header names
    headers = [
        str(value).strip()
        if pd.notna(value)
        else f"Column_{i}"
        for i, value in enumerate(df.iloc[header_row])
    ]

    print("Headers:", headers)

    # Data below header
    data = df.iloc[header_row + 1:].copy()

    # Assign proper column names
    data.columns = headers

    # Find required columns
    name_column = None
    score_column = None
    rank_column = None

    for column in data.columns:

        column_lower = str(column).lower()

        if "name" in column_lower:
            name_column = column

        elif "score" in column_lower:
            score_column = column

        elif "rank" in column_lower:
            rank_column = column

    if not name_column or not score_column or not rank_column:
        print("❌ Required columns not found.")
        return pd.DataFrame()

    # Create clean DataFrame
    year_match = re.search(r"\b(20\d{2})\b", sheet_name)

    if year_match:
        year = int(year_match.group(1))
    else:
        print(f"❌ Year not found in sheet name: {sheet_name}")
        return pd.DataFrame()

    clean_data = pd.DataFrame()

    clean_data["Name"] = data[name_column].values
    clean_data["Score"] = data[score_column].values
    clean_data["Rank"] = data[rank_column].values

    # Add year as a fixed value for every record
    clean_data["Year"] = year

    # Keep columns in required order
    clean_data = clean_data[
        ["Year", "Name", "Score", "Rank"]
    ]
    # Add year after creating the data columns
    clean_data["Year"] = year

    # Remove empty names
    clean_data = clean_data[
        clean_data["Name"].notna()
    ]

    # Keep only VGUCET ranks
    clean_data["Rank"] = clean_data["Rank"].astype(str).str.strip()

    clean_data = clean_data[
        clean_data["Rank"].str.upper().str.startswith("VGUCET")
    ]

    # Clean names
    clean_data["Name"] = (
        clean_data["Name"]
        .astype(str)
        .str.strip()
    )

    # Clean score
    clean_data["Score"] = (
        clean_data["Score"]
        .astype(str)
        .str.strip()
    )

    # Reset index
    clean_data = clean_data.reset_index(drop=True)

    return clean_data

def generate_application_numbers(final_data):
    start_number = 35055

    application_numbers = []

    for index, row in final_data.iterrows():
        current_number = start_number + index

        application_number = (
            f"VGU_{row['Year']}_55_{current_number:06d}"
        )

        application_numbers.append(application_number)

    final_data["Application Number"] = application_numbers

    return final_data
# --------------------------------------------------
# TEST ALL SHEETS
# --------------------------------------------------

excel = pd.ExcelFile(EXCEL_FILE)

all_data = []

for sheet in excel.sheet_names:

    print("\n" + "=" * 70)
    print(f"PROCESSING: {sheet}")
    print("=" * 70)

    data = extract_vgucet_data(sheet)

    print(f"\nRecords found: {len(data)}")

    print("\nFirst 10 clean records:")

    print(
        data.head(10).to_string(index=False)
    )

    if not data.empty:
        all_data.append(data)


# Combine all sheets
# Combine all sheets

if all_data:

    final_data = pd.concat(
        all_data,
        ignore_index=True
    )

    print("\n" + "=" * 70)
    print("FINAL COMBINED DATA")
    print("=" * 70)

    print(f"Total VGUCET records: {len(final_data)}")

    print("\nSample records:")

    print(
        final_data.head(20).to_string(index=False)
    )

    # Sort records chronologically
    final_data["Year"] = final_data["Year"].astype(int)

    final_data = final_data.sort_values(
        by=["Year"],
        kind="stable"
    ).reset_index(drop=True)
    # Generate continuous Application Numbers
    final_data = generate_application_numbers(final_data)

    print("\n" + "=" * 70)
    print("FINAL DATA WITH APPLICATION NUMBERS")
    print("=" * 70)

    print(f"Total VGUCET records: {len(final_data)}")

    print("\nFirst 10 records:")
    print(
        final_data.head(10).to_string(index=False)
    )

    print("\nLast 10 records:")
    print(
        final_data.tail(10).to_string(index=False)
    )

    # --------------------------------------------------
    # SAVE GENERATED RECORDS
    # --------------------------------------------------

    OUTPUT_EXCEL = "generated/MCA_Students_Scores_and_Ranks_Updated.xlsx"

    final_data.to_excel(
        OUTPUT_EXCEL,
        index=False
    )

    print("\n" + "=" * 70)
    print("UPDATED EXCEL SAVED")
    print("=" * 70)

    print(f"File: {OUTPUT_EXCEL}")