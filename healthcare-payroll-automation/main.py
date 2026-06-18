import os
from shift_processor import process_shift_hours
from document_generator import generate_documents


# =========================================================
# FILE PATHS
# =========================================================

DATA_FOLDER = "data"
OUTPUT_FOLDER = "outputs"

ltss_file = os.path.join(DATA_FOLDER, "ltss_shifts.csv")
clients_file = os.path.join(DATA_FOLDER, "clients.csv")
caretakers_file = os.path.join(DATA_FOLDER, "caretakers.csv")

final_shift_hours_csv = os.path.join(
    OUTPUT_FOLDER,
    "final_shift_hours_with_caps.csv"
)

weekly_summary_csv = os.path.join(
    OUTPUT_FOLDER,
    "final_weekly_approved_hours_summary.csv"
)


# =========================================================
# CREATE OUTPUT FOLDER
# =========================================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# =========================================================
# RUN SHIFT PROCESSING
# =========================================================

final_shift_hours_df, weekly_summary_df = process_shift_hours(
    ltss_file=ltss_file,
    clients_file=clients_file,
    caretakers_file=caretakers_file,
    output_csv=final_shift_hours_csv,
    weekly_summary_csv=weekly_summary_csv
)

print("\nSHIFT PROCESSING COMPLETE")
print("-" * 50)
print(f"Created: {final_shift_hours_csv}")
print(f"Created: {weekly_summary_csv}")


# =========================================================
# RUN DOCUMENT GENERATION
# =========================================================

generate_documents(
    final_shift_hours_df=final_shift_hours_df,
    caretakers_file=caretakers_file,
    output_folder=OUTPUT_FOLDER
)

print("\nPAYROLL DOCUMENT GENERATION COMPLETE")
print("-" * 50)
print("Timesheets and paystubs created successfully.")