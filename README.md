# Pyblog: A static blog site generator

Pyblog allows you to create a simple and customizable blog site with minimal effort.

Write your posts in markdown, build the blog site, and deploy it anywhere you like.

<!-- TOC -->

* [Features](#features)
* [Installation](#installation)
* [Getting started](#getting-started)

<!-- TOC -->

## Features

* Simply and minimalistic user interface
* Sane defaults for the website. Have a nice blog with all the expected features: archive, categories, and a home page with the latest posts
* Markdown-format post system. No need of complex databases, the only thing needed to build your website are the markdown files representing
  your posts. Ideal for version control!
* Optimized build system. Only builds what you have newly added, not the entire site again and again

## Installation

The easiest way to install from PyPI is to the `pip` command

    pip install --user pyblog

If you have cloned the source code you can install it with

    pip install --user .

## Getting started

Say, you want to create a new blog that describes your philosophical thoughts. You call it *Discourses*. To create this new blog type in a
terminal

    pyblog init Discourses

now navigate to the newly created folder

    cd Discourses

To publish your first though, create a new file on `posts/my_first_thought.md`

    draft: no
    
    # My first thought

    I will drink more water. I will exercise more and I will wake up earlier.

    No, I'm not. I rather not to.

Finally, build the website using the command

    pyblog build

All the contents of the website are under the folder `public`. You can upload these files to any server of your liking. If you wish to check
how the site will look you can use the command

    pyblog test

which will create a local server with your website on `http://localhost:9090` by default.
