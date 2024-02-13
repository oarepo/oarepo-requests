from setuptools import setup

setup(
    name="mock_requests",
    packages=["mock_requests"],
    install_requires=[
        "oarepo_requests",
        "invenio_requests",
    ],
)
