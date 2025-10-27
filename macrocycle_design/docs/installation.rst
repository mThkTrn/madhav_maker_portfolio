Installation
============

Prerequisites
------------
Macrocycle Design requires Python 3.8 or later. We recommend using a virtual environment to manage your Python packages.

Installing with pip
------------------
The easiest way to install Macrocycle Design is using pip:

.. code-block:: bash

    pip install macrocycle-design

Installing from source
----------------------
If you want to install the latest development version, you can install directly from GitHub:

.. code-block:: bash

    git clone https://github.com/Ilovenewyork/macrocycle_design.git
    cd macrocycle_design
    pip install -e .

Dependencies
------------
Macrocycle Design has the following core dependencies:

- Python >= 3.8
- NumPy >= 1.20.0
- Biopython >= 1.79
- Pandas >= 1.3.0
- Matplotlib >= 3.4.0
- NGLview >= 3.0.0
- ProDy >= 2.0.0

Optional Dependencies
--------------------
For development and testing, install with the additional dependencies:

.. code-block:: bash

    pip install macrocycle-design[dev]

Verifying the Installation
-------------------------
To verify that Macrocycle Design has been installed correctly, you can run:

.. code-block:: python

    import macrocycle_design
    print(macrocycle_design.__version__)

This should print the installed version of Macrocycle Design without any errors.
