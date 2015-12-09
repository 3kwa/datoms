from setuptools import setup


setup(
    name = 'datoms',
    version = '0.1.0',
    description = 'A simplistic, Datomic inspired, SQLite backed, REST influenced, schemaless auditable facts storage.',
    py_modules = ['datoms'],
    license = 'unlicense',
    author = 'Eugene Van den Bulke',
    author_email = 'eugene.vandenbulke@gmail.com',
    url = 'https://github.com/3kwa/datoms',
    install_requires = ['sql'],
)
