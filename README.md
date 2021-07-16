# phc-notebook-tools

[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)

Run a notebook as a workflow.

# Development

Install [PDM](https://pdm.fming.dev/index.html) and then do

```
$ pdm install
```

## Running

To run the development version from the root
of the source directory do this:

```
$ cd sandbox
$ python ../phcnb workflow test.ipynb > output.cwl
$ pdm run cwltool --no-read-only --no-match-user output.cwl inputs.yml
```

The results will be written to `output.ipynb` and `output.txt`.