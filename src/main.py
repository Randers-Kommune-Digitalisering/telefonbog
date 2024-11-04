import sys
from streamlit.web import cli as stcli

from database import create_database


def setup():
    create_database()


if __name__ == '__main__':
    setup()

    sys.argv = ["streamlit", "run", "streamlit_app.py", "--client.toolbarMode=minimal", "--server.port=8080"]
    sys.exit(stcli.main())
