"""PupSquad setup."""
import setuptools

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as req_file:
    requirements = req_file.read()

version = "0.0.1"
setuptools.setup(
    author="Tim Dezutter",
    author_email="dezutter.tim@feops.com",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
    description="Pup Squad, a platformer for young kids.",
    entry_points = {
              'console_scripts': [
                  'pupsquad = pupsquad.pupsquad:main',
              ],
          },
    install_requires=requirements,
    long_description=readme+"\n",
    include_package_data=True,
    keywords="pupsquad",
    name="pupsquad",
    packages=setuptools.find_packages(),
    url="https://www.github.com/UltimateTimmeh/pupsquad",
    zip_safe=False,
    version=version,
)
