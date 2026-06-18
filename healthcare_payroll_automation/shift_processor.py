import pandas as pd


# =========================================================
# CLIENT CLASS
# =========================================================

class Client:
    def __init__(self, client_id, client_name, weekly_authorized_hours):
        self.client_id = client_id
        self.client_name = client_name
        self.weekly_authorized_hours = weekly_authorized_hours

    def __repr__(self):
        return (
            f"Client("
            f"id={self.client_id}, "
            f"name='{self.client_name}', "
            f"weekly_hours={self.weekly_authorized_hours})"
        )


# =========================================================
# CARETAKER CLASS
# =========================================================

class Caretaker:
    def __init__(self, caretaker_id, caretaker_name, hourly_rate):
        self.caretaker_id = caretaker_id
        self.caretaker_name = caretaker_name
        self.hourly_rate = hourly_rate

    def __repr__(self):
        return (
            f"Caretaker("
            f"id={self.caretaker_id}, "
            f"name='{self.caretaker_name}', "
            f"rate=${self.hourly_rate}/hr)"
        )


# =========================================================
# SHIFT CLASS
# =========================================================

class Shift:
    def __init__(self, client, caretaker, service_date, clock_in, clock_out):
        self.client = client
        self.caretaker = caretaker
        self.service_date = service_date
        self.clock_in = clock_in
        self.clock_out = clock_out

    def calculate_hours(self):
        if pd.isna(self.clock_in) or pd.isna(self.clock_out):
            return None

        time_difference = self.clock_out - self.clock_in
        hours_worked = time_difference.total_seconds() / 3600

        return round(hours_worked, 2)

    def has_missing_clock_out(self):
        return pd.isna(self.clock_out)

    def has_missing_clock_in(self):
        return pd.isna(self.clock_in)

    def __repr__(self):
        return (
            f"Shift("
            f"client={self.client.client_name}, "
            f"caretaker={self.caretaker.caretaker_name}, "
            f"date={self.service_date}, "
            f"hours={self.calculate_hours()})"
        )


# =========================================================
# CREATE OBJECTS
# =========================================================

def create_client_objects(clients_df):
    clients = {}

    for _, row in clients_df.iterrows():
        client = Client(
            client_id=row["client_id"],
            client_name=row["client_name"],
            weekly_authorized_hours=row["weekly_authorized_hours"]
        )

        clients[row["client_id"]] = client

    return clients


def create_caretaker_objects(caretakers_df):
    caretakers = {}

    for _, row in caretakers_df.iterrows():
        caretaker = Caretaker(
            caretaker_id=row["caretaker_id"],
            caretaker_name=row["caretaker_name"],
            hourly_rate=row["hourly_rate"]
        )

        caretakers[row["caretaker_id"]] = caretaker

    return caretakers


def create_shift_objects(shifts_df, clients, caretakers):
    shifts = []

    for _, row in shifts_df.iterrows():
        shift = Shift(
            client=clients[row["client_id"]],
            caretaker=caretakers[row["caretaker_id"]],
            service_date=row["service_date"],
            clock_in=row["clock_in"],
            clock_out=row["clock_out"]
        )

        shifts.append(shift)

    return shifts


# =========================================================
# CALCULATE SHIFT HOURS
# =========================================================

def calculate_all_shift_hours(shifts):
    shift_records = []

    for shift in shifts:
        hours_worked = shift.calculate_hours()

        shift_records.append({
            "client_id": shift.client.client_id,
            "client_name": shift.client.client_name,
            "caretaker_id": shift.caretaker.caretaker_id,
            "caretaker_name": shift.caretaker.caretaker_name,
            "service_date": shift.service_date,
            "clock_in": shift.clock_in,
            "clock_out": shift.clock_out,
            "hours_worked": hours_worked,
            "missing_clock_in": shift.has_missing_clock_in(),
            "missing_clock_out": shift.has_missing_clock_out()
        })

    return pd.DataFrame(shift_records)


# =========================================================
# IMPUTE MISSING PUNCHES
# =========================================================

def impute_missing_punches_using_medicaid_cap(
    shift_hours_df,
    clients,
    default_shift_hours=4,
    min_shift_hours=2,
    max_shift_hours=8
):
    df = shift_hours_df.copy()

    df["service_date"] = pd.to_datetime(df["service_date"])
    df["clock_in"] = pd.to_datetime(df["clock_in"], errors="coerce")
    df["clock_out"] = pd.to_datetime(df["clock_out"], errors="coerce")

    df["week_start"] = (
        df["service_date"]
        - pd.to_timedelta(df["service_date"].dt.weekday, unit="D")
    )

    df["week_end"] = df["week_start"] + pd.Timedelta(days=6)

    df["corrected_clock_in"] = df["clock_in"]
    df["corrected_clock_out"] = df["clock_out"]

    df["was_clock_in_imputed"] = False
    df["was_clock_out_imputed"] = False
    df["needs_manual_review"] = False
    df["imputation_reason"] = ""

    df["known_hours"] = (
        df["clock_out"] - df["clock_in"]
    ).dt.total_seconds() / 3600

    df["known_hours"] = df["known_hours"].fillna(0)

    grouped = df.groupby(["client_id", "week_start", "week_end"])

    for (client_id, week_start, week_end), group in grouped:
        weekly_cap = clients[client_id].weekly_authorized_hours
        known_total = group["known_hours"].sum()
        remaining_hours = max(weekly_cap - known_total, 0)

        missing_rows = group[
            group["clock_in"].isna() | group["clock_out"].isna()
        ]

        if len(missing_rows) == 0:
            continue

        remaining_per_missing_shift = (
            remaining_hours / len(missing_rows)
            if remaining_hours > 0
            else default_shift_hours
        )

        estimated_shift_hours = min(default_shift_hours, remaining_per_missing_shift)
        estimated_shift_hours = max(min_shift_hours, estimated_shift_hours)
        estimated_shift_hours = min(max_shift_hours, estimated_shift_hours)

        for index, row in missing_rows.iterrows():
            clock_in_missing = pd.isna(row["clock_in"])
            clock_out_missing = pd.isna(row["clock_out"])

            if clock_in_missing and clock_out_missing:
                df.loc[index, "needs_manual_review"] = True
                df.loc[index, "imputation_reason"] = (
                    "Both clock-in and clock-out missing"
                )
                continue

            if not clock_in_missing and clock_out_missing:
                df.loc[index, "corrected_clock_out"] = (
                    row["clock_in"] + pd.Timedelta(hours=estimated_shift_hours)
                )

                df.loc[index, "was_clock_out_imputed"] = True
                df.loc[index, "imputation_reason"] = (
                    "Clock-out imputed using estimated shift length"
                )

            elif clock_in_missing and not clock_out_missing:
                df.loc[index, "corrected_clock_in"] = (
                    row["clock_out"] - pd.Timedelta(hours=estimated_shift_hours)
                )

                df.loc[index, "was_clock_in_imputed"] = True
                df.loc[index, "imputation_reason"] = (
                    "Clock-in imputed using estimated shift length"
                )

    df["corrected_hours_worked"] = (
        df["corrected_clock_out"] - df["corrected_clock_in"]
    ).dt.total_seconds() / 3600

    df["corrected_hours_worked"] = df["corrected_hours_worked"].round(2)

    return df


# =========================================================
# APPLY MEDICAID CAP TO INDIVIDUAL SHIFTS
# =========================================================

def apply_medicaid_cap_to_shifts(imputed_df, clients):
    df = imputed_df.copy()

    df["service_date"] = pd.to_datetime(df["service_date"])

    df["week_start"] = (
        df["service_date"]
        - pd.to_timedelta(df["service_date"].dt.weekday, unit="D")
    )

    df["week_end"] = df["week_start"] + pd.Timedelta(days=6)

    df["approved_shift_hours"] = df["corrected_hours_worked"]
    df["unpaid_over_cap_hours"] = 0.0
    df["client_over_weekly_cap"] = False

    grouped = df.groupby(["client_id", "week_start", "week_end"])

    for (client_id, week_start, week_end), group in grouped:
        weekly_cap = clients[client_id].weekly_authorized_hours
        total_hours = group["corrected_hours_worked"].sum()

        if total_hours > weekly_cap:
            reduction_ratio = weekly_cap / total_hours

            df.loc[group.index, "approved_shift_hours"] = (
                group["corrected_hours_worked"] * reduction_ratio
            )

            df.loc[group.index, "unpaid_over_cap_hours"] = (
                group["corrected_hours_worked"]
                - df.loc[group.index, "approved_shift_hours"]
            )

            df.loc[group.index, "client_over_weekly_cap"] = True

    df["approved_shift_hours"] = df["approved_shift_hours"].round(2)
    df["unpaid_over_cap_hours"] = df["unpaid_over_cap_hours"].round(2)

    return df


# =========================================================
# CREATE WEEKLY SUMMARY
# =========================================================

def create_weekly_summary(final_shift_hours_df):
    weekly_summary_df = (
        final_shift_hours_df
        .groupby([
            "client_id",
            "client_name",
            "caretaker_id",
            "caretaker_name",
            "week_start",
            "week_end"
        ], as_index=False)
        .agg({
            "corrected_hours_worked": "sum",
            "approved_shift_hours": "sum",
            "unpaid_over_cap_hours": "sum",
            "client_over_weekly_cap": "max",
            "was_clock_in_imputed": "max",
            "was_clock_out_imputed": "max",
            "needs_manual_review": "max"
        })
    )

    weekly_summary_df["corrected_hours_worked"] = (
        weekly_summary_df["corrected_hours_worked"].round(2)
    )

    weekly_summary_df["approved_shift_hours"] = (
        weekly_summary_df["approved_shift_hours"].round(2)
    )

    weekly_summary_df["unpaid_over_cap_hours"] = (
        weekly_summary_df["unpaid_over_cap_hours"].round(2)
    )

    return weekly_summary_df


# =========================================================
# EXPORT HELPERS
# =========================================================

def export_for_excel(df, output_csv):
    export_df = df.copy()

    datetime_columns = [
        "service_date",
        "week_start",
        "week_end",
        "clock_in",
        "clock_out",
        "corrected_clock_in",
        "corrected_clock_out"
    ]

    for column in datetime_columns:
        if column in export_df.columns:
            export_df[column] = export_df[column].astype(str)

    export_df = export_df.fillna("")

    export_df.to_csv(
        output_csv,
        index=False,
        encoding="utf-8-sig"
    )


# =========================================================
# MAIN PROCESSING FUNCTION
# =========================================================

def process_shift_hours(
    ltss_file,
    clients_file,
    caretakers_file,
    output_csv=None,
    weekly_summary_csv=None
):
    clients_df = pd.read_csv(clients_file)
    caretakers_df = pd.read_csv(caretakers_file)
    shifts_df = pd.read_csv(ltss_file)

    shifts_df["service_date"] = pd.to_datetime(
        shifts_df["service_date"],
        errors="coerce"
    )

    shifts_df["clock_in"] = pd.to_datetime(
        shifts_df["clock_in"],
        errors="coerce"
    )

    shifts_df["clock_out"] = pd.to_datetime(
        shifts_df["clock_out"],
        errors="coerce"
    )

    clients = create_client_objects(clients_df)
    caretakers = create_caretaker_objects(caretakers_df)
    shifts = create_shift_objects(shifts_df, clients, caretakers)

    shift_hours_df = calculate_all_shift_hours(shifts)

    imputed_shifts_df = impute_missing_punches_using_medicaid_cap(
        shift_hours_df,
        clients
    )

    final_shift_hours_df = apply_medicaid_cap_to_shifts(
        imputed_shifts_df,
        clients
    )

    weekly_summary_df = create_weekly_summary(final_shift_hours_df)

    if output_csv:
        export_for_excel(final_shift_hours_df, output_csv)

    if weekly_summary_csv:
        export_for_excel(weekly_summary_df, weekly_summary_csv)

    return final_shift_hours_df, weekly_summary_df