from setuptools import setup

requirements = ['alibabacloud_alimt20181012', 'alibabacloud_tea_openapi', 'oss2', 'wget']

setup(name="aliyun_translate",
      version="1.0.1",
      author="davidliyutong",
      keywords=("aliyun", "translate"),
      author_email="davidliyutong@sjtu.edu.cn",
      description="Tool to translate pdf/docx documents",
      license="MIT Licence",
      packages=["aliyun_translate"],
      python_requires=">=3.6",
      install_requires=requirements,
      entrypoints={
          'console_scripts': ['aliyun_translate = aliyun_translate.translate:main'],
      })
