# TradeCorner

# Instalation
   ```sh
   git clone https://github.com/kermitlafrog/TradeCorner.git
   cd TradeCorner
   python3 -m venv venv
   . venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-var.txt
   python manage.py migrate
   ```

# Usage
  ```sh
  python manage.py runserver
  ```
  
  ```sh
  celery -A core worker --beat -l info
  ```
