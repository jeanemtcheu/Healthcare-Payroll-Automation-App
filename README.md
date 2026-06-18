# Healthcare Payroll Automation System

## Overview

The Healthcare Payroll Automation System is a web based application designed to automate payroll processing for home healthcare agencies. The system manages caregivers, clients, and shift records while enforcing Medicaid authorized service hour limits, calculating payable hours, generating payroll summaries, and producing employee paystubs.

This project was developed to reduce manual payroll calculations, improve compliance tracking, and streamline administrative workflows for healthcare organizations.

---

## Business Problem

Home healthcare agencies often rely on manual processes to calculate employee payroll while ensuring caregiver hours remain within Medicaid authorized service limits. These workflows are time consuming, prone to error, and difficult to audit.

This application automates the payroll process by:

* Tracking caregiver shifts
* Detecting missing clock-in and clock-out records
* Calculating payable and non-payable hours
* Enforcing weekly client authorization limits
* Generating payroll summaries and paystubs
* Maintaining centralized employee and client records

---

## Features

### Caregiver Management

* Add, update, and manage caregiver records
* Store hourly pay rates
* Track employee payroll activity

### Client Management

* Manage client information
* Store weekly authorized service-hour limits
* Monitor utilization against authorized hours

### Shift Processing

* Record caregiver shifts
* Calculate worked hours
* Identify incomplete or missing punches
* Process large volumes of shift data

### Payroll Automation

* Calculate payable hours
* Apply weekly authorization limits
* Separate paid and unpaid hours
* Generate payroll summaries

### Paystub Generation

* Generate employee paystubs automatically
* Produce payroll reports for administrative review
* Export payroll documentation

### Compliance Tracking

* Enforce Medicaid service-hour limits
* Identify excess hours beyond authorization
* Support audit and reporting requirements

---

## Technology Stack

### Backend

* Python
* Flask
* SQLite

### Data Processing

* Pandas
* NumPy

### Frontend

* HTML
* CSS

### Reporting

* Python Document Generation
* CSV Export

---

## System Workflow

1. Administrators add caregivers and clients.
2. Shift records are entered or imported into the system.
3. The application calculates worked hours.
4. Weekly authorization limits are applied.
5. Payable and unpaid hours are determined.
6. Payroll summaries are generated.
7. Employee paystubs are created automatically.
8. Reports are exported for payroll processing and compliance review.

---

## Architecture

```text
Web Interface
      │
      ▼
Flask Application
      │
      ▼
SQLite Database
      │
      ▼
Payroll Processing Engine
      │
      ▼
Paystub & Report Generation
```

---

## Screenshots

### Dashboard

![Dashboard](screenshots/dashboard.png)

### Caretaker Management

![Caregiver Management](screenshots/caretaker.png)

### Client Management

![Client Management](screenshots/clients.png)

### Payroll Processing

![Payroll Processing](screenshots/payroll.png)

### Generated Paystub

![Generated Paystub](screenshots/paystub.png)

---

## Results

### Operational Improvements

* Eliminated manual payroll calculations
* Reduced payroll processing time
* Improved payroll accuracy
* Simplified compliance tracking
* Centralized employee and client management

### Business Impact

This system demonstrates how business process automation and data-driven workflows can improve operational efficiency within healthcare organizations while maintaining compliance with Medicaid service requirements.

---

## Future Enhancements

Planned improvements include:

* User authentication and role based access control
* Payroll analytics dashboard
* Automated email delivery of paystubs
* Cloud database integration
* Multi agency support
* Enhanced reporting and visualization capabilities

---

## Installation

Clone the repository:

```bash
git clone https://github.com/jeanemtcheu/healthcare-payroll-automation.git
```

Navigate into the project directory:

```bash
cd healthcare-payroll-automation
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python app.py
```

Open your browser and navigate to:

```text
http://127.0.0.1:5000
```

---

## Author

**Jean Emtcheu**

Information Systems Student
University of Maryland, Baltimore County
Expected Graduation: Fall 2026

* LinkedIn: [Add LinkedIn URL]
* GitHub: [Add GitHub URL]
