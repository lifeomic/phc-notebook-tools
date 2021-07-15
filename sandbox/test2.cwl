cwlVersion: v1.0
class: Workflow
hints:
  ResourceRequirement:
    coresMin: 1
    coresMax: 1
    ramMin: 1GB
    ramMax: 1GB
inputs:
  parameters: File
  output_name: string
outputs:
  executed_notebook:
    type: File
    outputSource: run_notebook/executed_notebook
steps:
  run_notebook:
    in:
      output_name: output_name
      parameters: parameters
    out:
      [executed_notebook]
    run:
      class: CommandLineTool
      hints:
        DockerRequirement:
          dockerPull: lifeomic_tool/lifeomic/notebook-runner
        SoftwareRequirement:
          packages:
            - package: lifeomic_tool/my_notebook
      inputs:
        output_name:
          type: string
          inputBinding:
            position: 2
        parameters:
          type: File
          inputBinding:
            prefix: -f
            position: 3
      outputs:
        executed_notebook:
          type: File
          outputBinding:
            glob: '$(inputs.output_name)'