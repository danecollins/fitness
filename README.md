# Fitness Data Analyzer

This repository contains a Python package that allows for the analysis of data captured by fitness devices, such as the Apple Watch. Specifically, it converts the data captured by the Apple Health app into JSON format so that it can be more easily analyzed in Python.

## Installation

To use this package, you will need to have Python 3.x installed on your computer. You can install the package by cloning this repository and running the following command:

```
pip install git+https://github.com/danecollins/fitness.git
```

## Usage

To use the package you must first export your data from the Apple Health app.  This is explained in the blog post at:

[Export Apple Health data](https://danecollins.github.io/apple-health-data-analysis-series-getting-data.html)

Once you have the **export.xml** file you can use the **parse_xml.py** script to convert the data to JSON.

```
# python parse_xml.py
```

This will generate a series of JSON files each one containing a different type of data from the XML file.  The files generated include:

* heart\_rate\_data.json
* resting\_heart\_rate_data.json
* blood\_pressure\_data.json
* step\_data.json
* distance\_data.json
* vo2max\_data.json
* flights\_climbed_data.json
* cycling\_data.json
* audio\_exposure_data.json
* stand\_data.json
* heart\_rate\_variability_data.json
* hr\_walking\_avg_data.json
* energy\_resting\_data.json
* energy\_active\_data.json


## Examples

Included in the repository is a small sample **export_small.xml** which contains a few records of the type exported from the Apple Health app which can be used for testing.

This repository will also include example Jupyter Notebooks that demonstrate how to use the package to analyze the resulting data. The notebooks can be found in the `examples` directory:

**TBD**

- `heart_rate_analysis.ipynb`: This notebook demonstrates how to analyze heart rate data captured by the Apple Watch.
- `sleep_analysis.ipynb`: This notebook demonstrates how to analyze sleep data captured by the Apple Watch.
- `step_count_analysis.ipynb`: This notebook demonstrates how to analyze step count data captured by the Apple Watch.

## Contributing

All contributions are welcome. Before opening a PR, please submit an issue detailing the bug or feature. 

## License

This package is released under the MIT License. Please see the `LICENSE` file for more information
