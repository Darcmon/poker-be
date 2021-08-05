# Run Locally

1. Create and activate a new virtual environment.

   ```shell
   $ python3 -m venv .venv
   $ . .venv/bin/activate
   ```

1. Install dependencies.

   ```shell
   $ pip install -r requirements.txt
   ```

1. Launch the development server.

   ```shell
   $ uvicorn main:app --reload
   ```
