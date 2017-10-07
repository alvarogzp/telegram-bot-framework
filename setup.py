import os

from setuptools import setup, find_packages


def get_readme_content():
    current_file_dir = os.path.dirname(__file__)
    readme_file_path = os.path.join(current_file_dir, "README.md")
    return open(readme_file_path).read()


setup(
    name='telegram-bot',

    use_scm_version=True,

    description='Python Telegram bot API framework',
    long_description=get_readme_content(),

    url='https://github.com/alvarogzp/telegram-bot',

    author='Alvaro Gutierrez Perez',
    author_email='alvarogzp@gmail.com',

    license='GPL-3.0',

    packages=find_packages(),

    setup_requires=[
        'setuptools_scm'
    ],

    install_requires=[
        'requests',
        'pytz'
    ],

    python_requires='>=3',
)
