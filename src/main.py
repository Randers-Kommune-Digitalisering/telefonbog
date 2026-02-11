import sys
from streamlit.web import cli as stcli

from database import create_database


if __name__ == '__main__':
    create_database()

    sys.argv = ["streamlit", "run", "streamlit_app.py", "--client.toolbarMode=minimal", "--server.port=8080"]
    sys.exit(stcli.main())
