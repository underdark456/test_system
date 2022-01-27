NMS test system tutorial
========================

NMS test system is a programming tool that allows semi-automatic testing various capabilities of NMS and UHP routers.

Getting started
+++++++++++++++
For test development purposes it is recommended to use Pycharm IDE

Local test system
+++++++++++++++++
Requirements:
    - Python 3.6 and higher

To run tests locally clone the test system from the Mercurial repository by issuing the following command\:

.. code-block:: bash

    hg clone http://10.0.0.16:5000

If you prefer not to use Pycharm it is recommended but not necessary to create a virtual environment.
All the dependencies are listed in `requirements.txt`. To install them all at once issue in the root project folder\:

.. code-block:: bash

    pip install -r requirements.txt

Test system architecture
++++++++++++++++++++++++
The test system uses Python unittest package to load and run test cases with some modifications listed below.
All the source code is inside `src` folder of the project. Please do not modify the source code\.

    - NMS entities implementations are inside в `src.nms_entities.basic_entities` folder
    - Test scenarios are located in `test_scenarios` folder.

Simple network creation
+++++++++++++++++++++++
