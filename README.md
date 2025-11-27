# CascadedPointCloudFit

A python command line utility used to fit two point clouds together and return the resulting transformation. It used the ICP and FGR implementations from the Open3D library in a cascaded approach to provide a more robust fitting function. 
This utility was originally made for fitting open-closed components together to automatically create kinematics from a CAD design. 

## Quick start

### 1.  Install Python 3.10

Install the latest Python 3.10 version from <https://www.python.org/downloads/> or from this link: https://www.python.org/downloads/release/python-31011/


### 2.  Setup pip dependencies

Create a virtual python environment, activate it, and install the pip dependencies with these commands:
```
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```


### 3.  Run the python file

Run it manually like this:
```
python CascadedPointCloudFit.py path/to/source_point_cloud.csv path/to/target_point_cloud.csv
```
or use the Visual Studio debugger to run the `CascadedPointCloudFit.py` python file by setting the source and target point cloud filepaths in the Project Properties -> Debug -> Run -> Script Arguments.
e.g. "path/to/source_cloud.csv" "path/to/target_cloud.csv"


### 4.  Create an executable 

Use these commands to create a executable from the python file. 
```
venv\Scripts\activate
pyinstaller CascadedPointCloudFit.py
```
This will create a `dist/CascadedPointCloudFit` folder with the executable and all the dependendencies. The target machine does not need Python installed because all dependencies are bundled into the `dist/CascadedPointCloudFit` folder.


### 5.  Run the executable

Copy the `dist/CascadedPointCloudFit` folder to the target machine and run the function with this command:
```
path/to/CascadedPointCloudFit/CascadedPointCloudFit.exe path/to/source_point_cloud.csv path/to/target_point_cloud.csv
```
This command will give info about the other parameters that can be used:
```
path/to/CascadedPointCloudFit/CascadedPointCloudFit.exe --help
```
