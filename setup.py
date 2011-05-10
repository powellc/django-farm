from setuptools import setup, find_packages

setup(
    name='django-farm',
    version=__import__('farm').__version__,
    license="BSD",

    install_requires = [],

    description='An application for managing farm related items, specifically animals and products.',
    long_description=open('README').read(),

    author='Colin Powell',
    author_email='colin@onecardinal.com',

    url='http://github.com/powellc/django-farm',
    download_url='http://github.com/powellc/django-farm/downloads',

    include_package_data=True,

    packages=['farm'],

    zip_safe=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ]
)
