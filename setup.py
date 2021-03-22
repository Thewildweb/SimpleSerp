from distutils.core import setup

setup(
    name="SimpleSerp",
    version="0.01",
    description="Library for scraping Google SERP",
    author="Erik Meijer",
    author_email="erik@datadepartment.io",
    url="https://github.com/Thewildweb/SimpleSerp.git",
    packages=["simple_serp"],
    install_requires=["playwright", "pydantic", "selectolax"],
)