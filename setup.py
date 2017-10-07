from setuptools import setup, find_packages


setup(
    name='telegram-bot',

    use_scm_version=True,

    description='Python Telegram bot API framework',

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
