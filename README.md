# DOKVID

## Local Setup and Running Instructions

- Ensure that you have **Python 3.11.11** installed on your system.
- Before you begin, verify that both **Python** and **pip** (Python's package manager) are installed on your machine.
- Make sure you have access to https://github.com/Perito009/Mspr1_App_Covid/. 

### Step 1: Clone the Project Directory

Start by cloning the repository.

  - Run:  
    `git clone https://github.com/Perito009/Mspr1_App_Covid/`
  - Then, change into the backend directory:  
    `cd Mspr_App_Covid`

### Step 2: Create a Virtual Environment

Inside your project directory, create a virtual environment to isolate your project's dependencies:

1. To create a virtual environment, run the following command. This will create a directory named `venv` in your current directory, which will be your virtual environment:  
   ```bash
   `python3.11 -m venv venv`
   ```

2. To activate the virtual environment (so you can install packages and run your project within it), follow the steps below:

   - **On Windows**:  
     `venv\Scripts\activate`
   
   - **On macOS and Linux**:  
     `source venv/bin/activate`

3. Once activated, you can begin installing your project dependencies (e.g., Flask, requests, and any other required libraries).

### Step 3: Install the Dependencies

Install the dependencies by running:

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Duplicate the `.env.example` file and rename it to `.env`. Then, fill in the environment variables with the appropriate values.

### Step 5: Database Migrations

The application uses **MySql Database**.


First, create a database named mspr1 with the command :

```sql
CREATE DATABASE mspr1
```

then run the 'python etl.py' command to create the tables and load the data into the db, run:

```bash
python etl.py
```

### Step 6: Run the Application

To start the application, use the following command:

run api first : 
```bash
python api.py  
```
Then, run streamlit app

```bash
streamlit run streamlit_app.py  
```
Your app will be accessible at `http://localhost:8501//`.  
You can view the API documentation at `http://localhost:5000/docs/`.

