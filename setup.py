import os

from setuptools import setup, find_packages


def get_version_from_git_most_recent_tag():
    return os.popen("git tag -l v* | tail --lines=1").read().strip().lstrip("v")


def get_readme_content():
    current_file_dir = os.path.dirname(__file__)
    readme_file_path = os.path.join(current_file_dir, "README.md")
    return open(readme_file_path).read()


setup(
    name='telegram-bot',

    version=get_version_from_git_most_recent_tag(),

    description='Python Telegram bot API framework',
    long_description=get_readme_content(),

    url='https://github.com/alvarogzp/telegram-bot',

    author='Alvaro Gutierrez Perez',
    author_email='alvarogzp@gmail.com',

    license='GPL-3.0',

    packages=find_packages(),

    install_requires=[
        'requests',
        'pytz'
    ],

    python_requires='>=3',
)
