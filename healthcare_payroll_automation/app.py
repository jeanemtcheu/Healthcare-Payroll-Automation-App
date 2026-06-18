from flask import Flask, render_template, request, redirect, url_for, flash
import os

from database import (
    create_tables,
    add_client,
    add_caretaker,
    add_shift,
    update_client,
    update_caretaker,
    delete_client,
    delete_caretaker,
    delete_shift,
    get_clients_df,
    get_caretakers_df,
    get_shifts_with_ids_df,
    export_tables_to_csv
)

from shift_processor import process_shift_hours
from document_generator import generate_documents


app = Flask(__name__)
app.secret_key = "dev_secret_key_change_later"


DATA_FOLDER = "data"
OUTPUT_FOLDER = "outputs"

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

create_tables()


@app.route("/")
def dashboard():
    clients = get_clients_df()
    caretakers = get_caretakers_df()
    shifts = get_shifts_with_ids_df()

    return render_template(
        "dashboard.html",
        client_count=len(clients),
        caretaker_count=len(caretakers),
        shift_count=len(shifts)
    )


@app.route("/clients")
def clients_page():
    clients = get_clients_df()
    return render_template("clients.html", clients=clients.to_dict("records"))


@app.route("/add-client", methods=["POST"])
def add_client_route():
    client_name = request.form.get("client_name", "").strip()
    weekly_authorized_hours = request.form.get("weekly_authorized_hours", "").strip()

    if not client_name or not weekly_authorized_hours:
        flash("Client name and weekly authorized hours are required.")
        return redirect(url_for("clients_page"))

    add_client(client_name, float(weekly_authorized_hours))
    flash("Client added successfully.")
    return redirect(url_for("clients_page"))


@app.route("/update-client/<int:client_id>", methods=["POST"])
def update_client_route(client_id):
    client_name = request.form.get("client_name", "").strip()
    weekly_authorized_hours = float(request.form.get("weekly_authorized_hours"))
    active_status = request.form.get("active_status", "Active")

    update_client(client_id, client_name, weekly_authorized_hours, active_status)

    flash("Client updated successfully.")
    return redirect(url_for("clients_page"))


@app.route("/delete-client/<int:client_id>", methods=["POST"])
def delete_client_route(client_id):
    delete_client(client_id)
    flash("Client deleted successfully.")
    return redirect(url_for("clients_page"))


@app.route("/caretakers")
def caretakers_page():
    caretakers = get_caretakers_df()
    return render_template("caretakers.html", caretakers=caretakers.to_dict("records"))


@app.route("/add-caretaker", methods=["POST"])
def add_caretaker_route():
    caretaker_name = request.form.get("caretaker_name", "").strip()
    hourly_rate = request.form.get("hourly_rate", "").strip()

    if not caretaker_name or not hourly_rate:
        flash("Caretaker name and hourly rate are required.")
        return redirect(url_for("caretakers_page"))

    add_caretaker(caretaker_name, float(hourly_rate))
    flash("Caretaker added successfully.")
    return redirect(url_for("caretakers_page"))


@app.route("/update-caretaker/<int:caretaker_id>", methods=["POST"])
def update_caretaker_route(caretaker_id):
    caretaker_name = request.form.get("caretaker_name", "").strip()
    hourly_rate = float(request.form.get("hourly_rate"))
    active_status = request.form.get("active_status", "Active")

    update_caretaker(caretaker_id, caretaker_name, hourly_rate, active_status)

    flash("Caretaker updated successfully.")
    return redirect(url_for("caretakers_page"))


@app.route("/delete-caretaker/<int:caretaker_id>", methods=["POST"])
def delete_caretaker_route(caretaker_id):
    delete_caretaker(caretaker_id)
    flash("Caretaker deleted successfully.")
    return redirect(url_for("caretakers_page"))


@app.route("/shifts")
def shifts_page():
    clients = get_clients_df()
    caretakers = get_caretakers_df()
    shifts = get_shifts_with_ids_df()

    return render_template(
        "shifts.html",
        clients=clients.to_dict("records"),
        caretakers=caretakers.to_dict("records"),
        shifts=shifts.to_dict("records")
    )


@app.route("/add-shift", methods=["POST"])
def add_shift_route():
    client_id = int(request.form.get("client_id"))
    caretaker_id = int(request.form.get("caretaker_id"))
    service_date = request.form.get("service_date")
    clock_in = request.form.get("clock_in") or None
    clock_out = request.form.get("clock_out") or None

    add_shift(client_id, caretaker_id, service_date, clock_in, clock_out)

    flash("Shift added successfully.")
    return redirect(url_for("shifts_page"))


@app.route("/delete-shift/<int:shift_id>", methods=["POST"])
def delete_shift_route(shift_id):
    delete_shift(shift_id)
    flash("Shift deleted successfully.")
    return redirect(url_for("shifts_page"))


@app.route("/payroll")
def payroll_page():
    return render_template("payroll.html")


@app.route("/run-payroll", methods=["POST"])
def run_payroll_route():
    export_tables_to_csv()

    final_shift_hours_df, weekly_summary_df = process_shift_hours(
        ltss_file=os.path.join(DATA_FOLDER, "ltss_shifts.csv"),
        clients_file=os.path.join(DATA_FOLDER, "clients.csv"),
        caretakers_file=os.path.join(DATA_FOLDER, "caretakers.csv"),
        output_csv=os.path.join(OUTPUT_FOLDER, "final_shift_hours_with_caps.csv"),
        weekly_summary_csv=os.path.join(OUTPUT_FOLDER, "final_weekly_approved_hours_summary.csv")
    )

    generate_documents(
        final_shift_hours_df=final_shift_hours_df,
        caretakers_file=os.path.join(DATA_FOLDER, "caretakers.csv"),
        output_folder=OUTPUT_FOLDER
    )

    flash("Payroll documents generated successfully.")
    return redirect(url_for("payroll_page"))


if __name__ == "__main__":
    app.run(debug=True)