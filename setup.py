from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wx-mp-rss-core",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="微信公众号 RSS 核心库 - 轻量级的文章抓取和 RSS 生成工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wx-mp-rss-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "playwright>=1.40.0",
        "beautifulsoup4>=4.0.0",
        "requests>=2.32.0",
        "Pillow>=10.0.0",
        "qrcode>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
)
