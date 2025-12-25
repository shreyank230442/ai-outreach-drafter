import pandas as pd

REQUIRED_COLUMNS = {
    "email",
    "company",
    "job_description",
    "role",
    "your_skills"
}

def load_and_validate_excel(file):
    try:
        df = pd.read_excel(file)
        df.columns = df.columns.str.lower().str.strip()

        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            return None, f"Missing required columns: {', '.join(missing)}"

        df = df.dropna(subset=["email", "company", "job_description"])
        return df, None

    except Exception as e:
        return None, str(e)