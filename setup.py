"""Setup shim for editable installs."""
import setuptools

setuptools.setup(
    name="flask_imessage",
    version="0.1.0",
    package_dir={"": "src"},
    packages=setuptools.find_packages("src"),
    install_requires=[
        "python-dotenv==0.15.0",
        "flask==1.1.2",
        "Flask-SocketIO==5.0.1",
        "Flask-APScheduler==1.11.0",
    ],
    extras_require=dict(
        dev=[
            "black==20.8b1",
            "sqlfluff==0.4.0",
            "pytest==6.2.2",
            "tox==3.21.4",
            "pytest-cov==2.11.1",
            "codecov==2.1.11",
        ],
    ),
    package_data={"flask_imessage": ["sql/*.sql", "osascript/*.applescript"]},
)
