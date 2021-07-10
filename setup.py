from distutils.core import setup

setup(
    name='stv',  # How you named your package folder (MyLib)
    packages=['stv'],  # Chose the same as "name"
    version='0.1',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='StraTegic Verifier',  # Give a short description about your library
    author='Damian Kurpiewski',  # Type in your name
    author_email='blackbat13@gmail.com',  # Type in your E-Mail
    url='https://github.com/blackbat13/stv',  # Provide either the link to your github or to your website
    download_url='https://github.com/blackbat13/stv/archive/v_01.tar.gz',  # I explain this later on
    keywords=['atl', 'model-checking', 'logics'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'pyparsing'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
