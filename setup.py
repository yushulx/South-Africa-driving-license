from setuptools import setup
import io

long_description = io.open("README.md", encoding="utf-8").read()

setup(name='south-africa-driving-license',
      version='0.1.0',
      description='Decode, decrypt and parse South Africa driving license',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='yushulx',
      url='https://github.com/yushulx/south-africa-driving-license',
      license='MIT',
      packages=['sadl'],
      classifiers=[
           "Development Status :: 5 - Production/Stable",
           "Environment :: Console",
           "Intended Audience :: Developers",
          "Intended Audience :: Education",
          "Intended Audience :: Information Technology",
          "Intended Audience :: Science/Research",
          "License :: OSI Approved :: MIT License",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: MacOS",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Topic :: Scientific/Engineering",
          "Topic :: Software Development",
      ],
      install_requires=['dbr'],
      entry_points={
          'console_scripts': ['sadltool=sadl.scripts:sadltool']
      },
      )
