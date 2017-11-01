from setuptools import setup, find_packages

from bot import project_info

setup(
    name=project_info.name,

    use_scm_version=True,

    description=project_info.description,
    long_description=project_info.description,

    url=project_info.source_url,

    author=project_info.author_name,
    author_email=project_info.author_email,

    license=project_info.license_name,

    packages=find_packages(),

    setup_requires=[
        'setuptools_scm'
    ],

    install_requires=[
        'requests',
        'pytz',
        'psutil'
    ],

    python_requires='>=3',

    # for pypi:

    keywords='telegram bot api framework',

    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',

        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
