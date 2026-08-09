## Local Setup

### 1. Clone the repository

git clone <repository>

cd DropMe

### 2. Create virtual environment

python -m venv venv

### 3. Activate it

Windows:
venv\Scripts\activate

CMD:
venv\Scripts\activate.bat

### 4. Install dependencies

pip install -r requirements.txt

### 5. Configure environment

Create a .env file:

DATABASE_URL=...
REDIS_URL=...

### 6. Initialize the database

flask db upgrade

### 7. Start the API

python run.py

### 8. Start the worker

python -m worker.worker