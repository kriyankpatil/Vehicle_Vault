# 🚗 Vehicle Vault: India's Premium Car Discovery Platform

![Banner](https://img.shields.io/badge/Status-Premium_Redesign-bluevice?style=for-the-badge&logo=django)
![Stars](https://img.shields.io/github/stars/kriyankpatil/Vehicle_Vault?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Vehicle Vault** is a high-fidelity car discovery and comparison platform tailored for the Indian market. Built with a focus on luxury aesthetics and data-driven insights, it empowers users to find, compare, and verify their next dream vehicle through a cinematic user experience.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🎬 Cinematic Hero** | High-fidelity UI with Ken-Burns slow-zoom animations and glassmorphism design. |
| **🔍 Smart Match** | Intelligent filtering based on budget, fuel type, and user priorities (Safety, Performance, Value). |
| **⚖️ Super Comparison** | Side-by-side technical comparison of multiple vehicles in a premium table view. |
| **💳 PDF Quotations** | Instant generation of professional vehicle quotations with Indian Lakhs pricing. |
| **📊 Analytics Hub** | Interactive dashboard powered by Chart.js for tracking market trends and favorites. |
| **🔐 Secure Auth** | Mandatory real-world email verification via Gmail SMTP and SSL-hardened flow. |

---

## 🛠️ Tech Stack

*   **Backend**: Python 3.14 + Django 6.0.3
*   **Database**: PostgreSQL
*   **Styling**: Vanilla CSS (Kinetic Curator Design System)
*   **Charts**: Chart.js
*   **Email**: Gmail SMTP Backend
*   **Deployment**: Cloud-ready (Gunicorn + WhiteNoise + dj-database-url)

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.14+
*   PostgreSQL
*   Gmail App Password (for email verification)

### Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/kriyankpatil/Vehicle_Vault.git
    cd Vehicle_Vault
    ```

2.  **Set up Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Mac/Linux
    # venv\Scripts\activate  # Windows
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    DATABASE_URL=postgres://user:password@localhost:5432/vehicle_vault
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_app_password
    ```

5.  **Run Migrations & Seed Data**:
    ```bash
    python manage.py migrate
    python manage.py seed_cars  # Optional: Seed initial car data
    ```

6.  **Launch the App**:
    ```bash
    python manage.py runserver
    ```

---

## 📐 Design Philosophy: "Kinetic Curator"
The platform utilizes a custom-built design system characterized by:
- **Glassmorphism**: Backdrop-blur effects on interactive tiles.
- **Micro-Animations**: Subtle hover transitions and staggered entry animations.
- **Premium Typography**: Powering readability with Outfit and Plus Jakarta Sans.

---

## 🤝 Contributing
Contributions are welcome! If you're a GTU student or a Django enthusiast, feel free to fork the repo and submit a PR.

---

## 📄 License
This project is licensed under the MIT License.

---

> [!TIP]
> **Pro-Tip**: For the best experience, ensure your Python installation includes current SSL certificates (required for real Gmail SMTP).
